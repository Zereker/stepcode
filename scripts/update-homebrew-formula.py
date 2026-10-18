#!/usr/bin/env python3
"""Generate a Stepcode Homebrew formula for a tested GitHub Release asset."""
import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--tag", required=True)
p.add_argument("--sha256", required=True)
p.add_argument("--output", default="Formula/stepcode.rb")
a = p.parse_args()
if not a.tag.startswith("stepcode-rust-v"):
    raise SystemExit("Refusing non-stable Stepcode release tag")
version = a.tag.removeprefix("stepcode-rust-v")
if not version or not all(x.isdigit() for x in version.split(".")) or len(a.sha256) != 64 or any(c not in "0123456789abcdef" for c in a.sha256):
    raise SystemExit("Invalid stable version or SHA256")
url = f"https://github.com/Zereker/zcode/releases/download/{a.tag}/stepcode-macos-arm64-rust-v{version}.tar.gz"
formula = f'''class Stepcode < Formula
  desc "Independent Stepcode CLI built from official stable Codex releases"
  homepage "https://github.com/Zereker/zcode"
  url "{url}"
  sha256 "{a.sha256}"
  version "{version}"

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
