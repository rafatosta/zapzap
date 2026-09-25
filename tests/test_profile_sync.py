import base64
import unittest

from PyQt6.QtGui import QImage

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.accounts.domain.profile_sync import (
    ProfileSyncError,
    ProfileSyncService,
)


class ProfileSyncServiceTest(unittest.TestCase):
    def _png_data_url(self):
        image = QImage(4, 4, QImage.Format.Format_RGB32)
        image.fill(0x336699)
        from PyQt6.QtCore import QBuffer, QIODevice

        buffer = QBuffer()
        self.assertTrue(buffer.open(QIODevice.OpenModeFlag.ReadWrite))
        self.assertTrue(image.save(buffer, "PNG"))
        return "data:image/png;base64," + base64.b64encode(
            bytes(buffer.data())
        ).decode("ascii")

    def test_payload_normalizes_photo_and_keeps_name_separate(self):
        result = ProfileSyncService.result_from_payload({
            "name": " Rafael Tosta ",
            "avatar": self._png_data_url(),
        })

        self.assertEqual(result.name, "Rafael Tosta")
        self.assertTrue(result.photo_data.startswith(UserIcon.PHOTO_PREFIX))

    def test_invalid_payload_does_not_create_data(self):
        with self.assertRaises(ProfileSyncError):
            ProfileSyncService.result_from_payload({"avatar": "blob:temporary"})

    def test_missing_profile_data_is_rejected(self):
        with self.assertRaises(ProfileSyncError):
            ProfileSyncService.result_from_payload({"name": "", "avatar": None})

    def test_capture_runs_javascript_once_and_returns_validated_result(self):
        class FakePage:
            def runJavaScript(self, script, callback):
                self.script = script
                callback({"name": "Rafael", "avatar": None})

        page = FakePage()
        received = []
        ProfileSyncService.capture(
            page,
            lambda result, error: received.append((result, error)),
        )

        self.assertIn("return {", page.script)
        self.assertEqual(received[0][0].name, "Rafael")
        self.assertIsNone(received[0][1])


if __name__ == "__main__":
    unittest.main()