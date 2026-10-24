#!/usr/bin/env python3
"""Apply the minimal Stepcode identity patch to a clean upstream Codex checkout.

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
    ('default-run = "codex"', 'default-run = "stepcode"'),
    ('name = "codex"\npath = "src/main.rs"', 'name = "stepcode"\npath = "src/main.rs"'),
])
patch("codex-rs/cli/src/main.rs", [
    ('bin_name = "codex",', 'bin_name = "stepcode",'),
    ('override_usage = "codex [OPTIONS] [PROMPT]\\n       codex [OPTIONS] <COMMAND> [ARGS]"',
     'override_usage = "stepcode [OPTIONS] [PROMPT]\\n       stepcode [OPTIONS] <COMMAND> [ARGS]"'),
])
patch("codex-rs/utils/home-dir/src/lib.rs", [
    ('std::env::var("CODEX_HOME")', 'std::env::var("STEPCODE_HOME")'),
    ('p.push(".codex");', 'p.push(".stepcode");'),
    ('expected.push(".codex");', 'expected.push(".stepcode");'),
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
# Adapt the upstream daemon package installer to the Stepcode executable name.
# 0.164.0 validates the entrypoint dynamically; do not patch the removed names list.\n# Retain upstream helper names (code-mode host, rg) to avoid changing their protocols.
patch("codex-rs/app-server-daemon/src/prepare_install.rs", [
    ('    let entrypoint = if cfg!(windows) {\n        "bin/codex.exe"\n    } else {\n        "bin/codex"\n    };',
     '    let entrypoint = if cfg!(windows) {\n        "bin/stepcode.exe"\n    } else {\n        "bin/stepcode"\n    };'),
    ('symlink("bin/codex",', 'symlink("bin/stepcode",'),
])
patch("codex-rs/app-server-daemon/src/managed_install.rs", [
    ('if cfg!(windows) { "codex.exe" } else { "codex" }',
     'if cfg!(windows) { "stepcode.exe" } else { "stepcode" }'),
])
# Isolate SQLite overrides and the daemon's inherited process environment.
patch("codex-rs/state/src/lib.rs", [
    ('pub const SQLITE_HOME_ENV: &str = "CODEX_SQLITE_HOME";',
     'pub const SQLITE_HOME_ENV: &str = "STEPCODE_SQLITE_HOME";'),
])
# The old CODEX_* values must never be propagated to Stepcode's daemon.
path = root / "codex-rs/app-server-daemon/src/background_command.rs"
original = path.read_text()
if original.count('"CODEX_HOME"') != 2 or original.count('"CODEX_SQLITE_HOME"') != 3:
    raise SystemExit("FAIL: unexpected daemon environment variable layout")
path.write_text(original.replace('"CODEX_HOME"', '"STEPCODE_HOME"')
                        .replace('"CODEX_SQLITE_HOME"', '"STEPCODE_SQLITE_HOME"'))

# All normal CLI, TUI, app-server and exec calls use this unified OTEL
# constructor. Return no provider even when the config explicitly requests
# Statsig or OTLP; leave model/API network traffic and local diagnostics intact.
path = root / "codex-rs/core/src/otel_init.rs"
original = path.read_text()
start = original.find("pub fn build_provider(")
end = original.find("\npub fn record_process_start(", start)
if start < 0 or end < 0 or original.count("pub fn build_provider(") != 1:
    raise SystemExit("FAIL: upstream OTEL provider entrypoint changed")
replacement = """pub fn build_provider(
    _config: &Config,
    _service_version: &str,
    _service_name_override: Option<&str>,
    _default_analytics_enabled: bool,
) -> Result<Option<OtelProvider>, Box<dyn Error>> {
    // Stepcode policy: never construct Statsig, OTLP logs, traces or metrics.
    Ok(None)
}
"""
path.write_text(original[:start] + replacement + original[end:])

print("Applied Stepcode identity patch and forced-off telemetry and isolated SQLite patch")

