"""Synthetic nested AIX/AAR/DEX fixtures and fail-closed native manifest tests."""
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from test_verify_android_adapter_apk import dex_for_class
from verify_appinventor_aix import (
    AAR_NAME, AIXError, CORE_ACTION, FILE_PATHS, PREFIX,
    PROVIDER, RECEIVER, REPACK, main, verify_aix,
)


def _zip(items):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for path, content in items.items():
            archive.writestr(path, content)
    return stream.getvalue()


class AIXIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "dev.aya.appinventor.aix"

    def build(self, *,
              activity_provider=PROVIDER,
              activity_authority="%packageName%.aya.files",
              aur_receiver=RECEIVER,
              native_provider=PROVIDER,
              native_authority="${applicationId}.aya.files",
              include_native_receiver=True,
              include_paths=True,
              include_core=True,
              methods=("HostIdentity", "OpenHelp"),
              dex_defined=True,
              extra_permissions=(),
              include_aar=True):
        android = "http://schemas.android.com/apk/res/android"
        pxml = (
            f'<provider xmlns:android="{android}" '
            f'android:name="{activity_provider}" android:authorities="{activity_authority}" '
            'android:exported="false" android:grantUriPermissions="true">'
            '<meta-data android:name="android.support.FILE_PROVIDER_PATHS" '
            f'android:resource="@xml/{FILE_PATHS}" /></provider>'
        )
        rxml = (
            f'<receiver xmlns:android="{android}" '
            f'android:name="{aur_receiver}" android:exported="false"/>'
        )
        info = [{
            "type": "dev.aya.appinventor.AyaHelp",
            "libraries": [AAR_NAME], "activities": [pxml, rxml],
            "permissions": list(extra_permissions), "queries": []
        }]
        component = [{
            "type": "dev.aya.appinventor.AyaHelp",
            "methods": [{"name": name} for name in methods],
            "events": [{"name": "LocalStatus"}],
        }]
        a_manifest = (
            f'<manifest xmlns:android="{android}" package="{REPACK}.dev.aya.android">'
            '<application>'
            f'<provider android:name="{native_provider}" '
            f'android:authorities="{native_authority}" android:exported="false" '
            'android:grantUriPermissions="true">'
            '<meta-data android:name="android.support.FILE_PROVIDER_PATHS" '
            f'android:resource="@xml/{FILE_PATHS}"/></provider>'
            + (f'<receiver android:name="{RECEIVER}" android:exported="false"/>'
               if include_native_receiver else "")
            + '</application></manifest>'
        )
        paths = ('<paths><cache-path name="aya_help" path="aya/"/></paths>').encode()
        classes = {
            CORE_ACTION: b"compiled action class",
            PROVIDER.replace(".", "/") + ".class": b"compiled provider class",
            RECEIVER.replace(".", "/") + ".class": b"compiled receiver class",
        }
        if not include_core:
            classes.pop(CORE_ACTION)
        aar = {
            "AndroidManifest.xml": a_manifest.encode(),
            "classes.jar": _zip(classes),
        }
        if include_paths:
            aar[f"res/xml/{FILE_PATHS}.xml"] = paths
        payload = {
            PREFIX + "components.json": json.dumps(component).encode(),
            PREFIX + "classes.jar": _zip({
                "classes.dex": dex_for_class("dev.aya.appinventor.AyaHelp",
                                             define=dex_defined),
            }),
            PREFIX + "files/AndroidRuntime.jar": b"real runtime substitute",
            PREFIX + "files/component_build_infos.json": json.dumps(info).encode(),
        }
        if include_aar:
            payload[PREFIX + "aars/" + AAR_NAME] = _zip(aar)
        self.path.write_bytes(_zip(payload))
        return self.path

    def test_valid_nested_aix_proves_compiled_blocks_and_relocated_native_files(self):
        report = verify_aix(self.build())
        self.assertEqual(report["schema"], "aya-appinventor-aix-integrity/v1")
        self.assertEqual(report["native_provider"], PROVIDER)
        self.assertEqual(report["native_receiver"], RECEIVER)
        self.assertEqual(report["method_blocks"], ["HostIdentity", "OpenHelp"])
        self.assertTrue(report["compiled_extension_dex"])
        self.assertTrue(report["repacked_native_aar_classes"])
        self.assertEqual(report["permission_declarations"], 0)
        self.assertIn("not a consuming", report["evidence"])

    def test_rejects_unsafe_extra_permissions_or_unexpected_block(self):
        with self.assertRaisesRegex(AIXError, "permissions"):
            verify_aix(self.build(extra_permissions=("android.permission.READ_CONTACTS",)))
        with self.assertRaisesRegex(AIXError, "guarded help"):
            verify_aix(self.build(methods=("HostIdentity", "OpenHelp", "SendWithoutReview")))

    def test_rejects_missing_or_unrelated_native_aix_aar(self):
        with self.assertRaisesRegex(AIXError, "native extension members"):
            verify_aix(self.build(include_aar=False))
        with self.assertRaisesRegex(AIXError, "native AYA compiled class"):
            verify_aix(self.build(include_core=False))

    def test_rejects_mismatched_manifest_provider_authority_or_name(self):
        with self.assertRaisesRegex(AIXError, "provider/receiver declaration mismatch"):
            verify_aix(self.build(activity_authority="example.unknown"))
        with self.assertRaisesRegex(AIXError, "provider/receiver declaration mismatch"):
            verify_aix(self.build(aur_receiver="dev.elsewhere.Receiver"))
        with self.assertRaisesRegex(AIXError, "AAR manifest does not match"):
            verify_aix(self.build(native_authority="com.example.unsafe"))
        with self.assertRaisesRegex(AIXError, "AAR manifest does not match"):
            verify_aix(self.build(native_provider="dev.elsewhere.Provider"))

    def test_rejects_missing_receiver_or_unsafe_provider_paths(self):
        with self.assertRaisesRegex(AIXError, "AAR manifest does not match"):
            verify_aix(self.build(include_native_receiver=False))
        with self.assertRaisesRegex(AIXError, "Missing, duplicate"):
            verify_aix(self.build(include_paths=False))

    def test_dex_string_reference_without_definition_is_insufficient(self):
        with self.assertRaisesRegex(AIXError, "not defined"):
            verify_aix(self.build(dex_defined=False))

    def test_rejects_bad_or_symlinked_artifact(self):
        self.path.write_bytes(b"bad")
        with self.assertRaisesRegex(AIXError, "bounded"):
            verify_aix(self.path)
        valid = self.build()
        moved = valid.with_name("actual.aix")
        valid.rename(moved)
        valid.symlink_to(moved)
        with self.assertRaisesRegex(AIXError, "bounded"):
            verify_aix(valid)


if __name__ == "__main__":
    unittest.main()
