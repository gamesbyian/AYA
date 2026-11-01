"""Structural fake-aapt fixtures for two independent secure APK FileProviders."""
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess

from verify_android_manifest_providers import ProviderError, check_providers, parse_providers

AYA = "dev.aya.android.AyaFileProvider"
HOST = "androidx.core.content.FileProvider"
PKG = "com.example.synthetic"
EXPECTED = {
    AYA: PKG + ".aya.files",
    HOST: PKG + ".fileprovider",
}

XML = f'''N: android=http://schemas.android.com/apk/res/android
  E: manifest (line=2)
    E: application (line=12)
      E: provider (line=13)
        A: android:name(0x01010003)="{AYA}" (Raw: "{AYA}")
        A: android:authorities(0x01010018)="{PKG}.aya.files"
        A: android:exported(0x01010010)=(type 0x12)0x0
        A: android:grantUriPermissions(0x0101001b)=(type 0x12)0xffffffff
        E: meta-data (line=16)
          A: android:name(0x01010003)="android.support.FILE_PROVIDER_PATHS"
          A: android:resource(0x01010025)=@0x7f0e0003
      E: provider (line=21)
        A: android:name(0x01010003)="{HOST}"
        A: android:authorities(0x01010018)="{PKG}.fileprovider"
        A: android:exported(0x01010010)=(type 0x12)0x0
        A: android:grantUriPermissions(0x0101001b)=(type 0x12)0x1
        E: meta-data (line=26)
          A: android:name(0x01010003)="android.support.FILE_PROVIDER_PATHS"
          A: android:resource(0x01010025)=@0x7f0e0004
      E: receiver (line=30)
        A: android:name(0x01010003)="dev.aya.android.AyaShareSelectionReceiver"
'''


class ManifestProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.apk = Path(self.temp.name) / "app-debug.apk"
        self.apk.write_bytes(b"fake binary; mocked aapt owns parsing")

    def inspect(self, xml=XML, *, expected=None):
        def run(argv, **kwargs):
            self.assertEqual(argv, [
                "aapt", "dump", "xmltree", str(self.apk), "AndroidManifest.xml"
            ])
            self.assertEqual(kwargs["timeout"], 30)
            return CompletedProcess(argv, 0, xml, "")
        return check_providers(
            self.apk, "aapt", EXPECTED if expected is None else expected,
            command_runner=run,
        )

    def test_two_independent_nonexported_read_granted_providers(self):
        found = self.inspect()
        self.assertEqual(len(found), 2)
        self.assertEqual([x["class"] for x in found], [AYA, HOST])
        self.assertEqual(found[0]["authority"], PKG + ".aya.files")
        self.assertEqual(found[1]["authority"], PKG + ".fileprovider")
        self.assertEqual(found[0]["paths"][0][0],
                         "android.support.FILE_PROVIDER_PATHS")

    def test_godot_or_aya_provider_can_be_missing_but_never_substituted(self):
        for name in (AYA, HOST):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ProviderError, "missing"):
                    self.inspect(XML.replace(name, "missing.foreign.Provider", 1))

    def test_deprecated_generic_aya_registration_is_not_sufficient(self):
        changed = XML.replace(
            'A: android:name(0x01010003)="' + AYA + '"',
            'A: android:name(0x01010003)="' + HOST + '"',
            1,
        )
        with self.assertRaises(ProviderError):
            self.inspect(changed)

    def test_wrong_authority_is_rejected_even_if_elsewhere_in_apk(self):
        changed = XML.replace(
            f'A: android:authorities(0x01010018)="{PKG}.aya.files"',
            f'A: android:authorities(0x01010018)="{PKG}.wrong"',
            1,
        )
        # The unrelated receiver contains that string, but the actual
        # provider owns a different one.
        changed += f'        A: android:label="{PKG}.aya.files"\n'
        with self.assertRaisesRegex(ProviderError, "authority mismatched"):
            self.inspect(changed)

    def test_provider_exported_or_without_read_grants_refuses(self):
        changed = XML.replace(
            "android:exported(0x01010010)=(type 0x12)0x0",
            "android:exported(0x01010010)=(type 0x12)0xffffffff",
            1,
        )
        with self.assertRaisesRegex(ProviderError, "security flags"):
            self.inspect(changed)
        changed = XML.replace(
            "android:grantUriPermissions(0x0101001b)=(type 0x12)0xffffffff",
            "android:grantUriPermissions(0x0101001b)=(type 0x12)0x0",
            1,
        )
        with self.assertRaisesRegex(ProviderError, "security flags"):
            self.inspect(changed)

    def test_meta_path_must_be_inside_the_same_provider(self):
        altered = XML.replace(
            "android.support.FILE_PROVIDER_PATHS",
            "host.unrelated.METADATA",
            1,
        )
        with self.assertRaisesRegex(ProviderError, "scoped file-path"):
            self.inspect(altered)
        no_resource = XML.replace(
            '        A: android:resource(0x01010025)=@0x7f0e0003',
            '        A: android:resource(0x01010025)="untrusted-path"',
            1,
        )
        with self.assertRaisesRegex(ProviderError, "scoped file-path"):
            self.inspect(no_resource)

    def test_duplicate_classes_and_authorities_are_rejected(self):
        same_authority = XML.replace(
            f'A: android:authorities(0x01010018)="{PKG}.fileprovider"',
            f'A: android:authorities(0x01010018)="{PKG}.aya.files"',
            1,
        )
        with self.assertRaisesRegex(ProviderError, "authorities collide"):
            self.inspect(same_authority)

    def test_invalid_input_and_missing_apk_fail_closed(self):
        self.apk.unlink()
        with self.assertRaisesRegex(ProviderError, "real APK"):
            self.inspect()
        self.apk.write_bytes(b"fixture")
        for values in ({}, {AYA: "../bad"}, {"NotQualified": PKG + ".aya.files"},
                       {AYA: PKG + ".fileprovider", HOST: PKG + ".fileprovider"}):
            with self.subTest(values=values), self.assertRaises(ProviderError):
                self.inspect(expected=values)

    def test_broken_aapt_execution_refuses(self):
        def runner(argv, **kwargs):
            return CompletedProcess(argv, 1, "", "cannot parse APK")
        with self.assertRaisesRegex(ProviderError, "Cannot read final APK"):
            check_providers(self.apk, "aapt", EXPECTED, command_runner=runner)

    def test_rejects_oversized_or_duplicate_xml_metadata(self):
        with self.assertRaisesRegex(ProviderError, "inspection budget"):
            parse_providers("x" * (4 * 1024 * 1024 + 1))
        duplicate = XML.replace(
            f'        A: android:name(0x01010003)="{AYA}"',
            f'        A: android:name(0x01010003)="{AYA}"\n'
            f'        A: android:name(0x01010003)="{AYA}"',
            1,
        )
        with self.assertRaisesRegex(ProviderError, "Duplicate Android manifest attribute"):
            parse_providers(duplicate)


if __name__ == "__main__":
    unittest.main()
