#!/usr/bin/env python3
"""Apply the minimal Zcode identity patch to a clean upstream Codex checkout.

Usage: python3 scripts/apply-zcode.py PATH_TO_CODEX_ROOT
Fails closed if upstream markers move; do not silently ship unpatched Codex.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else None
if not root or not (root / "codex-rs" / "Cargo.toml").is_file():
    raise SystemExit("Usage: apply-zcode.py PATH_TO_CODEX_ROOT")

def patch(rel, edits):
    path = root / rel
    original = path.read_text()
    result = original
    for old, new in edits:
        count = result.count(old)
        if count != 1:
            raise SystemExit(f"FAIL: {rel}: expected one match, found {count}: {old!r}")
        result = result.replace(old, new, 1)
    path.write_text(result)

patch("codex-rs/cli/Cargo.toml", [
    ('default-run = "codex"', 'default-run = "zcode"'),
    ('name = "codex"\npath = "src/main.rs"', 'name = "zcode"\npath = "src/main.rs"'),
])
patch("codex-rs/cli/src/main.rs", [
    ('bin_name = "codex",', 'bin_name = "zcode",'),
    ('override_usage = "codex [OPTIONS] [PROMPT]\\n       codex [OPTIONS] <COMMAND> [ARGS]"',
     'override_usage = "zcode [OPTIONS] [PROMPT]\\n       zcode [OPTIONS] <COMMAND> [ARGS]"'),
])
patch("codex-rs/utils/home-dir/src/lib.rs", [
    ('std::env::var("CODEX_HOME")', 'std::env::var("ZCODE_HOME")'),
    ('p.push(".codex");', 'p.push(".zcode");'),
    ('expected.push(".codex");', 'expected.push(".zcode");'),
])
# Inspired by Mabikega/codex-slop-fork: disable analytics by default.
# Also disable the default Statsig metrics exporter; default-off is not a
# complete runtime guarantee against explicitly configured exporters.
patch("codex-rs/exec/src/lib.rs", [
    ('const DEFAULT_ANALYTICS_ENABLED: bool = true;', 'const DEFAULT_ANALYTICS_ENABLED: bool = false;'),
])
patch("codex-rs/tui/src/daemon_telemetry.rs", [
    ('/*default_analytics_enabled*/ true,', '/*default_analytics_enabled*/ false,'),
])
patch("codex-rs/config/src/types.rs", [
    ('metrics_exporter: OtelExporterKind::Statsig,', 'metrics_exporter: OtelExporterKind::None,'),
])
# Adapt the upstream daemon package installer to the Zcode executable name.
# Retain upstream helper names (code-mode host, rg) to avoid changing their protocols.
patch("codex-rs/app-server-daemon/src/prepare_install.rs", [
    ('"bin/codex.exe"', '"bin/zcode.exe"'),
    ('        "bin/codex"\\n', '        "bin/zcode"\\n'),
    ('symlink("bin/codex",', 'symlink("bin/zcode",'),
])
patch("codex-rs/app-server-daemon/src/managed_install.rs", [
    ('if cfg!(windows) { "codex.exe" } else { "codex" }',
     'if cfg!(windows) { "zcode.exe" } else { "zcode" }'),
])
print("Applied Zcode identity patch and default-off analytics/metrics patch")

