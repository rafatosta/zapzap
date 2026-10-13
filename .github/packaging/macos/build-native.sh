#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
mkdir -p build/native
xcrun clang -fobjc-arc -fblocks -dynamiclib -fvisibility=hidden \
    -Wall -Wextra -Werror -mmacosx-version-min=12.0 \
    -framework AppKit -framework UserNotifications -framework Intents \
    -framework UniformTypeIdentifiers \
    zapzap/features/notifications/macos_notifications.m \
    -o build/native/libZapZapNotifications.dylib
