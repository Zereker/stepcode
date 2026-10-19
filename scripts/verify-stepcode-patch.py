#!/usr/bin/env python3
"""Validate Stepcode's patched stable-release source before the expensive build."""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) == 2 else None
if root is None:
    raise SystemExit("usage: verify-stepcode-patch.py PATH_TO_CODEX_ROOT")

def require(path, *needles):
    text = (root / path).read_text()
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"FAIL: {path}: missing {needle!r}")
    return text

state = require("codex-rs/state/src/lib.rs", 'pub const SQLITE_HOME_ENV: &str = "STEPCODE_SQLITE_HOME";')
daemon = require("codex-rs/app-server-daemon/src/background_command.rs", '"STEPCODE_HOME"', '"STEPCODE_SQLITE_HOME"')
if '"CODEX_HOME"' in daemon or '"CODEX_SQLITE_HOME"' in daemon:
    raise SystemExit("FAIL: daemon still propagates legacy Codex home variables")
provider = require("codex-rs/core/src/otel_init.rs", "// Stepcode policy: never construct Statsig, OTLP logs, traces or metrics.", "Ok(None)")
start = provider.index("pub fn build_provider(")
end = provider.index("pub fn record_process_start(", start)
if "OtelProvider::try_new" in provider[start:end] or "OtelExporter::" in provider[start:end]:
    raise SystemExit("FAIL: unified Stepcode provider can still initialize exporters")
require("codex-rs/utils/home-dir/src/lib.rs", '"STEPCODE_HOME"', '".stepcode"')
require("codex-rs/app-server-daemon/src/managed_install.rs", '"stepcode"')
print("PASS: Stepcode SQLite, daemon env, home, and unified telemetry guards")
