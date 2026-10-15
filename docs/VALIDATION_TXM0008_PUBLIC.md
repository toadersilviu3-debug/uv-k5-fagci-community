# TXM0008 validation

2026-10-14: 135 automated tests passed (70 firmware regressions, 65 CHIRP/ARM/TX/menu).
The actual compiled ARM code runs under Unicorn, with EEPROM/register bus mocks.
No COM port was opened and no radio was flashed, uploaded, reset or RF-tested.

- Raw SHA256: `39bc4e57857fe9702d27a645abc7620dc89ac052aabbd3bc5baeab17d0323f33`.
- Packed SHA256: `bed3557dab11a4b0317c67e7f69d167538f870d2dfc24d3ed064733c41298403`.
- Driver SHA256: `8045de1fe0341af5e61e066226207cc20c65c39c61fd4259c01a3eb6b4a40046`.
- Raw 60,668 bytes; packed 60,686 bytes; 772 FLASH bytes free; no new EEPROM bytes.

New tests exercise all 200 destinations, actual M/51/M/arrow/M dispatch, exit
cancellation, unchanged-save write avoidance, channel pinning, held keys, PTT/F/
side-key suppression, VFO/NOAA/invalid-memory rejection, both VFO cache updates,
restart, CHIRP synchronization, and CH-xxx/GLOBAL OFF/MR ONLY LCD glyph rendering.
Full-image comparisons verify only the TX marker changes, with name/RX profile/
other channel data preserved. Existing serial, boot/vector, AM AGC, RX profile,
Spectrum/VFO save, SOS and TX-inhibition tests pass. The AM-fix source is unchanged.

CHIRP core: official master snapshot, archive SHA256
`f0ff4fa70fadfef294ee0b995719699e297224140d96b363a2743be95d537faa`. The user's installed GUI was not exercised.
Full log: TESTE_TXM0008.txt. Test sources: tests/ and validation_chirp/.


## Owner field report - 15 October 2026

The owner reported that the latest TXM0008 firmware works successfully on their
radio. The exact board revision, test matrix and RF measurements were not supplied.
The automated tests above and this field report are separate evidence. No new
radio flash or hardware measurement was performed by the assistant for publication.
The distributed raw/packed binary hashes remain those of the tested TXM0008 build.
