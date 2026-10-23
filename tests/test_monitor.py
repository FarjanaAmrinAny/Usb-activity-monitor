import unittest

from monitor import classify_device


class TestUSBAllowlist(unittest.TestCase):

    def setUp(self):
        self.allowed = {"TEST-USB-123"}

    def test_allowlisted_device_is_authorized(self):
        status, _ = classify_device(
            "TEST-USB-123", self.allowed
        )
        self.assertEqual(status, "AUTHORIZED")

    def test_unknown_serial_is_unauthorized(self):
        status, _ = classify_device(
            "OTHER-USB-456", self.allowed
        )
        self.assertEqual(status, "UNAUTHORIZED")

    def test_missing_serial_needs_review(self):
        status, _ = classify_device(None, self.allowed)
        self.assertEqual(status, "REVIEW")

    def test_empty_allowlist_is_unknown(self):
        status, _ = classify_device(
            "TEST-USB-123", set()
        )
        self.assertEqual(status, "UNKNOWN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
