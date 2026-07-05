"""Unit tests for zapzap.webengine.deeplink.

These tests load the helper directly by path so they do not import the zapzap
package, which requires PyQt6 in ``zapzap.__init__``.
"""

import importlib.util
import json
import os
import unittest

_DEEPLINK_PATH = os.path.join(
    os.path.dirname(__file__), "..", "zapzap", "webengine", "deeplink.py"
)
_SPEC = importlib.util.spec_from_file_location("zapzap_deeplink", _DEEPLINK_PATH)
_deeplink = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_deeplink)

build_open_chat_script = _deeplink.build_open_chat_script


class BuildOpenChatScriptTests(unittest.TestCase):
    def test_legit_whatsapp_link_allowed(self):
        script = build_open_chat_script("whatsapp://send?phone=15551234567")

        self.assertIsNotNone(script)
        self.assertIn("a.click()", script)

    def test_http_and_https_links_allowed(self):
        self.assertIsNotNone(build_open_chat_script("https://web.whatsapp.com/"))
        self.assertIsNotNone(build_open_chat_script("http://example.invalid/"))

    def test_javascript_scheme_rejected(self):
        self.assertIsNone(build_open_chat_script("javascript:alert(1)"))

    def test_data_scheme_rejected(self):
        self.assertIsNone(
            build_open_chat_script("data:text/html,<script>alert(1)</script>")
        )

    def test_empty_and_missing_scheme_rejected(self):
        self.assertIsNone(build_open_chat_script(""))
        self.assertIsNone(build_open_chat_script("just-some-text"))

    def test_url_embedded_only_as_json_literal(self):
        for payload in [
            'whatsapp://x";alert(document.cookie);a.href="',
            'whatsapp://\n"+alert(1)+"',
            "whatsapp://send?phone=1",
        ]:
            script = build_open_chat_script(payload)

            self.assertIsNotNone(script)
            self.assertIn(json.dumps(payload), script)

    def test_breakout_tokens_not_present_as_code(self):
        payload = 'whatsapp://x";alert(document.cookie);a.href="'
        script = build_open_chat_script(payload)
        scaffold = script.replace(json.dumps(payload), "URL")

        self.assertNotIn("alert", scaffold)
        self.assertNotIn("document.cookie", scaffold)


if __name__ == "__main__":
    unittest.main(verbosity=2)
