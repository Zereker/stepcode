#!/usr/bin/env bash
set -euo pipefail
binary="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
test "$(uname -s)" = Darwin
test "$(uname -m)" = arm64
test "$(basename "$binary")" = zcode
file "$binary" | grep -q 'Mach-O 64-bit executable arm64'
scratch_dir="$(mktemp -d)"
trap 'rm -rf "$scratch_dir"' EXIT
mkdir -p "$scratch_dir/zcode" "$scratch_dir/codex"
printf 'preserve\n' > "$scratch_dir/codex/sentinel"
# Deliberately supply both overrides. Full session isolation is a separate gate.
ZCODE_HOME="$scratch_dir/zcode" CODEX_HOME="$scratch_dir/codex" "$binary" --version
ZCODE_HOME="$scratch_dir/zcode" CODEX_HOME="$scratch_dir/codex" "$binary" --help > "$scratch_dir/help.txt"
grep -q 'zcode' "$scratch_dir/help.txt"
test "$(cat "$scratch_dir/codex/sentinel")" = preserve
test "$(find "$scratch_dir/codex" -type f | wc -l | tr -d ' ')" = 1

