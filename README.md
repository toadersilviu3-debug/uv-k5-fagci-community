# UV-K5 FAGCI Community - TXM0008

Independent community firmware based on FAGCI MOD v1.2.1 / DualTachyon.
Latest build: **OSFW-TXM0008**. The owner reported successful operation on their
radio on **15 October 2026**; **135 automated tests** also passed. This remains an
experimental community release for the original DP32G030 source platform.

## Download and instructions

- [TXM0008 release and complete package](https://github.com/toadersilviu3-debug/uv-k5-fagci-community/releases/tag/txm0008-test1)
- [Complete English guide](docs/TXM0008_USER_GUIDE_EN.md) / [PDF](docs/TXM0008_USER_GUIDE_EN.pdf)
- [Romanian TXM0008 instructions](docs/TXM0008_RO.md)
- [All community changes](docs/CHANGES_TXM0008_EN.md) / [development changelog](CHANGELOG.md)
- [Validation and field report](docs/VALIDATION_TXM0008_PUBLIC.md)

The release includes raw and packed firmware, the matching CHIRP Python module,
complete source/dependencies, English MD/PDF help, Romanian help, test logs,
SHA256 checksums, and **official K5Prog Windows v1.26 with corresponding source and GPL license**.
The privately modified IJV K5Prog executable is not redistributed.

## Features added in this community project

- **50 NAME:** view/edit full ten-character memory names without discarding RX profiles.
- **Spectrum Side Key 2:** capture the peak/fixed frequency, choose a destination and explicitly confirm saving.
- **Long Side Key 2 in VFO:** save the accepted/tuned frequency using MEM-CH.
- **AM reception integration:** fixed hardware gain slot with inherited FAGCI software AM-fix; other modes restore hardware AGC.
- **Flashlight SOS:** steady / repeated Morse SOS / off.
- **Optional RX profile:** explicitly save gain/IF from fixed Spectrum listening as RX:MANUAL; AUTO remains default.
- **Per-memory TX permission:** persistent RX-only flag, respected by normal and Spectrum TX paths.
- **51 TX-CH:** on-radio ON/OFF with CH-xxx, MR ONLY and GLOBAL OFF; both matching VFO caches update immediately.
- **CHIRP TXM0008 driver:** correct EEPROM mapping, RX profiles and TX flag, settings, changed-byte upload with conflict checks and readback verification.

Quick TX menu: select a stored transmit memory, **M -> 5 -> 1 -> M**, choose ON/OFF,
then M to save or EXIT to cancel. ON still obeys global limits. The same frequency
in another memory or VFO is independent. Special menus are now 52-57; boot shortcut
remains PTT + Side Key 1.

## Installation and limits

Use firmware_TXM0008.bin with a raw-compatible loader, or the packed file with
a compatible packed loader. Keep each radio's own calibration/configuration
backup. No reset is required when upgrading from this community project's earlier
builds. In CHIRP load chirp/uvk5_fagci_txm0008.py and download a NEW image using
Quansheng / UV-K5 FAGCI TXM0008. Old IJV/TXP0007 tabs are not converted automatically.

Raw: **60,668 bytes**; packed: **60,686 bytes**; free FLASH: **772 bytes**.
TX-CH requires no new EEPROM allocation. Profiles store gain/IF only, not DEV,
CMP, MIC or Spectrum squelch/RSSI. Spectrum 6.25 kHz bandwidth is stored as Narrow.
Old firmware before TXP0007 does not enforce the TX marker. Other processors/board
revisions and third-party CPS tools are not established as compatible.

The field report is one owner's successful use, not exhaustive hardware coverage,
RF certification or measured sensitivity. K5Prog's official binary was checked
for provenance and source, not physically used by the assistant to flash a radio.

## Source and tests

Build with `bash build-firmware.sh` using ARM GCC, make and Python crcmod.
The branch vendors the actual CMSIS_5/printf dependency snapshot used in the build;
see [dependency provenance](docs/DEPENDENCY_PROVENANCE.md). Later toolchain/build
dates can change hashes; release checksums identify the distributed tested binaries.

Run `python -m unittest discover -s tests -v` with Unicorn and the ARM tools
(ARM_BIN defaults to C:/msys64/ucrt64/bin). For validation_chirp tests set
UVK5_FIRMWARE_DIR to this checkout, UVK5_DRIVER to chirp/uvk5_fagci_txm0008.py,
and PYTHONPATH to an official CHIRP checkout plus Unicorn, then run
`python -m unittest discover -s validation_chirp -v`.
The 135 recorded tests are 70 firmware regressions and 65 CHIRP/ARM/TX/menu tests.

## Credits and licenses

Original authors retain their credits and notices. Firmware is Apache-2.0,
printf MIT, CMSIS Apache-2.0; standalone CHIRP and K5Prog have separate GPL notices.
See LICENSE, NOTICE, CREDITS.md, THIRD_PARTY_NOTICES.txt, chirp/COPYING_GPL3.txt,
and tools/k5prog-win/v1.26/LICENSE. K5Prog upstream is OneOfEleven, based on Jacek
Lipkowski's original k5prog. Local changes/documentation used Codex assistance.
This is not an official FAGCI, Egzumer, IJV or Quansheng release; no endorsement is implied.

Report reproducible problems via Issues and discuss ideas in Discussions. Do not
post private EEPROM/calibration/contact backups in public reports.
