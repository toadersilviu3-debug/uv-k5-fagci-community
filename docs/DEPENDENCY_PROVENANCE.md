# Dependency provenance

The original local FAGCI MOD v1.2.1 ZIP contained empty external/CMSIS_5 and external/printf directories. The development build recovered these trees from the user-supplied Egzumer 0.22 source ZIP.

CMSIS remains attributed to ARM and its contributors; printf remains attributed to Marco Paland and its contributors. Their licenses are preserved. This use of dependencies does not mean the Egzumer AM controller was incorporated.

The full release source archive contains the actual dependency files. DEPENDENCIES_SHA256.json records their content hashes. Exact upstream Git commit IDs have not been reconstructed from those ZIP snapshots. The original .gitmodules is preserved as historical/upstream metadata; it does not by itself prove matching revisions.

Before presenting the Git fork checkout as a reproducible source for the distributed binary, compare its initialized submodules with this snapshot, pin matching revisions if found, or explicitly vendor the required snapshot with notices and a documented change to .gitmodules/gitlinks. Never silently replace the dependencies or claim verified equivalence without comparing them.

## Fork checkout decision
This branch vendors the exact dependency snapshot used for SPC0002 instead of using Git submodules. The two original gitlinks and .gitmodules were removed; upstream metadata is retained in docs/upstream.gitmodules.txt. Content hashes remain in DEPENDENCIES_SHA256.json. The inherited release workflow is archived as docs/upstream-release-workflow.yaml.txt and is not active.
