# TXM0008 - User and installation guide

UV-K5 FAGCI Community | OSFW-TXM0008 | 15 October 2026

This independent community build is based on FAGCI MOD v1.2.1 / DualTachyon.
It includes all local additions from NAME001/SPC0002 through TXM0008. It is not
an official FAGCI, Egzumer, IJV or Quansheng release.

The maintainer reported successful operation of TXM0008 on their radio on
15 October 2026. In addition, 135 automated tests passed against compiled ARM
firmware and the CHIRP core with simulated peripherals. These are different
forms of evidence; neither establishes compatibility with every hardware revision
or a measured RF sensitivity improvement.

## 1. Files and compatibility

| File | Purpose |
|---|---|
| firmware_TXM0008.bin | Raw firmware, 60,668 bytes. Use with a raw-compatible loader such as K5Prog. |
| firmware_TXM0008.packed.bin | Packed firmware, 60,686 bytes. Use only with a loader supporting that format. |
| uvk5_fagci_txm0008.py | Standalone CHIRP module for OSFW-TXM0008. |
| TXM0008_complete_package.zip | Firmware, CHIRP module, guides, K5Prog, sources, credits and licenses. |
| sursa_FAGCI_TXM0008_publicare.zip | Complete firmware source, dependencies, CHIRP module and tests; not a radio image. |
| K5Prog-v1.26-official-with-source.zip | Unmodified official OneOfEleven Windows tool, GPL license and corresponding source archive. |
| SHA256_PUBLICARE_TXM0008.txt | Checksums of the published assets. |

This source targets the original DP32G030 platform. Compatibility with GD32/PY32
or other processor/board variants is not established. Check the hardware rather
than relying on a similar model name. No EEPROM reset is required when updating
from the earlier builds of this community project.

Firmware and EEPROM configuration are different: flashing the firmware updates
the program; a CHIRP .img is a backup/configuration image. Keep each radio's own
configuration and calibration. Do not replace them with someone else's dump.

## 2. Install with K5Prog on Windows

The bundle contains official **K5Prog Windows v1.26**, pinned to a published
OneOfEleven source revision, together with its GPL license and corresponding
source. It is not the separately modified IJV executable used by the maintainer.
That local IJV executable was not redistributed because its exact corresponding
source was not established. The included official executable has not been
physically tested with this radio during packaging.

1. Extract the complete package to a local folder. Use the original programming cable.
2. Close CHIRP or other software using the same COM port.
3. For backup, turn the radio on normally. In K5Prog select the cable's COM port and connect.
4. Use **Read Configuration** and **Read Calibration**, keeping the saved files privately.
5. Disconnect in K5Prog and turn the radio off.
6. Hold **PTT** while powering on to enter the firmware-update mode. The flashlight LED lights.
7. Connect in K5Prog using the correct COM port, then choose **Write Firmware**.
8. Select **firmware_TXM0008.bin**. This is the raw firmware, not a source ZIP or CHIRP .img.
9. Wait for completion without interrupting the connection or power. Then switch the radio off and restart normally.
10. Check OSFW-TXM0008 using CHIRP identification or the build information, then check your channels and settings.

Raw and packed files are separate assets; do not rename one to pretend it is
the other. The official K5Prog source describes support for both raw and packed
firmware. The raw file above keeps the flashing workflow used in this project.

K5Prog upstream: https://github.com/OneOfEleven/k5prog-win

## 3. Main menu: the M key

Press M briefly from the main screen. Select a menu with UP/DOWN or its number,
press M to edit, change the value, and press M to accept. EXIT cancels an unsaved
edit; another EXIT closes the menu. MEM-CH, DEL-CH and RESET require an additional
SURE? confirmation. Holding M does not replace a separate confirmation press.

Normal menu numbers 1-50 are retained. TX-CH is the new normal menu 51.

