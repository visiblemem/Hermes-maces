# Native Hermes runtime distribution

The development repository contains adversarial fixtures, test runners and CI.
They are needed to verify the security boundary but are not runtime dependencies.
Some Hermes Plugin Guard versions flag fixture text during whole-repository installs.
Do not remove or disguise those tests, exempt runtime files, or disable the scanner.

`scripts/build_runtime.py` builds a separate distribution containing an explicit
inventory of runtime modules, the plugin entrypoint and manifest, safe example
configuration, license and security guidance. All shipped source bytes are unchanged.
No test runner, CI installer, build script, credential or database is shipped.
The builder refuses an existing output directory, symlinked inputs and an unexpected
module inventory. `SOURCE.json` records the source commit and hashes of shipped files.

## Release procedure

1. Review and test an immutable development commit. Keep all adversarial tests in it.
2. Export that commit into a fresh staging directory, using Git's committed bytes
   rather than an edited working tree or platform-specific checkout conversion.
3. Run the builder from the reviewed source, giving the exported directory as
   `--source`, its full commit as `--source-commit`, and a new outside destination.
4. Run the full real-PluginManager suite against the generated layout. Its E2E fixture
   builds exactly this layout. Scan the whole artifact with the unmodified native
   Hermes Plugin Guard. A clean scan is not a substitute for source review and tests.
5. Publish the generated artifact on a separate distribution branch. Keep the
   development commit as its parent for traceability; never merge a runtime-only
   tree into main. Publish its exact SHA together with the source SHA and scan result.
6. Install that immutable distribution SHA through the native Hermes CLI with
   `--no-enable`. Check the installed files against SOURCE.json and source Git blobs.
7. Configure one profile in Shadow Mode, explicitly deny tool overrides, enable
   through the native registry, and verify its next runtime startup.

The installer scans every shipped file. There is no local scanner exception,
trust-level override, filtered runtime source or alternate loader. Runtime changes
require new tests, a new artifact and another scan. Existing installs remain pinned.

This packaging does not make MACES a stable release or enable automatic learning.
The seven-day minimum Shadow period and separate local quality review still apply.
