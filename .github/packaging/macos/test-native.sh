#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
mkdir -p build/native
xcrun clang -fobjc-arc -fblocks -Wall -Wextra -Werror \
    -mmacosx-version-min=12.0 \
    -framework AppKit -framework UserNotifications -framework Intents \
    -framework UniformTypeIdentifiers \
    tests/macos_notification_bridge.m -o build/native/notification-lifecycle-test
build/native/notification-lifecycle-test
