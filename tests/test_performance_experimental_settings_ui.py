"""UI regression tests for experimental performance settings."""

from qt_test_case import QtTestCase
from zapzap.core.config.settings.performance import (
    COMPATIBILITY_RENDERING_PRESET,
    DEFAULT_RENDERING_PRESET,
    MAX_HTTP_CACHE_MIB,
    PerformanceSettings,
    RenderingProfile,
)
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.ui.components import SettingsRestartBar
from zapzap.features.settings.pages.performance_experimental.controller import (
    PerformanceExperimentalSettingsController,
)


class PerformanceExperimentalSettingsUiTests(QtTestCase):

    def setUp(self):
        SettingsManager.clear()

    def test_software_video_decoding_uses_gpu_section_and_full_restart(self):
        page = PerformanceExperimentalSettingsController()

        self.assertEqual(
            page.software_video_decoding_row.title_label.text(),
            "Use software video decoding",
        )
        self.assertIn(
            "CPU and battery usage",
            page.software_video_decoding_row.description_label.text(),
        )
        self.assertFalse(page.software_video_decoding.isChecked())

        page.software_video_decoding.click()

        self.assertTrue(
            page.model.get_boolean_setting("software_video_decoding")
        )
        self.assertEqual(
            page.restart_bar.restart_kind,
            SettingsRestartBar.APPLICATION,
        )

        page.rendering_default_radio.click()

        self.assertIsNone(page.restart_bar.restart_kind)

    def test_default_profile_applies_and_persists_exact_rendering_defaults(self):
        settings = PerformanceSettings()
        settings.apply_rendering_profile(RenderingProfile.COMPATIBILITY)
        settings.set_boolean_setting("single_process", True)
        settings.set_boolean_setting("background_throttling", False)
        settings.set_boolean_setting("disable_accessibility", True)
        settings.set_boolean_setting("disable_pinch", True)
        settings.js_memory_limit_index = 2
        page = PerformanceExperimentalSettingsController()

        page.rendering_default_radio.click()

        self.assertTrue(page.rendering_default_radio.isChecked())
        self.assertEqual(
            page.model.rendering_profile,
            RenderingProfile.DEFAULT,
        )
        for name, expected in DEFAULT_RENDERING_PRESET.items():
            self.assertEqual(
                page.model.get_boolean_setting(name),
                expected,
                name,
            )
            self.assertEqual(getattr(page, name).isChecked(), expected, name)
        self.assertTrue(page.model.get_boolean_setting("single_process"))
        self.assertFalse(page.model.get_boolean_setting("background_throttling"))
        self.assertTrue(page.model.get_boolean_setting("disable_accessibility"))
        self.assertTrue(page.model.get_boolean_setting("disable_pinch"))
        self.assertEqual(page.model.js_memory_limit_index, 2)
        self.assertEqual(
            page.restart_bar.restart_kind,
            SettingsRestartBar.APPLICATION,
        )

    def test_compatibility_profile_applies_only_conservative_workarounds(self):
        page = PerformanceExperimentalSettingsController()

        page.rendering_compatibility_radio.click()

        self.assertTrue(page.rendering_compatibility_radio.isChecked())
        self.assertEqual(
            page.model.rendering_profile,
            RenderingProfile.COMPATIBILITY,
        )
        for name, expected in COMPATIBILITY_RENDERING_PRESET.items():
            self.assertEqual(
                page.model.get_boolean_setting(name),
                expected,
                name,
            )
            self.assertEqual(getattr(page, name).isChecked(), expected, name)
        self.assertFalse(page.disable_gpu.isChecked())
        self.assertFalse(page.software_rendering.isChecked())
        self.assertFalse(page.in_process_gpu.isChecked())
        self.assertEqual(
            page.restart_bar.restart_kind,
            SettingsRestartBar.APPLICATION,
        )

    def test_manual_change_resynchronizes_profile_from_effective_values(self):
        page = PerformanceExperimentalSettingsController()
        page.rendering_compatibility_radio.click()

        page.software_video_decoding.click()

        self.assertTrue(page.rendering_manual_radio.isChecked())
        self.assertEqual(page.model.rendering_profile, RenderingProfile.MANUAL)
        self.assertEqual(
            page.restart_bar.restart_kind,
            SettingsRestartBar.APPLICATION,
        )

        page.software_video_decoding.click()

        self.assertTrue(page.rendering_compatibility_radio.isChecked())
        self.assertEqual(
            page.model.rendering_profile,
            RenderingProfile.COMPATIBILITY,
        )

    def test_existing_settings_are_detected_without_a_mode_migration(self):
        settings = PerformanceSettings()
        settings.apply_rendering_profile(RenderingProfile.COMPATIBILITY)

        compatibility_page = PerformanceExperimentalSettingsController()

        self.assertTrue(
            compatibility_page.rendering_compatibility_radio.isChecked()
        )
        self.assertFalse(SettingsManager.contains("performance/rendering_mode"))

        SettingsManager.clear()
        settings = PerformanceSettings()
        settings.set_boolean_setting("disable_gpu", True)
        manual_page = PerformanceExperimentalSettingsController()

        self.assertTrue(manual_page.rendering_manual_radio.isChecked())
        self.assertTrue(manual_page.disable_gpu.isChecked())
        self.assertFalse(SettingsManager.contains("performance/rendering_mode"))

    def test_rendering_profile_copy_and_new_controls_are_accessible(self):
        page = PerformanceExperimentalSettingsController()

        self.assertEqual(page.rendering_default_radio.text(), "Default")
        self.assertEqual(
            page.rendering_compatibility_radio.text(),
            "Compatibility",
        )
        self.assertEqual(page.rendering_manual_radio.text(), "Manual")
        for radio in (
            page.rendering_default_radio,
            page.rendering_compatibility_radio,
            page.rendering_manual_radio,
        ):
            self.assertTrue(radio.accessibleDescription())
        self.assertEqual(
            page.disable_gpu_memory_buffer_video_frames_row.title_label.text(),
            "Disable GPU memory buffer for video",
        )
        self.assertEqual(
            page.disable_zero_copy_row.title_label.text(),
            "Disable zero-copy",
        )
        self.assertTrue(page.disable_gpu_memory_buffer_video_frames.isEnabled())
        self.assertTrue(page.disable_zero_copy.isEnabled())

    def test_http_cache_selector_uses_qt_safe_mib_values(self):
        page = PerformanceExperimentalSettingsController()
        values = [
            page.cache_size_max.itemData(index)
            for index in range(page.cache_size_max.count())
        ]

        self.assertEqual(values[0], 0)
        self.assertEqual(values[-1], MAX_HTTP_CACHE_MIB)
        self.assertTrue(all(value <= MAX_HTTP_CACHE_MIB for value in values))
        self.assertNotIn(2048, values)
        self.assertEqual(
            page.cache_size_max.itemText(page.cache_size_max.count() - 1),
            "2047 MiB",
        )
        self.assertIn(
            "automatic",
            page.cache_size_max_row.description_label.text(),
        )
        self.assertIn("2047 MiB", page.cache_size_max.toolTip())
