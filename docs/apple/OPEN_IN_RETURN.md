# iOS document Open In return (optional host integration)

A host app can register one of its **own** supported document formats with iOS Launch Services, then receive a user-selected document via SwiftUI `.onOpenURL`. This is a second *system-mediated* file-return entry point alongside `.fileImporter` and the explicit text-paste route. It is not an automatic agent integration, a device-wide file watcher or access to another app's sandbox.

Apple documents `CFBundleDocumentTypes`, `LSItemContentTypes` and `LSSupportsOpeningDocumentsInPlace` for opening registered documents. For outside-sandbox URLs, the host must use a security scope and coordinate reading. The iOS sample registers **public.json** only as an *alternate Viewer*; generic AYA code never registers a file type on behalf of a host.

## Sample flow

1. Have an external app, a compatible assistant, or Files save a valid `.json` document.
2. In Files, select the saved document and use the available **Share / Open In / Open with** action to choose **AYA Lantern** (exact action labels can differ by iOS release and provider).
3. iOS delivers a file URL to the host's `.onOpenURL` callback. Only a `file:` URL enters the import path; other links are ignored.
4. The sample uses `AYAAppleFileImport.snapshot(userSelectedURL:)`, which requires security-scoped access, coordinated reading and the standard 4 MiB byte ceiling. The original selected URL is not persisted.
5. The sample calls its own `AYAImportRegistry` and `LayoutProposal.decode`; a compatible proposal opens a *separate* preview with Cancel and Apply. The initial return never mutates the layout. Invalid and oversized files must show rejection and preserve state.

**Host decision:** whether to support `public.json` or a custom document UTType is a host-app product choice. Register the narrowest truthful set of formats, as Viewer/alternate where appropriate, to avoid claiming to own every JSON file. Another host can substitute its own declared UTTypes and format validators. The fictional Lantern schema cannot be part of the AYA SDK.

The sample deliberately requires a valid security scope when opening foreign URLs. Some iOS handoffs instead copy a document into a host-owned Inbox that may not carry a security scope; that variant is not yet demonstrated, and must be implemented and tested as a distinct authorized local-file path before claiming universal Open In compatibility. Do not silently weaken the generic file-import requirement to accept arbitrary unscoped paths.

## Native acceptance and limitations

The native workflow now verifies the **built** Lantern Info.plist contains a single `public.json` Viewer/Alternate document declaration and `LSSupportsOpeningDocumentsInPlace = YES`. It also compiles the `.onOpenURL` scene listener and previously qualified AYA file reader with strict Cancel/Apply host logic. **This does not prove Launch Services actually delivered a foreign file.**

An actual physical-device or installed-simulator **Open In** acceptance must separately prove: (a) external file visible in the source app or Files, (b) user explicitly chooses the host, (c) host receives that specific file's bytes via the OS, (d) valid JSON shows preview without changing state, (e) Cancel leaves state unchanged, (f) a second selection + Apply changes state, (g) invalid and >4 MiB documents cannot Apply. Record the exact OS, host build SHA, file origin and security-scope/access failures. Do not pass a test by directly constructing an `AYAImportFile`, passing a local filesystem path to the sample or checking only Info.plist.

This is independent of [#147](https://github.com/gamesbyian/AYA/pull/147), whose original `.fileImporter` system-selection tests remain red. Passing Open In does not qualify the original picker. For the practical physical-device test suite, see [PHYSICAL_FILES_QA.md](PHYSICAL_FILES_QA.md). For text-only agents, see [PASTE_RETURN.md](PASTE_RETURN.md).

### Apple references

- [Open-in-place and document registration](https://developer.apple.com/documentation/UIKit/synchronizing-documents-in-the-icloud-environment)
- [Launch Services document-opening key](https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/LaunchServicesKeys.html)
- [SwiftUI `onOpenURL`](https://developer.apple.com/documentation/swiftui/view/onopenurl%28perform%3A%29)
- [Security-scoped resource rules](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
