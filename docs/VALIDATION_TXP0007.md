# TXP0007 validation

Date: 2026-10-14. 123 automated tests passed: 70 firmware regressions and 53
CHIRP/compiled ARM/TX tests. No COM port, radio upload, flash or physical RF test.

Firmware raw SHA256: `ebc4e61822434f0dac0042a0af6a2c5f2f525469c159f9af37a1510e10f914d5`.
Firmware packed SHA256: `2d2854391be910995ac484ef4de491492a2b621fa9cce7aacf3706a39a60c1b8`.
Driver SHA256: `4d8be7aa9e17a5dc2881a0cda2812afbf659d556ff8652a4f4fd0a2d131193bf`.
Raw: 60,248 bytes; packed: 60,266 bytes; 1,192 FLASH bytes free.

The compiled ARM firmware was executed under Unicorn with EEPROM and peripheral
bus mocks. Tests verify all 200 memory slots in both VFOs, normal PTT and all alarm
states, Spectrum PTT and direct ToggleTX, direct normal TX setup, offset/reverse,
global TX enable/disable, existing band limits, persistence, resaving a blocked
destination, empty-slot stale-marker handling and unchanged RX profile restoration.
Existing NAME, Spectrum/VFO save, SOS, AM AGC, RX-profile and boot/vector tests pass.

The real CHIRP Python core was used, from the official master archive with SHA256
`f0ff4fa70fadfef294ee0b995719699e297224140d96b363a2743be95d537faa`. Native image metadata, five modulations/twelve
steps, all tones/DCS, settings, no-op preservation, protected EEPROM areas,
conflict preflight and readback verification were tested with simulated serial I/O.

The installed CHIRP GUI and real cable timing were not tested. This is experimental.
TX control is per memory and requires TXP0007; older firmware ignores the marker.
The original RXP0006 AM-fix source remains byte-identical.

See TESTE_TXP0007.txt and the complete source validation_chirp/ and tests/ directories.
