import CryptoKit
import Foundation
import UIKit
import UniformTypeIdentifiers

/// First-party synthetic foreign recipient. It hashes actual input bytes
/// received via NSItemProvider, never stores or prints the document body.
final class ShareViewController: UIViewController {
    private static let maxBytes = 2 * 1_024 * 1_024
    private let statusLabel = UILabel()
    private let kindLabel = UILabel()
    private let countLabel = UILabel()
    private let hashLabel = UILabel()
    private let detailLabel = UILabel()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        let heading = UILabel()
        heading.text = "AYA synthetic receiver"
        heading.font = .preferredFont(forTextStyle: .headline)
        heading.adjustsFontForContentSizeCategory = true
        let done = UIButton(type: .system)
        done.setTitle("Done", for: .normal)
        done.accessibilityIdentifier = "qa.receiver.done"
        done.addTarget(self, action: #selector(dismissReceipt), for: .touchUpInside)
        done.heightAnchor.constraint(greaterThanOrEqualToConstant: 44).isActive = true

        let stack = UIStackView(arrangedSubviews: [
            heading, statusLabel, kindLabel, countLabel, hashLabel, detailLabel, done
        ])
        stack.axis = .vertical
        stack.spacing = 14
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -20),
            stack.topAnchor.constraint(greaterThanOrEqualTo: view.safeAreaLayoutGuide.topAnchor, constant: 24),
            stack.centerYAnchor.constraint(equalTo: view.safeAreaLayoutGuide.centerYAnchor)
        ])
        for (label, id) in [
            (statusLabel, "qa.receiver.status"),
            (kindLabel, "qa.receiver.kind"),
            (countLabel, "qa.receiver.bytes"),
            (hashLabel, "qa.receiver.sha256"),
            (detailLabel, "qa.receiver.detail")
        ] {
            label.font = .preferredFont(forTextStyle: .body)
            label.adjustsFontForContentSizeCategory = true
            label.numberOfLines = 0
            label.lineBreakMode = .byCharWrapping
            label.accessibilityIdentifier = id
        }
        show(status: "loading", kind: "unknown", bytes: 0, digest: "", detail: "Waiting for item provider")
        receiveItem()
    }

    @objc private func dismissReceipt() {
        extensionContext?.completeRequest(returningItems: [], completionHandler: nil)
    }

    private func receiveItem() {
        let providers = (extensionContext?.inputItems as? [NSExtensionItem] ?? [])
            .flatMap { $0.attachments ?? [] }
        guard providers.count == 1, let provider = providers.first else {
            show(status: "invalid_items", detail: "Require exactly one explicit shared item")
            return
        }
        // File URLs advertise public.file-url; a string-based share normally
        // offers public.plain-text/public.text. Never infer source AI identity.
        if provider.hasItemConformingToTypeIdentifier(UTType.fileURL.identifier) {
            guard let type = provider.registeredTypeIdentifiers.first(where: {
                UTType($0)?.conforms(to: .text) == true
            }) else {
                show(status: "unsupported_file", detail: "No text file representation offered")
                return
            }
            provider.loadFileRepresentation(forTypeIdentifier: type) { [weak self] url, error in
                // Apple owns the temporary file and may delete it as soon as
                // this callback exits, so hash the bytes before returning.
                guard let self else { return }
                if let error { self.show(status: "file_error", detail: String(describing: Swift.type(of: error))); return }
                guard let url else { self.show(status: "missing_file"); return }
                self.receiveFile(url, kind: "file")
            }
        } else if provider.hasItemConformingToTypeIdentifier(UTType.plainText.identifier) {
            provider.loadItem(forTypeIdentifier: UTType.plainText.identifier, options: nil) { [weak self] item, error in
                guard let self else { return }
                if let error { self.show(status: "text_error", detail: String(describing: Swift.type(of: error))); return }
                if let text = item as? String {
                    self.receive(Data(text.utf8), kind: "text")
                } else if let data = item as? Data {
                    self.receive(data, kind: "text")
                } else {
                    self.show(status: "unsupported_text", detail: "Received unexpected text representation")
                }
            }
        } else {
            show(status: "unsupported_type", detail: "No advertised plain-text or file URL representation")
        }
    }

    private func receiveFile(_ url: URL, kind: String) {
        do {
            let handle = try FileHandle(forReadingFrom: url)
            defer { try? handle.close() }
            let data = try handle.read(upToCount: Self.maxBytes + 1) ?? Data()
            receive(data, kind: kind)
        } catch {
            show(status: "read_error", detail: String(describing: Swift.type(of: error)))
        }
    }

    private func receive(_ data: Data, kind: String) {
        guard data.count <= Self.maxBytes else {
            show(status: "too_large", kind: kind, detail: "Input exceeds the 2 MiB synthetic test bound")
            return
        }
        let digest = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        show(status: "received", kind: kind, bytes: data.count, digest: digest,
             detail: "Digest computed within the independent recipient extension")
    }

    private func show(status: String, kind: String = "unknown", bytes: Int = 0,
                      digest: String = "", detail: String = "") {
        let update = {
            self.statusLabel.text = "Status: \(status)"
            self.kindLabel.text = "Type: \(kind)"
            self.countLabel.text = "Bytes: \(bytes)"
            self.hashLabel.text = "SHA-256: \(digest)"
            self.detailLabel.text = detail
        }
        if Thread.isMainThread { update() }
        else { DispatchQueue.main.async(execute: update) }
    }
}
