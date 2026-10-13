# Changelog

## SPC0002 - experimental community prerelease

Based on FAGCI MOD v1.2.1 (4dcc901). Firmware identifier: OSFW-SPC0002.

### Added

- Menu 50 NAME: view/edit up to ten ASCII characters for the active memory channel. EXIT cancels; MENU saves only the name.
- Spectrum Side Key 2: capture the displayed peak or the fixed listening frequency, select memory slot 001-200, and require two distinct MENU presses before writing.
- Separate SAVE? / REPLACE? confirmation, cancellation, held-key protection, and saved-slot feedback.
- Preserve frequency, modulation, step, and Wide/Narrow when capturing a Spectrum channel.
- Automated ARM execution tests, Romanian help, and build/packaging instructions.

### Behavioral changes

- Side Key 2 in Spectrum opens channel saving instead of toggling the backlight. Its behavior outside Spectrum is unchanged.
- Existing normal menu entries 01-49 retain their numbers. NAME is 50; special menu entries become 51-56.

### Unchanged or not implemented

- AM-fix is unchanged from the original local FAGCI archive. The Egzumer comparison did not introduce an AM reception fix.
- Special receiver-register settings and Spectrum RSSI threshold are not saved per channel.
- Spectrum 6.25 kHz bandwidth is represented as Narrow in the existing memory format.

### Files modified

- `app/menu.c`: Added NAME editing, cancellation, and dedicated name-only persistence.
- `app/menu.h`: Added declarations for the NAME editor state.
- `ui/menu.c`: Added NAME menu entry and ten-character editor display.
- `ui/menu.h`: Added NAME and a symbolic menu count.
- `main.c`: Updated normal menu count to include NAME.
- `helper/boot.c`: Updated special menu count after adding NAME.
- `settings.c`: Added name-only EEPROM persistence preserving six reserved slot bytes.
- `settings.h`: Declared the name-only persistence function.
- `app/spectrum.c`: Added Side Key 2 channel capture, slot selection, confirmation, and saving.
- `app/spectrum.h`: Added the Spectrum channel-save state.

Original file headers are preserved. Each modified inherited file carries a prominent local-change notice.
