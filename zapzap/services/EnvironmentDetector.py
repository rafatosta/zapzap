from enum import Enum


class BuildChannel(Enum):
    OFFICIAL = "Official"
    COMMUNITY = "Community"
    CUSTOM = "Custom"


try:
    from zapzap.BuildInfo import (
        BUILD_CHANNEL,
        BUILD_PROVIDER,
        BUILD_COMMIT,
    )
except ImportError:
    BUILD_CHANNEL = BuildChannel.CUSTOM.value
    BUILD_PROVIDER = "Unknown"
    BUILD_COMMIT = "Unknown"


class EnvironmentDetector:
    CHANNEL = BUILD_CHANNEL
    PROVIDER = BUILD_PROVIDER
    COMMIT = BUILD_COMMIT

    @classmethod
    def is_official(cls) -> bool:
        return cls.CHANNEL == BuildChannel.OFFICIAL.value

    @classmethod
    def is_community(cls) -> bool:
        return cls.CHANNEL == BuildChannel.COMMUNITY.value

    @classmethod
    def is_custom(cls) -> bool:
        return cls.CHANNEL == BuildChannel.CUSTOM.value