| No. | Display | Function | Values or operation |
|---:|---|---|---|
| 01 | **SQL** | Squelch threshold; 0 keeps reception open. | 0-9 |
| 02 | **STEP** | Tuning step. Changes through this menu are accepted only in VFO mode. | 0.01 / 0.1 / 0.5 / 1 / 2.5 / 5 / 6.25 / 8.33 / 10 / 12.5 / 25 / 100 kHz |
| 03 | **TXP** | Transmit power for the active VFO/channel. | LOW / MID / HIGH |
| 04 | **R_DCS** | Receive DCS code. | OFF or normal/inverted DCS code |
| 05 | **R_CTCS** | Receive CTCSS tone. | OFF or one of 50 tones |
| 06 | **T_DCS** | Transmit DCS code. | OFF or normal/inverted DCS code |
| 07 | **T_CTCS** | Transmit CTCSS tone. | OFF or one of 50 tones |
| 08 | **SFT-D** | Transmit frequency offset direction. | OFF / + / - |
| 09 | **OFFSET** | RX-TX frequency offset, displayed in MHz. | Number keys or arrow keys |
| 10 | **W/N** | Channel filter bandwidth. | WIDE / NARROW |
| 11 | **SCR** | Channel scrambling, intended for FM. | OFF / 1-10; also depends on SCREN |
| 12 | **BCL** | Blocks transmission when the channel is busy. | OFF / ON |
| 13 | **MEM-CH** | Stores the current parameters in the selected memory slot. Requires SURE? confirmation. | CH-001 to CH-200 |
| 14 | **SAVE** | Battery saving. SAVE here does not store a channel. | OFF / 1:1 / 1:2 / 1:3 / 1:4 |
| 15 | **VOX** | Voice-activated transmission and trigger level. | OFF / 1-10 |
| 16 | **BACKLI** | Display backlight duration. | OFF / 5 sec / 10 sec / 20 sec / 1 min / 2 min / ON |
| 17 | **DW** | Dual Watch: monitors both VFOs, with the associated A/B selection. | OFF / CHAN_A / CHAN_B |
| 18 | **WX** | Routes reception and transmission between VFOs A/B. In this source, it is the cross-band setting, although the display says WX. | OFF / CHAN_A / CHAN_B |
| 19 | **BEEP** | Keypad sounds. | OFF / ON |
| 20 | **TOT** | Maximum duration of a transmission. | OFF / 1-10 min |
| 21 | **VOICE** | Inherited voice announcement language selector. This source does not implement voice playback linked to this setting. | OFF / CHI / ENG |
| 22 | **SC-REV** | Scan behavior when a signal is detected: timed resume, resume after the carrier disappears, or stop. | TO / CO / SE |
| 23 | **MDF** | Memory channel display format. | FREQ / CHAN / NAME / NAME+F |
| 24 | **AUTOLK** | Automatic keypad lock. | OFF / ON |
| 25 | **S-ADD1** | Includes the channel in scan list 1. | OFF / ON |
| 26 | **S-ADD2** | Includes the channel in scan list 2. | OFF / ON |
| 27 | **STE** | Squelch tail elimination, where applicable. | OFF / ON |
| 28 | **RP-STE** | Repeater tail elimination delay. | OFF / 1-10 x 100 ms |
| 29 | **MIC** | Transmit microphone sensitivity. | 0-4 |
| 30 | **1-CALL** | One-touch call channel, subsequently accessed with F → 9. | CH-001 to CH-200 |
| 31 | **S-LIST** | Default memory channel scan list. | LIST1 / LIST2 |
| 32 | **SLIST1** | Views list 1 and its priority channels. Does not edit priorities. | Channels in the list / NULL |
| 33 | **SLIST2** | Views list 2 and its priority channels. Does not edit priorities. | Channels in the list / NULL |
| 34 | **ANI-ID** | Displays your own DTMF identifier. Cannot be edited here. | View only |
| 35 | **UPCODE** | Displays the DTMF code sent at the beginning of transmission. Cannot be edited here. | View only |
| 36 | **DWCODE** | Displays the DTMF code sent at the end of transmission. Cannot be edited here. | View only |
| 37 | **D-ST** | Local monitoring of DTMF tones. | OFF / ON |
| 38 | **D-RSP** | Response to a decoded DTMF call. | NULL / RING / REPLY / BOTH |
| 39 | **D-HOLD** | DTMF call hold/automatic reset time. | 5-60 sec |
| 40 | **D-PRE** | Delay before sending the DTMF code. | 3-99 x 10 ms |
| 41 | **PTT-ID** | When the DTMF identifier is sent during PTT operation. | OFF / BOT at start / EOT at end / BOTH |
| 42 | **D-DCD** | Enables DTMF decoding on the channel. | OFF / ON |
| 43 | **D-LIST** | Selects a DTMF contact. Confirming a valid contact prepares it for a call. | 1-16 / NULL for an invalid entry |
| 44 | **PONMSG** | Startup screen: full display, message, or battery voltage. | FULL / MSG / VOL |
| 45 | **ROGER** | End-of-transmission signal. | OFF / ROGER / MDC |
| 46 | **VOL** | Displays battery voltage. VOL in this menu is not a volume adjustment. | View only, in volts |
| 47 | **MODUL** | Basic modulation selector in the main menu. | OFF = FM / ON = AM; see modulation notes |
| 48 | **DEL-CH** | Deletes the selected channel from usable memory. Requires SURE? confirmation. | CH-001 to CH-200 |
| 49 | **RESET** | Resets settings or performs a full reset. Requires SURE? confirmation and restarts the radio. | VFO / ALL |
| 50 | **NAME** | Views and edits the active memory channel name. | Up to 10 ASCII characters; see steps below |
| 51 | **TX-CH** | Persistent TX permission for the selected stored memory. | OFF = RX-only / ON = allowed subject to global limits |

