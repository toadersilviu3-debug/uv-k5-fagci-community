# Publication update - 2026-10-15

- Owner separately reported successful TXM0008 operation on their radio.
- Publish the unchanged tested binaries, matching CHIRP driver and complete source.
- Add complete English MD/PDF guide for menus 1-57 and all current features.
- Include official unmodified K5Prog v1.26 with exact upstream source and GPL license.
- No private calibration/configuration/CHIRP backups or local IJV executable included.

# TXM0008 - 2026-10-14

- Add normal menu 51 TX-CH, ON/OFF for the selected transmit memory, with CH-xxx,
  MR ONLY and GLOBAL OFF indications. Existing normal menus retain their numbers.
- Pin the target on entry; M saves, EXIT cancels. Ignore PTT, side keys and F in
  the editor. Update both matching VFO caches immediately.
- Reuse TXP0007 EEPROM encoding. Only write the containing 8-byte block when the
  flag changes; preserve RX profiles, names, offsets, calibration and other channels.
- Update CHIRP model/version gate; align memory validity with firmware's full
  four-bit band field (0..6 valid), preserving the reserved upper bits.
- 135 automated tests passed: 70 firmware regressions plus 65 driver/ARM/TX/menu.
- Raw 60,668 bytes, packed 60,686, free FLASH 772 bytes. No new EEPROM allocation.
- No hardware flashing or physical radio test was performed.

# TXP0007 - 2026-10-14

- Add a persistent per-memory TX-inhibit flag and explicit CHIRP TX enabled control.
- Preserve RX, repeater offset/direction, scrambling and the six-byte RX profile.
- Block normal PTT, alarm/1750-Hz paths, direct TX setup and Spectrum TX regardless
  of global TX enable. TX enabled still obeys the existing global limits.
- Preserve an occupied destination's TX block when saving from VFO or Spectrum.
- Legacy valid scrambling values 0..10 and unset 0xFF keep the original behavior.
- EEPROM channel byte 15: high nibble 0xA indicates TX inhibited; low nibble is
  scrambling index. Normal enabled channels retain legacy 0..10 encoding.
- 70 firmware regression and 53 CHIRP/compiled-ARM/TX tests passed (123 total).
- Raw 60,248 bytes; packed 60,266 bytes; 1,192 FLASH bytes free. No physical radio
  test was performed. Downgrading to older firmware does not enforce the flag.

# RXP0006 - 2026-10-14

- Explicit RX:AUTO/RX:MANUAL when saving from Spectrum fixed listening; default AUTO.
- Persist gain and IF in six reserved bytes per channel; restore on MR selection and restart.
- Prevent AM-fix from overriding manual channels; restore defaults on AUTO transitions and normal TX.
- Preserve names, legacy channel data, calibration, existing features and original AM-fix table.
- LTO/section optimization with explicit vector retention and testable bus/function boundaries.
- 70 ARM-emulation tests passed; 59,808-byte raw image, 1,632 bytes free; hardware validation pending.

# SOS0005 - 2026-10-14

- Replace rhythmic flashlight blinking with repeated Morse SOS. Preserve steady/SOS/OFF cycle.
- Restart at the first dot when SOS is reactivated. Use the existing 160 ms scheduler cadence.
- Keep AMH0004 AM AGC, channel-name editing and Spectrum/VFO memory saving.
- All 53 ARM-emulation tests passed; 36 flash bytes remain. Physical validation pending.

# AMH0004 - 2026-10-14

- Set fixed BK4819 gain-table slot 3 for normal AM RX and automatic AGC outside AM. Preserve REG_7E bits 11:0.
- Spectrum uses automatic AGC and restores the prior register mode on exit.
- Keep original FAGCI AM-fix controller/table byte-identical; no sensitivity or audio improvement is yet claimed.
- All 47 ARM-emulation tests passed; field comparison is pending.

# VFO0003 - 2026-10-14

- Long SK2 in VFO opens MEM-CH at the first free slot. Accept typed frequency with M first.
- Preserve ordinary VFO channel parameters using the existing save path.
- Changing destination resets confirmation. Suppress PTT/side-key actions while editing a MEM-CH destination.
- Keep short SK2 and configured long SK2 outside VFO. AM AGC unchanged.
- 38 ARM-emulation tests passed; physical-radio validation pending.
- Correct special-menu documentation to PTT + Side Key 1 at power-on.

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
