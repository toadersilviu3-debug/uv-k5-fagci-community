# TXM0008 - complete community testing package

This experimental community release brings all changes since SPC0002 together:
VFO long-SK2 saving, AM hardware/software AGC integration, SOS flashlight, optional
saved RX gain/IF profiles, dedicated per-memory TX inhibition, and the on-radio
51 TX-CH menu. Existing NAME editing and Spectrum saving remain available.

The owner reported successful TXM0008 operation on 15 October 2026. 135 automated
tests passed separately; RF sensitivity and wider board compatibility are not certified.

## Downloads

- TXM0008_complete_package.zip: start here; firmware, matching CHIRP module, full
  English MD/PDF guide, Romanian instructions, sources, K5Prog, licenses and checksums.
- firmware_TXM0008.bin: raw firmware (60,668 bytes).
- firmware_TXM0008.packed.bin: packed firmware (60,686 bytes).
- uvk5_fagci_txm0008.py: Quansheng / UV-K5 FAGCI TXM0008 CHIRP module.
- TXM0008_USER_GUIDE_EN.pdf and .md: complete current menu/install/use guide.
- sursa_FAGCI_TXM0008_publicare.zip: complete firmware/CHIRP source and dependencies.
- K5Prog-v1.26-official-with-source.zip: official unmodified Windows tool, GPL and corresponding source.
- SHA256_PUBLICARE_TXM0008.txt: checksums for these assets.

## Quick start

Keep your own configuration/calibration backup. Flash the raw binary with K5Prog
or another raw-compatible loader; use the packed file only with a compatible loader.
No EEPROM reset is required for an update from this community project's earlier builds.
For CHIRP, load the new module and download a new image using the TXM0008 model.
On radio: select a memory, M -> 5 -> 1 -> M, choose ON/OFF, M to save or EXIT to cancel.
ON still obeys global TX limits; GLOBAL OFF means ALL_TX is disabled.

## Compatibility and attribution

Targets the original DP32G030 source platform. Other processors/board revisions
are not established as compatible. TX blocking is per stored memory, not a global
frequency blacklist; old firmware before TXP0007 does not enforce it.
Spectrum profiles save gain/IF only, and 6.25 kHz bandwidth is represented as Narrow.

Firmware is based on FAGCI/DualTachyon and retains contributor/dependency notices.
CHIRP and K5Prog have separate GPL licenses, included with sources. The K5Prog
binary is the official v1.26 snapshot, not the maintainer's modified IJV executable.
Independent community release with Codex assistance; no upstream endorsement implied.
Please report reproducible results via Issues and use Discussions for general feedback.
Do not publish private EEPROM/calibration/contact dumps.
