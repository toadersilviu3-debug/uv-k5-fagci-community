# SPC0002 - experimental community prerelease

Independent derivative of FAGCI MOD v1.2.1 / 4dcc901. No upstream endorsement is implied.

New: menu 50 NAME for direct channel-name editing; Side Key 2 Spectrum capture with slot selection, explicit overwrite confirmation, and cancellation. The original AM controller is unchanged.

Firmware identifier OSFW-SPC0002. Raw 60,928 bytes; packed 60,946 bytes. These formats are loader-dependent; use the appropriate format.

Validation: complete build with GCC ARM 16.1.0 and 27 ARM-emulation tests passed, including all 200 memory slots and 180 modulation/bandwidth/step combinations. This is software validation with simulated peripherals. SPC0002 field testing has not yet been confirmed in the development record.

Limitations: special receiver-register settings are not persistent; 6.25 kHz becomes Narrow in channel memory; legacy CHIRP module compatibility is unverified; this release does not add an AM/AERO fix. Hardware compatibility is limited to the architecture actually supported by this source.

Assets: raw and packed firmware in firmware_SPC0002_release.zip with licenses/notices/help, separate complete source snapshot, and checksums. Keep the radio's own configuration and calibration backups. Report concrete results in Issues and avoid publishing private EEPROM data.
