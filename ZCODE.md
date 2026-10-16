# Zcode — Project Requirements

Zcode is an independent, upstream-trackable fork of [OpenAI Codex CLI](https://github.com/openai/codex). It is **not** the Codex desktop application.

## Non-negotiable requirements

1. **Independent CLI identity.** The primary installed executable and visible main process must be named `zcode`, not `codex`. Help text and user-facing Zcode branding should be updated where appropriate. Check spawned subprocess names separately; changing the main binary does not automatically rename them.
2. **Independent user data.** Use `~/.zcode` by default and `ZCODE_HOME` as its override. Keep authentication, session history, logs, caches and mutable state separate from `~/.codex` wherever technically possible. Audit alternate paths, environment variables, keychain entries, and project-specific artifacts. Never overwrite or migrate Codex data implicitly.
3. **AgentD is out of scope.** AgentD is a system tool and MUST NOT be modified: no edits to `~/.agentd`, its profiles, plist files, services or source. Zcode must expose its own process identity and paths so AgentD *can* distinguish it. Whether AgentD actually recognizes Zcode as a separate agent must be verified externally; changing Zcode alone cannot guarantee AgentD behavior.
4. **No Zcode telemetry.** Do not configure, generate or emit OTel traces, metrics, or telemetry logs from Zcode. Eliminate or disable other optional analytics/telemetry paths as well, and test the result. API traffic required to operate the coding agent is not telemetry. Ordinary local operational logs and session data are separate and should be controllable. Do not install AgentD hooks in Zcode.
5. **Apple Silicon only.** Build and release a macOS ARM64 executable/package. No Windows, Linux or Intel Mac release artifacts are required.
6. **Track upstream.** Check OpenAI Codex upstream regularly, merge updates when safe, test the customized build and package/publish only after success. Merge conflicts, compilation failure, failed tests or failed isolation checks MUST block releases. Avoid unnecessary broad edits to upstream internals.
7. **Coexistence.** Original `codex` and custom `zcode` must be able to coexist without clobbering each other's files or executable.

## Release acceptance checklist

- [ ] `zcode --version` and `zcode --help` work on Apple Silicon.
- [ ] Executable basename is `zcode`; inspect running process tree.
- [ ] Fresh Zcode session writes to `~/.zcode` and not `~/.codex`.
- [ ] `ZCODE_HOME` override is respected; no accidental `CODEX_HOME` dependence in runtime paths.
- [ ] Credentials, history, logs, caches, keychain and child processes are audited for isolation.
- [ ] Zcode does not emit optional OTel or analytics telemetry; test this explicitly.
- [ ] Neither build/install nor runtime modifies AgentD configuration.
- [ ] Official Codex continues to work independently.
- [ ] CI compiles/tests `aarch64-apple-darwin` and publishes ONLY on passing checks.
- [ ] Upstream sync failure or merge conflict cannot publish a release.

## Current status (2026-10-16)

**Partial implementation, not an accepted release.**

- Done in source: changed CLI binary target/default-run to `zcode`, changed top-level CLI usage text, and modified centralized home directory handling to `ZCODE_HOME` / `~/.zcode`.
- Added initial GitHub Actions workflow `.github/workflows/zcode-arm64.yml` for scheduled upstream sync and ARM64 compilation/release.
- NOT YET VERIFIED: workflow run, successful macOS compilation, process/subprocess identity, fully isolated user data, test suite, and actual release artifacts.
- NOT YET COMPLETE: removing/disabling every Codex telemetry path, full isolation audit, robust CI release gates. The initial workflow's build check alone is insufficient for this specification.
- No AgentD files were changed as part of this repository work.

## Upstream maintenance policy

Treat upstream source as a base. Keep Zcode-specific edits small and well documented. Never silently discard downstream patches to resolve a merge. Publish only builds proven to meet the checklist.
