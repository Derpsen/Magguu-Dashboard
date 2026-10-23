# MEMORY.md

Helper memory for Magguu-Dashboard. Rules, design system and QA live in `AGENTS.md`.

## Ownership (2026-10-12)

- **"Bot & Dashboard"** (formerly Bot Fixer) owns Magguu-Dashboard and MagguuBot (fixes, Renovate (ex-Dependabot), AGENTS/MEMORY, Notion log). "Website" (formerly Stack Fixer) covers MagguuUI-Website only.
- Results go to **Buddy** (front door) as a short German Done-State. Helpers never ask Marco directly.

## Current state (2026-10-12)

- Version: `6.4.0-dev` (`VERSION`). Last merges: #8 `279f99e` (Dependabot groups, superseded by Renovate; AGENTS refresh, absorbs #7), #9 `4e47296` (CodeQL python + actions, weekly validate). No open PRs at handover.
- Repo is HA YAML only: no `package.json`, no Docker image, no Unraid container. Every merge is **Actions-only**; "Unraid & Server" is never pinged from here.
- CI: `validate.yml` (push, PR, weekly `17 4 * * 1`), `codeql.yml` (python + actions, SHA-pinned, push/PR to `main` + weekly). Dependency bot: Renovate since 2026-10-14 (ex-Dependabot, `renovate.json`): github-actions + pip, grouped, Monday Europe/Berlin; App not installed yet (see 2026-10-14 "Bot & Dashboard" wave 2).

## Pipeline

- Push directly to `main` (no PRs, no pre-review; Buddy reviews commits afterwards). Renovate PRs (App installed 2026-10-16): merge when CI green. No force-push. No tags/releases without Marco's explicit yes via Buddy.
- Actions-only (action pins, workflows, `requirements-dev.txt`, docs): push/merge when CI is green.
- Nothing here touches an App-Image path; no "Unraid & Server" pull.
- Merge reports always say **Actions-only vs App-Image** (expect Actions-only).

## Locked majors (cross-repo, need Marco's yes)

