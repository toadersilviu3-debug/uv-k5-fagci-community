# VFO0003 - long Side Key 2 VFO memory-save shortcut

Experimental OSFW-VFO0003 build based on SPC0002. Not yet field-tested or published on GitHub.

1. Select VFO mode (F, then 3 if currently in MR mode).
2. Enter the frequency and press M to accept it. Check the tuned frequency; normal VFO tuning-step alignment applies.
3. Hold Side Key 2 (lower side button) for about 1.3 seconds. The shortcut opens menu 13 MEM-CH directly in destination selection.
4. Release Side Key 2. The first free slot is suggested, or CH-001 if all slots are occupied.
5. Select a slot with the arrow keys or three digits (025 selects CH-025).
6. Press M for SURE?, then press M again to save. An occupied slot will be overwritten.
7. EXIT cancels destination editing; another EXIT returns to the main screen. After saving, EXIT leaves MEM-CH. Select the saved slot in MR to use it or rename it with menu 50 NAME.

Changing the destination invalidates confirmation. Holding M cannot automatically confirm the save. PTT and side keys are ignored while editing/confirming a MEM-CH destination.

Short SK2 retains its configured action. Long SK2 is reserved for saving in VFO mode, overriding its previously configured long action there. The configured long action remains available in MR and other screens. Spectrum saving is unchanged.

Accept an unfinished frequency entry with M before using the shortcut; otherwise the save is rejected rather than capturing the old frequency. The shortcut is blocked while the keypad is locked or scanning is active.

The existing MEM-CH path stores the active VFO's RX frequency, offset/direction, RX/TX tones/codes, modulation, step, bandwidth, power, BCL, reverse, DTMF, scrambling and scan-list membership. Existing destination names are retained. Special receiver-register adjustments and global squelch are not added to channel storage.

The raw firmware is 61,264 bytes, leaving 176 bytes within the 61,440-byte flash limit. Built with ARM GCC 16.1.0. All 38 ARM-emulation tests passed (13 NAME, 14 Spectrum, 11 VFO), including all 200 destinations and 180 Spectrum mode/bandwidth/step combinations. Peripherals are simulated; hardware and RF validation remain pending.

Choose the raw or packed file according to your loader. Keep your own configuration/calibration backups. No reset is required. AM AGC is unchanged. This source retains the Apache-2.0 and third-party license notices of SPC0002.
