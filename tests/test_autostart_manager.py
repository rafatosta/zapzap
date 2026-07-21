"""Tests for Flatpak autostart requests."""

import sys
import unittest
from unittest.mock import MagicMock, patch

from zapzap.features.startup.autostart_manager import AutostartManager


class FlatpakAutostartTests(unittest.TestCase):
    def test_commandline_is_marshaled_as_string_array(self):
        dbus = MagicMock()
        dbus.Array.side_effect = lambda values, signature=None: (values, signature)

        with patch.dict(sys.modules, {"dbus": dbus}):
            AutostartManager._handle_flatpak(True)

        options = dbus.Interface.return_value.RequestBackground.call_args.args[1]
        self.assertEqual((["zapzap", "--hideStart"], "s"), options["commandline"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
