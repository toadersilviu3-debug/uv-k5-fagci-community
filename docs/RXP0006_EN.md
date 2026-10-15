# RXP0006 - optional Spectrum RX profiles

Experimental OSFW-RXP0006, based on SOS0005. Retains AMH0004 AM AGC integration, SOS flashlight, NAME editing, Spectrum saving and long-SK2 VFO saving. Not yet field-tested or published on GitHub.

During fixed-frequency Spectrum listening, SK2 opens channel saving in RX:AUTO by default. Press F to explicitly choose RX:MANUAL; F toggles the choice. Changing the mode or destination invalidates confirmation. Use MENU twice to save, or EXIT to cancel. After leaving Spectrum, select the saved slot in MR mode.

RX:MANUAL stores the captured LNAs/LNA/PGA/MIX gain register and IF register. These are restored on channel selection and restart, with fixed hardware gain and software AM-fix suppressed for that channel. AUTO retains the normal AM software AGC or non-AM hardware AGC behavior, without persisting special gain/IF adjustments. Manual mode is available only from fixed-frequency listening, not the scanning graph.

To adjust before saving, briefly press and release PTT on the detected peak to enter fixed listening, then use MENU and the arrows for register adjustments. Another PTT press in fixed listening can transmit. Captured register values are pinned when SK2 opens saving.

Resave the same slot with RX:AUTO to clear a manual profile. Ordinary MEM-CH saving from an automatic VFO also clears an old manual profile. NAME edits preserve profiles. Manual RX settings are reset to baseline values during normal TX setup and reapplied on RX return.

The profile occupies the six bytes following the ten-character channel name. Other channel data and calibration are preserved in the tested write paths. DEV, CMP, MIC and per-channel squelch/RSSI are not included. CHIRP/CPS/other firmware compatibility for this extension is unverified; external tools may discard or retain unrecognized profile bytes. Older firmware ignores the profile; returning to RXP0006 can reactivate a retained profile.

Raw image: 59,808 bytes of the 61,440-byte limit; 1,632 bytes free. Packed image: 59,826 bytes. ARM GCC 16.1.0, LTO, section garbage collection, explicit KEEP of interrupt vectors, and preserved emulation/peripheral call boundaries. No existing feature was disabled.

All 70 ARM-emulation tests passed: 53 existing, 15 RX profile tests and 2 startup tests. Tests cover all 200 destinations, profile persistence, names, EEPROM boundaries, auto/manual transitions, VFO changes and normal RX/TX transitions. The original FAGCI AM-fix source/table is unchanged. Simulated register behavior is not proof of RF/audio performance or on-radio boot validation.

Keep your own configuration/calibration backups. No reset is required. Choose raw/packed format according to your loader. AUTO remains the default, particularly for changing aircraft signal levels.
