# M Key Guide for FAGCI SPC0002

This guide describes **OSFW-SPC0002**, the latest firmware build generated for this project. The Romanian original was checked against the firmware source on October 13, 2026. This version includes the NAME editor and Spectrum saving with Side Key 2. The AM comparison with Egzumer did not change the firmware.

## Using the main menu

1. From the main screen, briefly press **M / MENU**.
2. Select an option with **▲/▼**, or enter its number. For example, press **5 then 0** to select NAME.
3. Press **M** to enter the setting.
4. Change the value with the arrow keys or, where supported, the number keys.
5. Press **M** to accept. **EXIT** cancels editing; press EXIT again to close the menu.

MEM-CH, DEL-CH and RESET require an additional confirmation: after selecting the value, press M to display **SURE?**, then press M again to perform the operation.

## Normal menu: options 01-50

The numbers and labels below are those displayed by SPC0002. Options 01-49 retain their original numbering; NAME is the new option 50.

| No. | Display | Function | Values or usage |
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

## Editing a channel name

First select a memory channel, then use **M → 50 NAME → M**. The screen shows the channel number and full name, regardless of the MDF setting.

| Key in the NAME editor | Action |
|---|---|
| ▲ / ▼ | Changes the character under the cursor; holding the key repeats the change. |
| F | Moves the cursor right. |
| * | Moves the cursor left. |
| 0-9 | Inserts the digit directly and advances the cursor. |
| M | Saves the name and finishes editing. |
| EXIT | Discards the changes. |

Names can contain up to **10 characters**, without accented letters. The cursor wraps around at either end. To shorten a name, replace its final characters with spaces; ten spaces clear the name. NAME does not create channels and displays **MR ONLY** unless a valid memory channel is selected.

## Saving a channel from the main menu

Set the frequency and parameters, then follow:

**M → 13 MEM-CH → M → select CH-xxx → M → SURE? → M**

Check the slot number before the final confirmation. An occupied slot will be overwritten. **14 SAVE** is battery saving and does not replace MEM-CH.

In SPC0002, ordinary parameter changes, such as TXP, tones or MODUL, automatically save the VFO settings but do not rewrite the parameters of an existing MR channel. To retain these changes in a memory channel, explicitly use **MEM-CH** afterwards. The NAME editor and S-ADD1/S-ADD2 scan list membership have their own save paths.

## Available modulation modes

Option **47 MODUL** offers only **OFF = FM** and **ON = AM**, even though its title suggests a general selector. Accepting this option on a USB/BYP/RAW channel selects FM or AM.

Cycle through the five modes **FM, AM, USB/SSB, BYP, RAW** with **F → 7** from the main screen, or **0** in Spectrum. To retain a mode change in an MR channel, use MEM-CH or Spectrum saving.

## What M does in Spectrum

Enter Spectrum from the main screen: press **F**, release it, then press **5**. The function of M depends on the current screen:

| Screen | What M does |
|---|---|
| Spectrum graph | Does not open the main menu or a help screen. The extended register menu on this screen is disabled in SPC0002. |
| Frequency entry, after pressing 5 | Accepts the entered frequency and returns to the previous Spectrum/listening state. |
| Spectrum fixed-frequency listening | Cycles through LNAs, LNA, PGA, MIX, IF, DEV, CMP and MIC adjustments. The arrow keys change the selected setting. |
| Slot selection after Side Key 2 | The first press requests confirmation; the second saves. |

To switch from the graph to fixed-frequency listening on the detected peak, briefly press PTT and release it. **During fixed-frequency listening, another PTT press may start transmission**; PTT is not the save button.

During fixed-frequency listening, EXIT first closes the adjustment selection, if active; the next EXIT returns to the graph. From the graph, EXIT closes Spectrum.

Special adjustments are temporary. In SPC0002, Side Key 2 **does not save** LNAs/LNA/PGA/MIX/IF/DEV/CMP/MIC settings or the squelch/RSSI threshold.

## Saving from Spectrum with Side Key 2

1. Press and release **Side Key 2**, the lower side button. In Spectrum, this replaces its backlight toggle function.
2. Check the displayed frequency. The captured frequency is the graph peak frequency, or the tuned frequency during fixed-frequency listening.
3. The first free slot is suggested. Use **▲/▼** to select a different slot if needed.
4. Press and release **M**: **SAVE?** appears for an empty slot, or **REPLACE?** for an occupied slot.
5. Press **M** again to save. **SAVED CH-xxx** appears, then you return to Spectrum.

EXIT cancels at either stage. Changing the slot cancels the previous confirmation. Holding M cannot automatically confirm an overwrite. PTT is ignored on this screen.

The frequency, modulation, tuning step and Wide/Narrow bandwidth are saved. The Spectrum 6.25 kHz filter is stored as Narrow. The channel is created without an offset or tones, using the active VFO's transmit power and membership in both scan lists. When overwriting, the existing name is preserved; a new slot has an empty name that can later be edited with NAME.

Saving does not automatically select the new channel on the main screen. After leaving Spectrum, select the saved slot to use or rename it.

## Special options 51-56

These options appear in the special mode accessed by powering on the radio while holding **PTT + Side Key 1** simultaneously. Side Key 1 is the small button immediately below PTT. Release both buttons when menu **51 - 350TX** appears. They configure transmission permissions and global scrambling; they are not AERO sensitivity or AM AGC adjustments.

| No. | Display | Function | Values |
|---:|---|---|---|
| 51 | **350TX** | Configured permission to transmit in the 350 MHz range. | OFF / ON |
| 52 | **F-LOCK** | Transmit frequency limit profile. | OFF / FCC / CE / GB / LPD PMR |
| 53 | **200TX** | Configured permission to transmit in the 200 MHz range. | OFF / ON |
| 54 | **500TX** | Configured permission to transmit in the 500 MHz range. | OFF / ON |
| 55 | **ALL_TX** | General transmission permission mode. | DEFAULT / ENABLE / DISABLE |
| 56 | **SCREN** | Global scrambling enable. | OFF / ON |

## Quick reference

- **13 MEM-CH:** saves a channel.
- **14 SAVE:** battery saving.
- **23 MDF:** name or frequency display.
- **46 VOL:** battery voltage.
- **47 MODUL:** FM/AM only in the main menu.
- **48 DEL-CH:** deletes a channel.
- **49 RESET:** reset; not required to enable the new features.
- **50 NAME:** edits a channel name.
- **F → 5:** Spectrum.
- **Side Key 2 in Spectrum:** selects a slot for saving.

This is an external guide for the existing version. Creating this document did not add a HELP screen to the firmware or change the behavior of the M key.

