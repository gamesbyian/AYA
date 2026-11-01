"""Final binary Android manifest metadata pairing and negative controls."""
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess

from verify_android_manifest_metadata import (
    MetadataError, check_metadata, parse_application_metadata,
)

XML = '''N: android=http://schemas.android.com/apk/res/android
  E: manifest (line=2)
    E: application (line=10)
      E: meta-data (line=11)
        A: android:name(0x01010003)="org.godotengine.plugin.v2.AYA" (Raw: "org.godotengine.plugin.v2.AYA")
        A: android:value(0x01010024)="dev.aya.godot.AyaGodotPlugin" (Raw: "dev.aya.godot.AyaGodotPlugin")
      E: receiver (line=20)
        A: android:name(0x01010003)="dev.aya.android.AyaShareSelectionReceiver"
      E: meta-data (line=22)
        A: android:name(0x01010003)="unrelated"
        A: android:value(0x01010024)="unrelated.value"
    E: activity (line=30)
      E: meta-data (line=31)
        A: android:name(0x01010003)="decoy"
        A: android:value(0x01010024)="decoy.value"
'''
NAME = "org.godotengine.plugin.v2.AYA"
VALUE = "dev.aya.godot.AyaGodotPlugin"


class MetadataTests(unittest.TestCase):
    def test_pairs_only_direct_application_metadata(self):
        self.assertEqual(parse_application_metadata(XML),
                         [(NAME, VALUE), ("unrelated", "unrelated.value")])

    def test_rejects_separate_elements_with_disjoint_name_and_value(self):
        changed = XML.replace(
            'A: android:value(0x01010024)="dev.aya.godot.AyaGodotPlugin" (Raw: "dev.aya.godot.AyaGodotPlugin")',
            "E: intent-filter (line=12)\n        A: android:value(0x01010024)=\"dev.aya.godot.AyaGodotPlugin\""
        )
        self.assertNotIn((NAME, VALUE), parse_application_metadata(changed))

    def test_rejects_duplicate_attribute_in_one_metadata(self):
        changed = XML.replace(
            '        A: android:value(0x01010024)="dev.aya.godot.AyaGodotPlugin"',
            '        A: android:name(0x01010003)="duplicate"\n'
            '        A: android:value(0x01010024)="dev.aya.godot.AyaGodotPlugin"'
        )
        with self.assertRaisesRegex(MetadataError, "Duplicate"):
            parse_application_metadata(changed)

    def test_binary_aapt_success_and_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "app.apk"
            apk.write_bytes(b"synthetic parser fixture")
            def runner(cmd, **kwargs):
                self.assertEqual(cmd, [
                    "aapt", "dump", "xmltree", str(apk), "AndroidManifest.xml"
                ])
                return CompletedProcess(cmd, 0, XML, "")
            check_metadata(apk, "aapt", NAME, VALUE, command_runner=runner)
            with self.assertRaisesRegex(MetadataError, "missing, duplicated"):
                check_metadata(apk, "aapt", NAME, "wrong", command_runner=runner)

    def test_fails_closed_on_duplicate_registration(self):
        doubled = XML.replace(
            "      E: receiver (line=20)",
            '      E: meta-data (line=12)\n'
            f'        A: android:name(0x01010003)="{NAME}"\n'
            f'        A: android:value(0x01010024)="{VALUE}"\n'
            "      E: receiver (line=20)"
        )
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "app.apk"
            apk.write_bytes(b"fixture")
            def runner(cmd, **kwargs):
                return CompletedProcess(cmd, 0, doubled, "")
            with self.assertRaisesRegex(MetadataError, "duplicated"):
                check_metadata(apk, "aapt", NAME, VALUE, command_runner=runner)

    def test_missing_apk_and_aapt_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "app.apk"
            with self.assertRaisesRegex(MetadataError, "required"):
                check_metadata(apk, "aapt", NAME, VALUE)
            apk.write_bytes(b"fixture")
            def runner(cmd, **kwargs):
                return CompletedProcess(cmd, 1, "", "aapt inspection error")
            with self.assertRaisesRegex(MetadataError, "inspection failed"):
                check_metadata(apk, "aapt", NAME, VALUE, command_runner=runner)


if __name__ == "__main__":
    unittest.main()
