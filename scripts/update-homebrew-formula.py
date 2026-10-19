#!/usr/bin/env python3
"""Generate a Stepcode Homebrew formula for a tested GitHub Release asset."""
import argparse
import re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--tag", required=True)
p.add_argument("--sha256", required=True)
p.add_argument("--output", default="Formula/stepcode.rb")
a = p.parse_args()
match = re.fullmatch(r"stepcode-rust-v(\d+\.\d+\.\d+)(?:-r([1-9]\d*))?", a.tag)
if not match or len(a.sha256) != 64 or any(c not in "0123456789abcdef" for c in a.sha256):
    raise SystemExit("Invalid stable version or SHA256")
version, revision = match.group(1), int(match.group(2) or 0)
url = f"https://github.com/Zereker/stepcode/releases/download/{a.tag}/stepcode-macos-arm64-{a.tag.removeprefix('stepcode-')}.tar.gz"
formula = f'''class Stepcode < Formula
  desc "Independent Stepcode CLI built from official stable Codex releases"
  homepage "https://github.com/Zereker/stepcode"
  url "{url}"
  sha256 "{a.sha256}"
  version "{version}"
  revision {revision}

  depends_on :macos
  depends_on arch: :arm64

  def install
    libexec.install "bin", "codex-path", "codex-package.json", "REVISION.txt"
    bin.install_symlink libexec/"bin/stepcode"
  end

  test do
    assert_match "stepcode", shell_output("#{{bin}}/stepcode --help")
  end
end
'''
out=Path(a.output)
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(formula)
print(out)