- TypeScript 7, h3 2, js-yaml 5 and satori >=0.48 (Website uses satori ^0.47.1; >=0.48 locked without Marco's yes), `@types/node` 26 (Bot). Node 26 is no longer locked (live in Bot + Website since 2026-10-16). Not used here, but do not introduce them via drive-by changes.
- Website: `engines.node >=26.12.0`; Bot: `>=26` (Node 26 live 2026-10-16), containers uid 99, Cosign keyless, no QEMU.

## Hard rules

- Never guess or silently change entity IDs; new entities only from `docs/entities.md` or as a marked TODO.
- Keep HA `!include*` tags. No unnecessary HACS dependencies. No credentials, tokens, hostnames or private URLs.
- No WoW/ElvUI/MagguuUI addon code in this repo; only short product-fact pointers in `AGENTS.md`.
- Never remove or replace third-party author names.
- Keep commits in scope; no drive-by dependency bumps.

## MagguuUI product facts pointer (2026-10-12)

- Addon live **v12.1.8** (since 2026-10-14; was v12.1.7). WIM fully removed; Whisper Messenger (WhisperMessenger) is the whisper chat on WowUp Optional. Player button: **Apply Magguu profiles**. Canonical detail lives in MagguuBot / MagguuUI-Website `AGENTS.md`; mirror pack/copy deltas here the same round.

## 2026-10-12 Docs/Bots-Sync

- Helpers (renamed again 2026-10-16, IDs unchanged): "Website" = MagguuUI-Website only; "Bot & Dashboard" = MagguuBot + Magguu-Dashboard; "Addon (Lua)" = addon Lua; "Code-Review" = review on request; "Release" = releases/Tag-Gate; "Unraid & Server" = Unraid; Buddy = front door. Former names: Webcraft, Botsmith, Luaforge, Sentinel, Launchpad, Homebase. Captain and all group chats/rooms were deleted 2026-10-16; Buddy contacts helpers directly; Notion holds only rules and the daily Docs-Abgleich log.
- Buddy makes small MagguuUI-Website design/text changes directly; bigger work goes to the helpers. Since 2026-10-12 helpers and Buddy push directly to `main` (no PRs, no pre-review); Buddy reviews commits afterwards; after a green Docker publish the no-AI Unraid pull/test script (`magguu-pull`, rollback on failure) pulls the new image.
- Addon live v12.1.7 (superseded: live **v12.1.8** since 2026-10-14). "Split names" options are becoming "Two-tone unit-frame names" / "Two-tone party and raid names" (MagguuUI PR #30; `SPLIT_NAMES` keys unchanged): half the name in the default color, half in the class color.
- Website live `sha-d8e734a` (digest `sha256:516f6c21…`, 2026-10-14: admin restyle, admin save clears cache, `/admin/content` shows a page list) — superseded: live since 2026-10-14 late evening is `sha-5db94ed` (digest `sha256:abfe0d1d…`, v12.1.8 changelog notes; superseded 2026-10-17 by `sha-6dc9870`, build id `da0941f8`, Node 26); legal notice = "free, non-commercial project operated from Switzerland" + `contact@magguu.xyz` (no name, no address).
- Unchanged: WIM removed, Whisper Messenger used; "Apply Magguu profiles"; Node 26 live (Bot + Website); locked TS 7, h3 2, @types/node 26; uid 99 + Cosign; `engines.node >=26` (Website >=26.12.0); no tags without Marco's yes; never remove third-party author names.

## 2026-10-14 "Bot & Dashboard" wave 2

- Renovate replaces Dependabot (`renovate.json`; `.github/dependabot.yml` removed): Monday, Europe/Berlin, groups github-actions + pip, automerge only minor/patch after green CI, majors manual; TypeScript <7, h3 <2, satori ~0.41 guards (this repo's `renovate.json`, left as is). Website uses satori ^0.47.1; satori >=0.48 is locked without Marco's yes. **Renovate GitHub App not installed yet** (superseded: installed 2026-10-16, Dependency Dashboard #12) (no Renovate check suites/PRs) – Marco/Buddy must install it; until then there are no automatic dependency PRs.
- New subview `dienste` („Magguu-Dienste“, linked from System): Website status, MagguuBot uptime/build, last Docker deploy (Bot + Website), last bot webhook per source. Shared include `shared/views/dienste.yaml` for mobile + tablet.
- Sensors live in optional package `docs/optional/magguu_dienste.yaml` (REST, secrets only via !secret: `magguu_bot_status_url`, `magguu_bot_status_auth`, `magguu_website_status_url`, `github_status_auth`). TODO in `docs/entities.md`; "Unraid & Server" copies it to /config/packages/ once secrets exist. Bot side: `GET /api/status` (Bearer `STATUS_API_TOKEN`). Website `/api/status` does not exist yet ("Website") – interim `/api/health`.

## 2026-10-15 Arbeitscomputer

- Helfer-Arbeitscomputer ist die Unraid-VM `Ubuntu` (machineId `3ff4cee8-7e7c-4cc9-a262-ebf10016d570`). Repos bereit unter `~/Projekte` (Buddy 2026-10-15). Marcos PC (`f01cf815-a384-40fb-ac18-c8450b4d5889`) nur noch für WoW-AddOns-Deploy, darf aus sein.
- "Bot & Dashboard" schreibt Marco nie im 1:1; Status/Done nur an Buddy.

- 2026-10-16: Renovate branch-automerge (minor/patch/pin/digest after green CI, majors manual; TS<7, @types/node<25 locked). Pre-push hook `.githooks/pre-push` (checks + actionlint + shellcheck), enable via `git config core.hooksPath .githooks`; VM checkout enabled.
- shellcheck SC1007 fixed: `CDPATH='' cd` in install.sh, update.sh, tests/test-install.sh.
- 2026-10-16: Node 26 approved; Renovate Node hold removed. This repo has no Node runtime/CI references (Python CI only).
- 2026-10-16: CI Python 3.12 → 3.15 (validate.yml); PyYAML 6.0.3 already latest.
- Security (2026-10-16): `scorecard.yml` (ossf/scorecard-action v2.5.0, SHA-pinned; push main + weekly; SARIF → code scanning, upload-sarif SHA = codeql.yml SHA, bump together) and `dependency-review.yml` (actions/dependency-review-action v5.0.0, PRs, fails on >= moderate). Secret scanning + push protection enabled via `gh api` (verified enabled).
- Quality (2026-10-16): `.github/workflows/quality.yml` runs `tools/drift-check.sh` (banned addon names outside AGENTS/MEMORY/CHANGELOG/tests, EllesmereUI min 9.0.6 in TOCs, Docker uid 99, engines.node = `${NODE_ENGINE:->=26}`), actionlint 1.7.12 + zizmor 1.31.1 (medium+) + shellcheck + osv-scanner 2.7.0 (downloads sha256-verified). All workflows hardened for zizmor: checkout `persist-credentials: false`, validate.yml actions SHA-pinned + contents:read.

## 2026-10-22 Docs drift check

- Adopted `tools/docs-drift.sh` (1:1 from MagguuUI-Website) + `.github/docs-drift-rules.txt` + `docs-drift.yml` (Mon 05:17 UTC + dispatch; issue "Docs-Drift" → Derpsen on hits, closed when clean). No `@health-url` (no endpoint in this repo).
- Baseline fix: AGENTS.md no longer names Website live sha/digests (rule scoped to AGENTS.md; history stays in MEMORY.md "Docs/Bots-Sync"); stale "Renovate App not installed" wording fixed.

