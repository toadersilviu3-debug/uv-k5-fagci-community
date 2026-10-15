# RXP0006 EEPROM RX profile format

Each MR channel uses its existing 16-byte name slot at 0x0F50 + 16 * internal_channel (0..199).

- Bytes 0..9: original ten-character name.
- Bytes 10..11: little-endian REG_13 gain fields, bits 9..0 only (LNAs/LNA/MIX/PGA).
- Bytes 12..13: little-endian REG_3D IF value.
- Bytes 14..15: marker 0x52, 0x58 (ASCII RX).

A manual profile is accepted only for a valid MR channel, matching marker, and gain <= 0x03FF. Missing or malformed profiles use AUTO. VFOs have no persistent manual profile.

AUTO save invalidates a matching marker by setting bytes 14..15 to FF; other unused bytes are retained. MANUAL save updates bytes 10..15 through an 8-byte read/modify/write at slot+8, preserving the final two name bytes. NAME uses its existing path and preserves all six profile bytes. Existing invalid/unmarked reserved data is not treated as a profile.

No EEPROM migration or reset is needed. External tools do not necessarily preserve or understand these reserved bytes. Normal saving with this firmware manages them explicitly; old firmware may retain stale profiles when overwriting channel data. Re-save as AUTO when a profile should be removed.
