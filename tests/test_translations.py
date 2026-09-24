"""Regression tests for gettext catalog discovery and Chinese translations."""

from __future__ import annotations

import ast
import gettext
from pathlib import Path
import string
import sys
import unittest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from zapzap.core.i18n.translation_manager import TranslationManager


PO_FILE = REPOSITORY_ROOT / "po" / "zh_CN.po"
LOCALE_DIR = REPOSITORY_ROOT / "zapzap" / "po"


def parse_po_entries(path: Path) -> list[dict]:
    """Read the small PO subset needed by catalog regression tests."""
    entries: list[dict] = []
    current = None

    def finish():
        nonlocal current
        if current is None:
            return
        if current["msgid"] and "".join(current["msgid"]):
            entries.append(current)
        current = None

    def append_literal(parts: list[str], raw: str):
        parts.append(ast.literal_eval(raw))

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            finish()
            continue
        if line.startswith("#,"):
            if current is None:
                current = {"msgid": [], "msgid_plural": [], "msgstr": {}, "flags": set()}
            current["flags"].update(
                flag.strip() for flag in line[2:].split(",") if flag.strip()
            )
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgid_plural "):
            if current is None:
                current = {"msgid": [], "msgid_plural": [], "msgstr": {}, "flags": set()}
            append_literal(current["msgid_plural"], line[len("msgid_plural "):])
            continue
        if line.startswith("msgid "):
            if current is None:
                current = {"msgid": [], "msgid_plural": [], "msgstr": {}, "flags": set()}
            append_literal(current["msgid"], line[len("msgid "):])
            continue
        if line.startswith("msgstr["):
            if current is None:
                current = {"msgid": [], "msgid_plural": [], "msgstr": {}, "flags": set()}
            key, raw = line.split("] ", 1)
            current["msgstr"][key[7:]] = []
            append_literal(current["msgstr"][key[7:]], raw)
            continue
        if line.startswith("msgstr "):
            if current is None:
                current = {"msgid": [], "msgid_plural": [], "msgstr": {}, "flags": set()}
            current["msgstr"]["0"] = []
            append_literal(current["msgstr"]["0"], line[len("msgstr "):])
            continue
        if line.startswith('"'):
            if current is None:
                continue
            if current["msgstr"]:
                append_literal(next(reversed(current["msgstr"].values())), line)
            elif current["msgid_plural"]:
                append_literal(current["msgid_plural"], line)
            else:
                append_literal(current["msgid"], line)
            continue
    finish()

    for entry in entries:
        entry["msgid"] = "".join(entry["msgid"])
        entry["msgid_plural"] = "".join(entry["msgid_plural"])
        entry["msgstr"] = {
            key: "".join(parts) for key, parts in entry["msgstr"].items()
        }
    return entries


def placeholders(value: str) -> list[str]:
    return sorted(
        field_name
        for _literal, field_name, _format_spec, _conversion in string.Formatter().parse(value)
        if field_name is not None
    )


class TranslationCatalogTests(unittest.TestCase):
    def test_zh_cn_is_discoverable_and_loads_from_runtime_catalog(self):
        languages = TranslationManager.list_available_languages()
        self.assertIn("en", languages)
        self.assertIn("pt_BR", languages)
        self.assertIn("zh_CN", languages)

        catalog = gettext.translation(
            "zapzap",
            localedir=str(LOCALE_DIR),
            languages=["zh_CN"],
        )
        self.assertEqual(catalog.gettext("Close ZapZap"), "关闭 ZapZap")
        self.assertEqual(catalog.gettext("Version {version}"), "版本 {version}")

    def test_english_and_existing_catalog_fallbacks_remain_available(self):
        english = gettext.translation(
            "zapzap",
            localedir=str(LOCALE_DIR),
            languages=["en"],
            fallback=True,
        )
        self.assertIsInstance(english, gettext.NullTranslations)
        self.assertEqual(english.gettext("Close ZapZap"), "Close ZapZap")

        portuguese = gettext.translation(
            "zapzap",
            localedir=str(LOCALE_DIR),
            languages=["pt_BR"],
        )
        self.assertEqual(portuguese.gettext("WhatsApp lock"), "Bloqueio do WhatsApp")

    def test_zh_cn_catalog_is_complete_and_preserves_placeholders(self):
        entries = parse_po_entries(PO_FILE)
        self.assertEqual(len(entries), 964)

        for entry in entries:
            self.assertNotIn("fuzzy", entry["flags"], entry["msgid"])
            self.assertTrue(entry["msgstr"], entry["msgid"])
            if entry["msgid_plural"]:
                self.assertEqual(placeholders(entry["msgid"]), placeholders(entry["msgstr"]["0"]))
                continue
            if "python-brace-format" in entry["flags"]:
                self.assertEqual(placeholders(entry["msgid"]), placeholders(entry["msgstr"]["0"]))


if __name__ == "__main__":
    unittest.main()
