#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Added for the independent SPC0002 community fork, 2026-10-13.
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/ucrt64/bin:$PATH:/usr/bin"
python3 -c 'import crcmod'
# The upstream Makefile ignores packing errors; remove stale output first.
rm -f firmware.packed.bin
make -B -j4 GIT_HASH=TXM0008
test -s firmware.packed.bin

