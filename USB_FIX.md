# UAE4ARM USB joystick test build

This fork changes hardware button 4 (and a gamepad button mapped to PageUp) to the Fire action used by touchscreen button 3. Physical gamepads use independent SDL joystick states, so player 2 cannot release or move player 1's joystick.

- First connected controller: Gamepad 1 / touch, Amiga Port 2.
- Second connected controller: Gamepad 2, Amiga Port 1.
- Touch controls still drive player 1.
- In Game ports, select these devices in Joystick mode if an existing .uae file overrides the defaults.
- Both pads should be connected before starting the emulator; reconnect and restart if Android changes their order.
- Use the touchscreen for menu navigation. Physical gameplay controls are routed directly to the individual SDL joysticks.
- Enable two human-controlled teams in SWOS for a two-player match.

The APK is named Uae4arm USB Fix, package atua.anddev.uae4arm.usbfix, so it installs beside the original application. It uses a test signing key and does not include game data, Kickstart ROMs, or the original app's private settings.

Build follows How_to_build.txt with Android SDL e0d402e50, capsimg ed4cb09, NDK 25.2.9519653, and Java 17. GitHub Actions builds armeabi-v7a and arm64-v8a and verifies the APK signature.

The automated test compiles the actual native controller helper and checks simultaneous presses, independent release, opposing movement, analog fallback and keyboard preservation. Physical USB/Android behavior requires testing on the user's hardware.
