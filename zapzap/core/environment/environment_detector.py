from enum import Enum
from gettext import gettext as _

class BuildChannel(Enum):
    OFFICIAL = _("Official")
    COMMUNITY =_("Community")
    CUSTOM = _("Unknown")


try:
    from zapzap.BuildInfo import (
        BUILD_CHANNEL,
        BUILD_PROVIDER,
        BUILD_REPOSITORY,
        BUILD_PACKAGING,
    )
except ImportError:
    BUILD_CHANNEL = BuildChannel.CUSTOM.value
    BUILD_PROVIDER = _("Unknown")
    BUILD_REPOSITORY = _("Unknown")
    BUILD_PACKAGING = _("Unknown")


class EnvironmentDetector:
    CHANNEL = BUILD_CHANNEL
    PROVIDER = BUILD_PROVIDER
    BUILD_REPOSITORY = BUILD_REPOSITORY
    PACKAGING = BUILD_PACKAGING

    @classmethod
    def is_official(cls) -> bool:
        return cls.CHANNEL == BuildChannel.OFFICIAL.value

    @classmethod
    def is_community(cls) -> bool:
        return cls.CHANNEL == BuildChannel.COMMUNITY.value

    @classmethod
    def is_custom(cls) -> bool:
        return cls.CHANNEL == BuildChannel.CUSTOM.value