## 4. Edit a channel name: menu 50 NAME

Select an existing memory channel, then press M, 5, 0, M. The screen identifies
the channel and shows the full name, independently of the MDF display setting.

| Key | Action in NAME |
|---|---|
| UP / DOWN | Change the current character; hold to repeat. |
| F | Move the cursor right. |
| * | Move the cursor left. |
| 0-9 | Insert that digit and advance. |
| M | Save and leave editing. |
| EXIT | Cancel the unsaved changes. |

Names use up to ten printable ASCII characters. Replace trailing characters
with spaces to shorten a name; ten spaces clear it. NAME displays MR ONLY outside
a valid memory. It updates only the name, preserving the RX profile and TX flag.

## 5. Save a frequency from VFO

Enter or tune the frequency. If you typed it manually, accept the frequency with
M first. **Hold Side Key 2** in VFO to open MEM-CH at the first free memory slot.
Select CH-001 through CH-200, press M for SURE?, then press M again to save.
EXIT cancels. Changing the destination invalidates the previous confirmation.

Side Key 2 is the lower small side button. Its short action remains configurable;
long-press VFO saving takes priority in VFO. Outside VFO, the configured long action
remains available. Ordinary VFO parameters are saved through the existing memory
serializer. An occupied destination is overwritten, with its existing TX block retained.

The ordinary menu route remains M -> 13 MEM-CH -> M -> destination -> M -> SURE? -> M.
Menu 14 SAVE is battery saving, not channel storage. Some ordinary changes made
while viewing an MR channel need an explicit MEM-CH save to persist. NAME, TX-CH
and scan-list participation have their own persistence paths.

## 6. Spectrum: enter, listen and save

From the main screen press F, release it, then 5. Pressing PTT briefly on the
graph enters fixed listening on the detected peak; release PTT. A later PTT press
in fixed listening can transmit if the current transmit memory and global limits
permit it. PTT is not the save button.

Press and release **Side Key 2** to open memory saving. From the graph, the peak
frequency is captured; from fixed listening, the tuned frequency is captured.
The first free slot is proposed. Choose a destination with UP/DOWN, press M for
SAVE? or REPLACE?, then press M again to save. EXIT cancels from either stage.
Changing the slot invalidates confirmation; held M cannot overwrite automatically.
PTT is ignored in this save screen. Select the saved memory after leaving Spectrum.

Frequency, modulation, tuning step and Wide/Narrow filter are saved. A Spectrum
6.25 kHz filter is stored as Narrow because the channel format has only two
bandwidth states. The new Spectrum memory has no tones or repeater offset, uses
the active VFO's power, and belongs to both scan lists. An existing name and TX
block are retained when overwriting an occupied slot; a new slot starts with a blank name.

