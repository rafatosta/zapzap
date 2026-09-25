"""Keep the Turkish UI catalog free of empty and fuzzy active entries."""

from pathlib import Path
import ast
import gettext
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PO_FILE = ROOT / "po" / "tr.po"
MO_FILE = ROOT / "zapzap" / "po" / "tr" / "LC_MESSAGES" / "zapzap.mo"


def _read_field(lines, prefix):
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        value = ast.literal_eval(line[len(prefix):].strip())
        index += 1
        while index < len(lines) and lines[index].startswith('"'):
            value += ast.literal_eval(lines[index])
            index += 1
        return value
    return None


class TurkishTranslationTests(unittest.TestCase):

    def test_active_entries_are_not_empty_or_fuzzy(self):
        content = PO_FILE.read_text(encoding="utf-8")
        problems = []

        for block in re.split(r"\n\n+", content):
            lines = block.splitlines()
            msgid = _read_field(lines, "msgid ")
            if not msgid:
                continue

            fuzzy = any(
                line.startswith("#,") and "fuzzy" in line
                for line in lines
            )
            plural = _read_field(lines, "msgid_plural ")
            if plural is None:
                translations = [_read_field(lines, "msgstr ")]
            else:
                translations = [
                    _read_field(lines, "msgstr[0] "),
                    _read_field(lines, "msgstr[1] "),
                ]

            if fuzzy or any(not item for item in translations):
                problems.append(msgid)

        self.assertEqual(
            problems,
            [],
            "Untranslated/fuzzy Turkish UI entries: " + ", ".join(problems),
        )

    def test_compiled_catalog_matches_new_translations(self):
        with MO_FILE.open("rb") as stream:
            catalog = gettext.GNUTranslations(stream)

        self.assertEqual(
            catalog.gettext("Could not open link"),
            "Bağlantı açılamadı",
        )
        self.assertEqual(
            catalog.gettext("Update available"),
            "Güncelleme mevcut",
        )
        self.assertEqual(
            catalog.gettext("Send message to number"),
            "Numaraya mesaj gönder",
        )
        self.assertEqual(catalog.gettext("Mute"), "Sessize al")
        self.assertEqual(catalog.gettext("Unmute"), "Sesliye al")


if __name__ == "__main__":
    unittest.main(verbosity=2)
