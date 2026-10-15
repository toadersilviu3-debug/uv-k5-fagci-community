# Credits and provenance

- Base firmware: [fagci/uv-k5-firmware-fagci-mod](https://github.com/fagci/uv-k5-firmware-fagci-mod), tag v1.2.1, commit prefix 4dcc901.
- Original firmware reimplementation: [DualTachyon/uv-k5-firmware](https://github.com/DualTachyon/uv-k5-firmware), credited in the inherited README and source.
- AM-fix and other upstream contributions: OneOfEleven and the contributors named in the preserved file headers and original README.
- Comparison/reference project: [egzumer/uv-k5-firmware-custom](https://github.com/egzumer/uv-k5-firmware-custom), local 0.22 archive. Missing third-party dependencies were recovered from that archive; this does not transfer authorship of CMSIS or printf to this fork or to Egzumer.
- CMSIS_5: ARM and its contributors, Apache-2.0, with original notices retained.
- printf: Marco Paland and contributors, MIT; the license is retained in external/printf/LICENSE and THIRD_PARTY_NOTICES.txt.

This is a non-exhaustive credit summary. All original source and dependency notices are retained and remain authoritative. The maintainer of this community fork claims only the documented local changes, not authorship of the complete firmware.

Development and documentation were prepared with AI assistance (OpenAI Codex). Build and emulator results are documented separately from physical-radio validation.

AMH0004: the explicit fixed-slot hardware AGC integration principle was identified by comparing Egzumer 0.22. This test implements it in FAGCI RX setup; the Egzumer software gain table/controller was not ported.

TXP0007: per-memory TX inhibition and matching CHIRP adaptation. CHIRP transport credits: Jacek Lipkowski, Dan Smith; supplied IJV adaptation also credits Julian Lilov LZ1JDL and Francesco IK8JHL. Driver source and GPL-3.0-or-later license are in chirp/.

TXM0008: on-radio per-memory TX menu and matching CHIRP module; independent community change prepared with Codex assistance.

Release packaging 2026-10-15: official OneOfEleven K5Prog Windows v1.26 and corresponding source are included separately under GPL. See tools/k5prog-win/v1.26/PROVENANCE.md.
