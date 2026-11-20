"""Keep the Indonesian UI catalog complete, non-fuzzy, and placeholder-safe."""

from pathlib import Path
import ast
import gettext
import re
import string
import unittest


ROOT = Path(__file__).resolve().parents[1]
PO_FILE = ROOT / "po" / "id.po"
MO_FILE = ROOT / "zapzap" / "po" / "id" / "LC_MESSAGES" / "zapzap.mo"
LINGUAS_FILE = ROOT / "po" / "LINGUAS"


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


def _placeholders(value: str) -> list[str]:
    return sorted(
        field_name
        for _literal, field_name, _format_spec, _conversion in string.Formatter().parse(value)
        if field_name is not None
    )


class IndonesianTranslationTests(unittest.TestCase):

    def test_id_is_registered_in_linguas(self):
        linguas = [
            line.strip()
            for line in LINGUAS_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertIn("id", linguas)

    def test_active_entries_are_not_empty_or_fuzzy_and_preserve_placeholders(self):
        content = PO_FILE.read_text(encoding="utf-8")
        problems = []
        placeholder_mismatches = []

        for block in re.split(r"\n\n+", content):
            lines = block.splitlines()
            msgid = _read_field(lines, "msgid ")
            if not msgid:
                continue

            flags = set()
            for line in lines:
                if line.startswith("#,"):
                    flags.update(flag.strip() for flag in line[2:].split(",") if flag.strip())

            plural = _read_field(lines, "msgid_plural ")
            if plural is None:
                translations = [_read_field(lines, "msgstr ")]
            else:
                translations = [_read_field(lines, "msgstr[0] ")]

            if "fuzzy" in flags or any(not item for item in translations):
                problems.append(msgid)
                continue

            if plural is not None or "python-brace-format" in flags:
                expected = _placeholders(msgid)
                for translated in translations:
                    if _placeholders(translated) != expected:
                        placeholder_mismatches.append((msgid, translated))

        self.assertEqual(
            problems,
            [],
            "Untranslated/fuzzy Indonesian UI entries: " + ", ".join(problems),
        )
        self.assertEqual(
            placeholder_mismatches,
            [],
            f"Placeholder mismatches in Indonesian UI entries: {placeholder_mismatches}",
        )

    def test_compiled_catalog_loads_and_translates_key_strings(self):
        self.assertTrue(MO_FILE.is_file(), f"Missing compiled catalog: {MO_FILE}")
        with MO_FILE.open("rb") as stream:
            catalog = gettext.GNUTranslations(stream)

        self.assertEqual(catalog.gettext("Close ZapZap"), "Tutup ZapZap")
        self.assertEqual(catalog.gettext("Version {version}"), "Versi {version}")
        self.assertEqual(catalog.gettext("Download behavior"), "Perilaku unduhan")
        self.assertEqual(
            catalog.gettext("Respect Do Not Disturb"),
            "Ikuti mode Jangan Ganggu",
        )
        self.assertEqual(
            catalog.gettext("WhatsApp wants to download multiple files."),
            "WhatsApp ingin mengunduh beberapa file.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
