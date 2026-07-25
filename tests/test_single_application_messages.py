"""Tests for messages exchanged between ZapZap application instances."""

import unittest

from zapzap.app.single_application import SingleApplication


class SingleApplicationMessageTests(unittest.TestCase):
    def test_instance_message_preserves_command_and_activation_token(self):
        message = SingleApplication.build_instance_message(
            "zapzap://activate",
            "activation-token-with-special/chars+=",
        )

        self.assertEqual(
            SingleApplication.parse_instance_message(message),
            (
                "zapzap://activate",
                "activation-token-with-special/chars+=",
            ),
        )

    def test_instance_message_supports_missing_activation_token(self):
        message = SingleApplication.build_instance_message(
            "whatsapp://send?phone=123",
        )

        self.assertEqual(
            SingleApplication.parse_instance_message(message),
            ("whatsapp://send?phone=123", None),
        )

    def test_malformed_instance_messages_are_rejected(self):
        invalid_messages = (
            "zapzap://activate",
            "zapzap://instance/not-base64!",
            "zapzap://instance/e30=",
        )

        for message in invalid_messages:
            with self.subTest(message=message):
                self.assertIsNone(
                    SingleApplication.parse_instance_message(message)
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
