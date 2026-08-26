"""Persisted preferences for local problem-report preparation."""

from zapzap.core.config.settings.base import BaseSettings


class ReportingSettings(BaseSettings):
    """Settings that authorize local preparation, never transmission."""

    CRASH_PROMPTS = ("reporting/crash_prompts", False)
    CRASH_PROMPTS_EXPLAINED = ("reporting/crash_prompts_explained", False)

    @property
    def crash_prompts_enabled(self) -> bool:
        return self._get_bool(self.CRASH_PROMPTS)

    @crash_prompts_enabled.setter
    def crash_prompts_enabled(self, value: bool) -> None:
        self._set_bool(self.CRASH_PROMPTS, value)

    @property
    def crash_prompts_explained(self) -> bool:
        return self._get_bool(self.CRASH_PROMPTS_EXPLAINED)

    @crash_prompts_explained.setter
    def crash_prompts_explained(self, value: bool) -> None:
        self._set_bool(self.CRASH_PROMPTS_EXPLAINED, value)