In fixed listening, M cycles through LNAs, LNA, PGA, MIX, IF, DEV, CMP and MIC;
UP/DOWN adjusts the selected register. EXIT first leaves register selection, then
returns to the graph; EXIT from the graph leaves Spectrum. Key 0 cycles modulation.

## 7. Optional saved RX profile

Spectrum saving starts at **RX:AUTO**. While saving from **fixed listening only**,
press **F** to choose RX:MANUAL; F toggles AUTO/MANUAL. The gain and IF values were
captured when saving opened. Changing this mode or destination requires a new
confirmation. From the scanning graph only AUTO is available.

- AUTO keeps normal operation, including the automatic AM controller.
- MANUAL stores the LNAs/LNA/MIX/PGA gain register and the IF register for that memory.
- MANUAL restores fixed gain on memory selection and restart; the AM controller does not override it.
- Resave the same slot as AUTO to remove its manual profile. NAME and TX-CH preserve the profile.
- DEV, CMP, MIC and the Spectrum squelch/RSSI threshold are not saved in the RX profile.

The profile uses the six reserved bytes after the ten-character name; it does
not shorten the name. AUTO remains the default, particularly for changing aircraft
signal levels. Fixed gain is an explicit option and does not guarantee improved reception.

## 8. Per-channel transmit control: menu 51 TX-CH

Select the stored channel used for TX, then press **M -> 5 -> 1 -> M**. Choose
OFF for RX-only or ON to permit TX subject to global limits. M saves immediately;
EXIT cancels. CH-xxx identifies the destination. Matching caches in both VFOs
update immediately, and the flag persists after restart.

GLOBAL OFF means the global ALL_TX setting is DISABLE; selecting ON does not
override it. MR ONLY means no valid stored memory is selected. This is a per-memory
flag, not a frequency blacklist: the same frequency entered in VFO or another
memory is independent. In Cross-band, the actual transmit memory determines the flag.

PTT, both side keys and F are ignored inside this editor. The destination is pinned
on entry. Saving the same choice does not write EEPROM again. Only the eight-byte
block containing the existing TX marker is written; no new EEPROM space is allocated.

Normal PTT, alarm/1750-Hz paths and Spectrum respect the block. Spectrum/VFO
overwrites of an occupied blocked slot keep it blocked. Explicit TX-CH ON or
CHIRP TX enabled clears the block. Deleting and recreating a memory resets its
old properties. Firmware older than TXP0007 does not enforce this marker.

## 9. CHIRP: load the correct module

1. Save any existing unsaved CHIRP work.
2. Choose File -> Load Module and open uvk5_fagci_txm0008.py.
3. If that menu is missing, enable Help -> Developer Mode, restart, and load the module.
4. Choose Radio -> Download From Radio with your cable port, vendor Quansheng and model UV-K5 FAGCI TXM0008.
5. Keep the radio in normal mode, outside Spectrum. Save the new .img as your original backup.
6. Edit the new image, save it, and use Radio -> Upload To Radio with the same model.

An old IJV/TXP0007 tab is not converted by loading the new module. The driver
accepts OSFW-TXM0008 exactly and requires its own download baseline before upload.

The table exposes frequency, name, FM/NFM/AM/NAM/USB, actual tuning step, tones,
power and offset. NAM means narrow AM. Open the channel properties and **Extra**
for TX enabled, bandwidth, scan lists, DTMF options, scrambling and the RX profile.
Disabled TX is also represented as Duplex off. Rechecking TX enabled restores
the stored offset/direction instead of replacing it with a fake offset.

MANUAL gain fields are LNAs/LNA/MIX/PGA indices and IF as a decimal register value.
For AUTO memories they are proposed defaults for creating a manual profile, not
live AGC measurements. BYP/RAW are selected in Extra; CHIRP represents them as FM/NFM
in the main Mode column. Unrelated edits preserve these special modulations.

Settings include radio/side-key/scan options, startup messages, DTMF codes,
20 broadcast-FM presets and 16 contacts. Calibration, password and AES-key upload
are protected. The fourteen internal VFO slots and unsaved Spectrum registers
are not editable. Only edited bytes are merged into current EEPROM blocks;
all conflicts are checked before writing, and written blocks are reread for verification.
After changing a setting directly on the radio, download again before editing
that same value in CHIRP. Keep native .img backups privately.

