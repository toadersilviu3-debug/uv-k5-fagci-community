# TXM0008 - cumulative community changes

Updated 15 October 2026. Base: FAGCI MOD v1.2.1 (4dcc901), with its inherited
DualTachyon and contributor work. This list describes local additions, not authorship
of the complete firmware.

| Build | Addition or improvement |
|---|---|
| NAME001 | On-radio menu 50 NAME: full ten-character ASCII name view/edit; dedicated correct-slot EEPROM writes; cancellation; both VFO name caches updated; six reserved bytes retained. |
| SPC0002 | Side Key 2 Spectrum peak/fixed-frequency capture; first-free destination; separate SAVE?/REPLACE? confirmation; held-key protection; frequency/modulation/step/Wide-Narrow storage; existing names retained. |
| VFO0003 | Long Side Key 2 in VFO opens MEM-CH for the accepted/tuned frequency; preserves ordinary VFO parameters; changing destination resets confirmation; prevents PTT/side-key actions in destination editing. |
| AMH0004 | Explicit fixed hardware gain-slot setup for normal AM plus inherited software AM-fix; automatic hardware gain outside AM; Spectrum AGC restored on exit; original gain controller/table retained. |
| SOS0005 | Flashlight steady/SOS/off cycle; repeated correctly timed Morse SOS; restart at first dot; nonblocking scheduler integration. |
| RXP0006 | Explicit optional AUTO/MANUAL RX profile when saving fixed Spectrum listening; per-memory gain/IF persistence; fixed manual gain without AM-fix override; default restoration on AUTO transitions; LTO/section optimization with interrupt vectors retained. |
| TXP0007 | Dedicated persistent per-memory TX inhibit, compatible CHIRP TX enabled / Duplex off; block cannot be bypassed by global TX enable, reverse/offset, alarm or Spectrum; occupied blocked destinations remain blocked on resave. |
| TXM0008 | Normal menu 51 TX-CH; ON/OFF with CH-xxx, MR ONLY and GLOBAL OFF; target pinning, cancellation, immediate both-VFO cache update; unchanged saves avoid EEPROM writes; full-nibble band validity aligned with firmware in CHIRP. |

## CHIRP module

Standalone model UV-K5 FAGCI TXM0008, gated to OSFW-TXM0008. Maps 200 memories,
twelve steps, FM/NFM/AM/NAM/USB, special BYP/RAW in Extra, tones/DCS, power,
offsets, scan lists, DTMF/scrambling, TX permission, AUTO/MANUAL RX gain and IF.
Also exposes general settings, side keys, messages, 20 FM presets and 16 DTMF contacts.
Unrelated edits preserve profiles and unused data. Upload merges edited bytes into
fresh blocks, preflights conflicts, protects calibration/password/AES and verifies
written blocks. Fresh native-image metadata is required; old IJV images are not
silently interpreted as this model.

## Validation and remaining limits

135 automated tests passed, including compiled ARM execution with mocked EEPROM,
LCD, keyboard and RF-register buses. The owner separately reported successful
TXM0008 use on one radio on 15 October 2026. No measured RF sensitivity claims,
hardware certification or exhaustive compatibility claims follow from that report.

Raw image: 60,668 bytes; packed: 60,686 bytes; free FLASH: 772 bytes. TX-CH uses
the existing TXP0007 marker and needs no new EEPROM allocation. Older firmware
before TXP0007 does not enforce the marker; unsupported external CPS tools can
discard extensions. Spectrum 6.25 kHz is stored as Narrow. DEV/CMP/MIC/squelch/RSSI
are not saved in the optional RX profile.

The unsupported offset-based Duplex off workaround was removed from the older
RXP0006 driver; reliable per-memory TX inhibition requires TXP0007 or TXM0008.
The AM controller/table remains the original FAGCI code; this project changes its
hardware integration and adds optional manual profiles, not a new software gain table.

## Public release packaging

Includes the original tested raw/packed binaries, matching Python module, complete
source and dependencies, English MD/PDF instructions, Romanian instructions,
cumulative changelog, test logs, checksums and original licenses/credits.
Official unmodified OneOfEleven K5Prog Windows v1.26 is included with its exact
upstream source archive and GPL license. The locally modified IJV executable and
the owner's calibration/configuration/channel backups are not redistributed.
