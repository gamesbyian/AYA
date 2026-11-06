import SwiftUI
import Foundation

/// Disposable installation container for the separately packaged Share Extension.
/// The host app itself never reads AYA data and is not an AYA runtime dependency.
@main
struct AYAShareQAHostApp: App {
    init() {
        // Simulator acceptance only: have the independently installed QA
        // application create its own files through FileManager. This is
        // intentionally separate from the AYA importing host and bypasses
        // neither the system Files picker nor host-side byte validation.
        let arguments = ProcessInfo.processInfo.arguments
        let isolated: String? = arguments.contains("--aya-stage-single-valid")
            ? "aya-layout-valid.json"
            : arguments.contains("--aya-stage-single-invalid")
                ? "aya-layout-invalid.json" : nil
        let sevenSmall = arguments.contains("--aya-stage-seven-small")
        if arguments.contains("--aya-stage-fixtures") || isolated != nil || sevenSmall {
            do {
                try Self.stageLocalProviderFixtures(only: isolated, smallOversized: sevenSmall)
            } catch {
                NSLog("AYA QA fixture staging failed: %@", String(describing: error))
            }
        }
    }

    private static func stageLocalProviderFixtures(
        only: String? = nil, smallOversized: Bool = false
    ) throws {
        let manager = FileManager.default
        let directory = try manager.url(
            for: .documentDirectory, in: .userDomainMask,
            appropriateFor: nil, create: true
        )
        func put(_ name: String, _ content: String) throws {
            guard only == nil || name == only else { return }
            try Data((content + "\n").utf8).write(
                to: directory.appendingPathComponent(name), options: .atomic
            )
        }

        try put("aya-layout-valid.json", #"{"aya_demo_layout":"v1","columns":3,"accent":"cool"}"#)
        try put("aya-layout-invalid.json", #"{"aya_demo_layout":"v1","columns":99,"accent":"invalid"}"#)
        try put("aya-layout-boolean.json", #"{"aya_demo_layout":"v1","columns":true,"accent":"cool"}"#)
        try put("aya-layout-float.json", #"{"aya_demo_layout":"v1","columns":1.0,"accent":"cool"}"#)
        try put("aya-layout-aaa-control.json", #"{"aya_demo_layout":"v1","columns":3,"accent":"cool"}"#)
        try put("aya-layout-zzz-invalid.json", #"{"aya_demo_layout":"v1","columns":99,"accent":"invalid"}"#)

        // Controlled File Provider differential: keep all seven names and
        // the invalid JSON target unchanged, replacing *only* the neighboring
        // 4 MiB+1 document with a tiny valid JSON in --aya-stage-seven-small.
        // Ordinary --aya-stage-fixtures still enforces the real byte cap.
        if only == nil {
            if smallOversized {
                try put("aya-layout-oversized.json",
                        #"{"aya_demo_layout":"v1","columns":3,"accent":"cool"}"#)
            } else {
                let prefix = Data(#"{"aya_demo_layout":"v1","columns":3,"accent":"cool"}"#.utf8)
                let oversizedCount = 4 * 1_024 * 1_024 + 1
                precondition(prefix.count < oversizedCount)
                var oversized = Data(capacity: oversizedCount)
                oversized.append(prefix)
                oversized.append(Data(repeating: 0x20, count: oversizedCount - prefix.count))
                try oversized.write(
                    to: directory.appendingPathComponent("aya-layout-oversized.json"),
                    options: .atomic
                )
            }
        }
        NSLog("AYA QA staged %@ through its owning application",
              only ?? (smallOversized ? "seven small fixtures" : "seven fixtures"))
    }

    var body: some Scene {
        WindowGroup {
            VStack(spacing: 12) {
                Text("AYA Share QA")
                    .font(.title)
                Text("This disposable test app installs a separate Share Extension for verifying bytes received through the iOS Share Sheet.")
                    .multilineTextAlignment(.center)
                Text("There is no account, backend, inbox, saved document or automatic import.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            .padding()
        }
    }
}