## 10. AM reception and the SOS flashlight

For normal AM reception, the firmware explicitly selects the fixed hardware gain
slot while the inherited FAGCI software AM controller adjusts gain. Other normal
modes use hardware automatic gain; Spectrum uses hardware AGC and restores it on exit.
The FAGCI gain table/controller source was not replaced with Egzumer's. The owner
reported improved AM reception during earlier testing; no laboratory sensitivity,
dynamic-range or audio-quality figures are claimed.

The flashlight action cycles **steady -> repeated SOS -> off**. SOS is three dots,
three dashes, three dots, then a pause. It restarts at the first dot when reactivated.
The nominal Morse unit is 160 ms, with a 5.44-second complete cycle. Scheduling
can affect real timings. As with the old blinking function, the separate Spectrum
loop pauses the sequence until Spectrum exits. RX/TX status LEDs are unchanged.

## 11. Special menus 52-57

Power on while holding **PTT + Side Key 1**, the upper small button immediately
below PTT. Release the buttons when the special menu appears. These settings are
TX permissions and global scrambling, not AM sensitivity controls.

| No. | Display | Function | Values |
|---:|---|---|---|
| 52 | 350TX | Configured 350 MHz TX permission. | OFF / ON |
| 53 | F-LOCK | Transmit band-limit profile. | OFF / FCC / CE / GB / LPD PMR |
| 54 | 200TX | Configured 200 MHz TX permission. | OFF / ON |
| 55 | 500TX | Configured 500 MHz TX permission. | OFF / ON |
| 56 | ALL_TX | Global transmission mode. | DEFAULT / ENABLE / DISABLE |
| 57 | SCREN | Global scrambling permission. | OFF / ON |

Use transmit functions only where you are authorized. No global permission is
changed automatically by this firmware update or by TX-CH.

## 12. Limitations and validation

Menu 47 MODUL selects only FM/AM. The five stored modulations can be cycled with
F then 7, or key 0 in Spectrum. Ordinary MR parameter changes may need MEM-CH.
STEP changes through the normal menu apply only in VFO; CHIRP can edit a memory's
stored step. Voice playback is not implemented by the inherited VOICE setting.

Raw firmware occupies 60,668 of 61,440 FLASH bytes; 772 bytes remain. Packed size
is 60,686 bytes. Memory fullness does not by itself slow menu navigation. TX-CH
reuses the existing EEPROM marker and avoids unchanged writes.

135 automated tests passed: 70 firmware regressions and 65 CHIRP/ARM/TX/menu tests.
The owner separately confirmed successful TXM0008 operation on 15 October 2026.
Exact board revision and exhaustive per-feature/hardware coverage were not provided.
The packaged official K5Prog v1.26 was checked for provenance, version, license
and matching source archive; it was not executed or used to flash a radio by the assistant.

## 13. Source, credits and licenses

Build the complete source with bash build-firmware.sh using ARM GCC and Python
crcmod. The actual CMSIS_5/printf dependency snapshot is included. Earlier missing
dependencies were recovered from the local Egzumer 0.22 archive; see dependency
provenance and retained license notices. Build dates/toolchains may change hashes.
Published SHA256 values identify the distributed binaries.

Base projects: FAGCI, DualTachyon; AM-fix contributors include OneOfEleven.
Egzumer 0.22 was used as a comparison reference and dependency archive. CMSIS
remains attributed to ARM; printf to Marco Paland and contributors.
CHIRP transport credits: Jacek Lipkowski and Dan Smith; the supplied IJV adaptation
also credits Julian Lilov LZ1JDL and Francesco IK8JHL. K5Prog Windows is by
OneOfEleven, based on Jacek Lipkowski's original k5prog.

Firmware: Apache-2.0 with dependency notices. CHIRP module and K5Prog: their
included GPL notices and source apply separately. Local development and
documentation were prepared with Codex assistance. Original authors are credited;
no endorsement by upstream projects or Quansheng is implied.
