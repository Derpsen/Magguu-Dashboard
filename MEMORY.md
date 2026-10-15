# MEMORY.md

Helper memory for Magguu-Dashboard. Rules, design system and QA live in `AGENTS.md`.

## Ownership (2026-10-12)

- **Botsmith** (formerly Bot Fixer) owns Magguu-Dashboard and MagguuBot (fixes, Renovate (ex-Dependabot), AGENTS/MEMORY, Notion log). Webcraft (formerly Stack Fixer) covers MagguuUI-Website only.
- Results go to **Buddy** (front door) as a short German Done-State. Helpers never ask Marco directly.

## Current state (2026-10-12)

- Version: `6.4.0-dev` (`VERSION`). Last merges: #8 `279f99e` (Dependabot groups + AGENTS refresh, absorbs #7), #9 `4e47296` (CodeQL python + actions, weekly validate). No open PRs at handover.
- Repo is HA YAML only: no `package.json`, no Docker image, no Unraid container. Every merge is **Actions-only**; Homebase is never pinged from here.
- CI: `validate.yml` (push, PR, weekly `17 4 * * 1`), `codeql.yml` (python + actions, SHA-pinned, push/PR to `main` + weekly). Dependency bot: Renovate since 2026-10-14 (ex-Dependabot, `renovate.json`): github-actions + pip, grouped, Monday Europe/Berlin; App not installed yet (see 2026-10-14 Botsmith wave 2).

## Pipeline

- Push directly to `main` (no PRs, no Sentinel pre-review; Buddy reviews commits afterwards). Renovate PRs (once the App is installed): merge when CI green. No force-push. No tags/releases without Marco's explicit yes via Buddy.
- Actions-only (action pins, workflows, `requirements-dev.txt`, docs): push/merge when CI is green.
- Nothing here touches an App-Image path; no Homebase pull.
- Merge reports always say **Actions-only vs App-Image** (expect Actions-only).

## Locked majors (cross-repo, need Marco's yes)

- Node 26 (~end of Oct 2026), TypeScript 7, h3 2, satori 0.41 (Website), `@types/node` 26 (Bot). Not used here, but do not introduce them via drive-by changes.
- Website/Bot: `engines.node >=24.17`, containers uid 99, Cosign keyless, no QEMU.

## Hard rules

- Never guess or silently change entity IDs; new entities only from `docs/entities.md` or as a marked TODO.
- Keep HA `!include*` tags. No unnecessary HACS dependencies. No credentials, tokens, hostnames or private URLs.
- No WoW/ElvUI/MagguuUI addon code in this repo; only short product-fact pointers in `AGENTS.md`.
- Never remove or replace third-party author names.
- Keep commits in scope; no drive-by dependency bumps.

## MagguuUI product facts pointer (2026-10-12)

- Addon live **v12.1.8** (since 2026-10-14; was v12.1.7). WIM fully removed; Whisper Messenger (WhisperMessenger) is the whisper chat on WowUp Optional. Player button: **Apply Magguu profiles**. Canonical detail lives in MagguuBot / MagguuUI-Website `AGENTS.md`; mirror pack/copy deltas here the same round.

## 2026-10-12 Docs/Bots-Sync

- Helpers renamed (IDs unchanged): Botsmith = MagguuBot + Magguu-Dashboard; Webcraft = MagguuUI-Website only; Luaforge = addon Lua; Sentinel = review; Launchpad = releases/Tag-Gate; Homebase = Unraid; Captain = Notion; Buddy = front door. Old names: Stack Fixer/Stack, Bot Fixer, Addon Fixer, Reviewer, Release Helfer, Homelab Helfer, Projects Manager.
- Rooms: Addon HQ, Web Studio, Bot Lab, Dashboard Deck, Homebase Ops.
- Buddy makes small MagguuUI-Website design/text changes directly; bigger work goes to the helpers. Since 2026-10-12 helpers and Buddy push directly to `main` (no PRs, no Sentinel pre-review); Buddy reviews commits afterwards; Homebase pulls autonomously after green Docker publish.
- Addon live v12.1.7 (superseded: live **v12.1.8** since 2026-10-14). "Split names" options are becoming "Two-tone unit-frame names" / "Two-tone party and raid names" (MagguuUI PR #30; `SPLIT_NAMES` keys unchanged): half the name in the default color, half in the class color.
- Website live `sha-d8e734a` (digest `sha256:516f6c21…`, 2026-10-14: admin restyle, admin save clears cache, `/admin/content` shows a page list) — superseded: live since 2026-10-14 late evening is `sha-5db94ed` (digest `sha256:abfe0d1d…`, v12.1.8 changelog notes); legal notice = "free, non-commercial project operated from Switzerland" + `contact@magguu.xyz` (no name, no address).
- Unchanged: WIM removed, Whisper Messenger used; "Apply Magguu profiles"; Node 26 needs Marco's yes; locked TS 7, h3 2, @types/node 26; uid 99 + Cosign; `engines.node >=24.17`; no tags without Marco's yes; never remove third-party author names.

## 2026-10-14 Botsmith wave 2

- Renovate replaces Dependabot (`renovate.json`; `.github/dependabot.yml` removed): Monday, Europe/Berlin, groups github-actions + pip, automerge only minor/patch after green CI, majors manual; Node <26, TypeScript <7, h3 <2, satori ~0.41 guards. **Renovate GitHub App not installed yet** (no Renovate check suites/PRs) – Marco/Buddy must install it; until then there are no automatic dependency PRs.
- New subview `dienste` („Magguu-Dienste“, linked from System): Website status, MagguuBot uptime/build, last Docker deploy (Bot + Website), last bot webhook per source. Shared include `shared/views/dienste.yaml` for mobile + tablet.
- Sensors live in optional package `docs/optional/magguu_dienste.yaml` (REST, secrets only via !secret: `magguu_bot_status_url`, `magguu_bot_status_auth`, `magguu_website_status_url`, `github_status_auth`). TODO in `docs/entities.md`; Homebase copies it to /config/packages/ once secrets exist. Bot side: `GET /api/status` (Bearer `STATUS_API_TOKEN`). Website `/api/status` does not exist yet (Webcraft) – interim `/api/health`.

## 2026-10-15 Arbeitscomputer

- Helfer-Arbeitscomputer ist die Unraid-VM `Ubuntu` (machineId `3ff4cee8-7e7c-4cc9-a262-ebf10016d570`), Repos unter `~/Projekte` nach Homebase-Umzug. Marcos PC (`f01cf815-a384-40fb-ac18-c8450b4d5889`) nur noch für WoW-AddOns-Deploy, darf aus sein.
- Botsmith schreibt Marco nie im 1:1; Status/Done nur an Buddy.
