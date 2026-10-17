import unittest

from scanner.model import FieldStatus, FieldValue, HardwareProfile


class TestModel(unittest.TestCase):
    def test_field_value_roundtrip(self):
        field = FieldValue(value="xbox", status=FieldStatus.DETECTED, source="generic-host")
        self.assertEqual(field.to_dict()["status"], "detected")
        self.assertEqual(field.to_dict()["source"], "generic-host")

    def test_profile_to_dict_includes_schema_metadata(self):
        profile = HardwareProfile(
            profile_name="sample",
            device_family="console",
            platform="xbox",
            model="series-s",
            fields={
                "serial": FieldValue("ABC123", status=FieldStatus.DETECTED, source="generic-host"),
                "cpu": FieldValue("zen2", status=FieldStatus.DETECTED, source="user-declared"),
            },
            schema_version="1.0",
            scan_id="scan-001",
        )
        data = profile.to_dict()
        self.assertEqual(data["schema_version"], "1.0")
        self.assertEqual(data["scan_id"], "scan-001")
        self.assertEqual(data["fields"]["cpu"]["source"], "user-declared")

    def test_redaction_for_save(self):
        profile = HardwareProfile(
            profile_name="sample",
            device_family="console",
            platform="xbox",
            model="series-s",
            fields={
                "serial": FieldValue("ABC123", status=FieldStatus.DETECTED, source="generic-host"),
                "hostname": FieldValue("host-01", status=FieldStatus.DETECTED, source="generic-host"),
                "cpu": FieldValue("zen2", status=FieldStatus.DETECTED, source="user-declared"),
            },
            provenance={"source": "scan"},
        )
        saved = profile.redact_for_save()
        self.assertEqual(saved.fields["serial"].value, "<REDACTED>")
        self.assertEqual(saved.fields["hostname"].value, "<REDACTED>")
        self.assertEqual(saved.fields["cpu"].value, "zen2")
        self.assertIn("redactions", saved.provenance)

    def test_unknown_is_not_zero(self):
        field = FieldValue(value=None, status=FieldStatus.UNKNOWN, source="generic-host")
        self.assertIsNone(field.value)
        self.assertEqual(field.status, FieldStatus.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
