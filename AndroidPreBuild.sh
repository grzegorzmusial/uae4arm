#!/usr/bin/env bash
set -euo pipefail
app_dir="$(cd "$(dirname "$0")" && pwd)"
sdl_root="$(cd "$app_dir/../../../.." && pwd)"
if git -C "$sdl_root" apply --reverse --check "$app_dir/usb-gamepads.patch" >/dev/null 2>&1; then
    echo "USB gamepad patch is already applied."
else
    git -C "$sdl_root" apply --check "$app_dir/usb-gamepads.patch"
    git -C "$sdl_root" apply "$app_dir/usb-gamepads.patch"
fi
