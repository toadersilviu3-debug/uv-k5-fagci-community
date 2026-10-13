# UV-K5 FAGCI community extensions - SPC0002

An independent experimental community fork based on **FAGCI MOD v1.2.1 (4dcc901)**. It adds an on-radio channel-name editor and direct Spectrum channel capture. This is not an official FAGCI, Egzumer, or Quansheng release and does not imply endorsement by those authors.

## Features

- **MENU 50 NAME:** edit the active memory channel's ten-character name.
- **F, then 5:** enter Spectrum.
- **Side Key 2 in Spectrum:** choose a slot and confirm saving with two distinct MENU presses; EXIT cancels.
- Existing channel-name bytes, adjacent EEPROM data, and calibration are preserved by the documented write paths.

See [Romanian help](docs/HELP_MENIU_SPC0002.md), [PDF help](docs/HELP_MENIU_SPC0002.pdf), and [change history](CHANGELOG.md).

## Status and compatible hardware

**Experimental / pre-release.** The code targets the DP32G030 architecture of the supplied UV-K5 source. Compatibility with other board revisions or different processors is not established. Do not infer compatibility from a similar product name.

The development record contains a successful owner-reported flash of the earlier NAME001 build. It does not yet establish field validation of SPC0002, every feature, or AM audio quality. Twenty-seven automated tests passed against compiled ARM instructions with simulated peripherals; these are not RF measurements or hardware certification.

## Release files

- `firmware_SPC0002.bin`: raw firmware, 60,928 bytes, for a raw-compatible loader such as the K5Prog setup used during development.
- `firmware_SPC0002.packed.bin`: packed firmware, 60,946 bytes, for a compatible packed-format loader.
- `firmware_SPC0002_release.zip`: both formats, notices, checksums, and help. Keep the two formats distinct.
- `sursa_FAGCI_SPC0002_publicare.zip`: complete source snapshot including the dependencies actually used for the distributed build.

Back up the radio's own configuration and calibration before testing. Preserve the originals. Flash only the firmware for this change; do not upload another radio's calibration. Firmware is provided AS IS under the included licenses. Use transmission functions only where you are authorized to do so.

## Build and reproducibility

The distributed image was compiled using MSYS2 UCRT64, arm-none-eabi GCC 16.1.0, the inherited Makefile options, and Python crcmod. Raw firmware uses 60,928 of the project's 61,440 flash bytes. Run `bash build-firmware.sh` with the ARM tools, make, and a Python environment containing crcmod available.

The original local FAGCI archive had empty dependency directories. The build used CMSIS_5 and printf recovered from the supplied Egzumer 0.22 archive. This is disclosed in [dependency provenance](docs/DEPENDENCY_PROVENANCE.md). The complete release source snapshot contains those files. Do not claim that an unverified clone using the upstream submodule pins reproduces these exact inputs. This branch vendors the actual dependency snapshot directly; the original submodule metadata is archived in docs/upstream.gitmodules.txt.

The firmware embeds compile date/time, so a later rebuild can have a different hash. The release hashes identify the distributed binaries, not a promise of bit-for-bit reproducibility on every compiler or date.

## Tests and known limitations

On Windows, install `tests/requirements.txt` in a Python environment and run `python -m unittest discover -s tests -v` after compiling. The test scripts default to `C:\msys64\ucrt64\bin`; ARM_BIN can override this path. The [test record](docs/TESTE_SPC0002.txt) describes the executed tests.

- Normal menu 47 MODUL offers only FM/AM. Other modes are selected through F then 7 or Spectrum key 0.
- Ordinary menu changes to an existing MR channel may require explicit MEM-CH confirmation to persist; see the help.
- The legacy custom CHIRP module supplied during development approves OSFW-4dcc901 exactly. Its compatibility with OSFW-SPC0002 has not been verified; this release does not claim working CHIRP support.
- Special LNAs/LNA/PGA/MIX/IF and other register adjustments are temporary.
- AM-fix has not been replaced or tuned in this release.

Report the firmware version, board revision, loader, exact steps, expected/actual results, and whether configuration/calibration were restored. Do not attach private EEPROM dumps or other people's channel/contact data to public issues.

## License and credits

The inherited firmware is Apache-2.0. Keep LICENSE, NOTICE, original copyright headers, and third-party licenses with redistributions. printf remains MIT. See [CREDITS.md](CREDITS.md) and THIRD_PARTY_NOTICES.txt. These notices do not imply upstream endorsement.

