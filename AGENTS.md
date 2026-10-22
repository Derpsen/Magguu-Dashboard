# Magguu Dashboard – Arbeitsregeln für Assistenten

## Ziel

Dieses Repository enthält ein vollständig YAML-basiertes Home-Assistant-Dashboard für Smartphone, Tablet und Desktop. Es soll sich wie eine hochwertige Smart-Home-App anfühlen und nicht wie eine lose Sammlung von Lovelace-Karten.

## Grok Bot / Buddy

## Arbeitscomputer (2026-10-15)

- Checkout: Unraid-VM `Ubuntu`, machineId `3ff4cee8-7e7c-4cc9-a262-ebf10016d570`, path `~/Projekte/Magguu-Dashboard` (repos ready).
- Marcos PC nur WoW-AddOns-Deploy; Status nur an Buddy, nie 1:1 Marco.


Marco nutzt Grok Bot „Buddy“ als einzige Front Door. Owner dieses Repos: **"Bot & Dashboard"** (auch MagguuBot). "Website" = nur MagguuUI-Website, "Addon (Lua)" = Addon-Lua, "Code-Review" = Review, "Release" = Releases, "Unraid & Server" = Unraid (Umbenennung 2026-10-16, IDs unverändert; Captain und Gruppenchats gelöscht). Helfer melden Ergebnisse an Buddy zurück.

- Interaktive/Ad-hoc-Sessions: kein Commit, Push oder Git-Tag ohne ausdrückliche Freigabe für genau diesen Schritt.
- Helfer unter Buddy-Hub-Standing-Order: klare In-Scope-Fixes dürfen ohne Nachfrage pro Änderung committen, pushen und nach `main` mergen; niemals force-push; niemals unzusammenhängendes dirty WIP mitveröffentlichen; Tags/Releases brauchen eine ausdrückliche Release-Freigabe.

## Unverhandelbare Regeln

- Vor Änderungen das gesamte betroffene Modul lesen.
- Bestehende Entitäts-IDs niemals erraten oder stillschweigend ändern.
- Neue Entitäten nur aus `docs/entities.md` verwenden oder als klar markiertes TODO dokumentieren.
- Home-Assistant-Tags wie `!include`, `!include_dir_merge_list` und `!include_dir_merge_named` erhalten.
- Keine unnötigen HACS-Abhängigkeiten hinzufügen.
- Gemeinsame Logik über Templates wiederverwenden; kein Copy-and-paste zwischen Mobile und Tablet.
- Mobile und Tablet nach jeder Layoutänderung gemeinsam prüfen.
- Keine funktionierende Seite entfernen, ohne Ersatz und Changelog-Eintrag.
- Keine Zugangsdaten, Tokens, Hostnamen oder privaten URLs committen.
- Änderungen klein, nachvollziehbar und rückrollbar halten.
- Kein ElvUI-/WoW-Addon-Ballast in dieses Home-Assistant-Repo einbringen.

## Designsystem

- Dunkles Midnight-Design mit ruhigen Flächen.
- Große, zusammenhängende Raumkarten statt vieler kleiner Standardkarten.
- Aktive Elemente erhalten Farbe und einen dezenten Glow.
- Licht: warmes Gold.
- Klima und Wasser: Blau/Türkis.
- Erfolgreicher/geschlossener Zustand: Grün nur sparsam.
- Warnung: Orange.
- Fehler: Rot.
- Inaktive Zustände neutral und kontrastarm.
- Abstände, Radien und Typografie über zentrale Templates bzw. Theme-Variablen steuern.
- Animationen dezent und performant; keine Daueranimationen ohne Informationswert.

## Seiten

- Home
- Räume
- Kalender
- Klima
- Medien
- Sicherheit
- Energie
- System

## Raumkarten

Jede Raumkarte soll möglichst in einer einzigen zusammenhängenden Karte enthalten:

- Raumname
- großes Raumsymbol
- Temperatur und Luftfeuchtigkeit
- Fenster-/Türstatus
- Anzahl aktiver Lichter
- wichtigste direkte Aktionen
- Navigation zur Raumdetailseite
- aktive Zustände visuell hervorgehoben

## Qualitätssicherung

Nach jeder Änderung:

1. YAML-Dateien syntaktisch prüfen.
2. Include-Pfade prüfen.
3. Entitäts-IDs gegen `docs/entities.md` prüfen.
4. Mobile und Tablet auf doppelte oder abweichende Logik prüfen.
5. `CHANGELOG.md` aktualisieren.
6. Einen kurzen Commit-Vorschlag nennen (Buddy/Helfer: bei klaren In-Scope-Fixes laut Standing Order selbst committen/pushen/mergen).

## Arbeitsweise

- Erst analysieren, dann einen konkreten Plan nennen, danach umsetzen.
- Bei großen Aufgaben phasenweise arbeiten.
- Rückfragen nur bei wirklich fehlenden Informationen stellen.
- Offene Punkte in `TASKS.md` dokumentieren.

## MagguuUI pack/copy product facts (pointer)

Dashboard stays HA-focused and does not invent MagguuUI Lua rules. When "Website" or "Bot & Dashboard" updates WowUp starter/optional packs, Ellesmere TOC, or related product facts (no KSL/WindTools, etc.), reflect the same delta here in a short note so helpers do not drift across repos. Canonical detail lives in MagguuUI-Website / MagguuBot `AGENTS.md`.

- Current state (2026-10-15): MagguuUI addon live **v12.1.8** (tagged 2026-10-14; v12.1.7 superseded). The old whisper addon is fully removed everywhere; WowUp Optional includes **Whisper Messenger** (WhisperMessenger) as the whisper chat. The in-game player button is called **„Apply Magguu profiles“**.
- Node 26 is live for Bot (engines `>=26`) and Website (`>=26.12.0`) since 2026-10-16; this repo has no `package.json` / npm.

- Current delta (2026-10): WowUp Optional includes **Whisper Messenger** (WhisperMessenger) - not WIM / Ellesmere WIM Skin.

## Renovate (ex-Dependabot) / Merge reports: Actions-only vs App-Image

Dashboard is HA YAML (+ `validate.yml` CI). There is **no** MagguuUI / MagguuBot Unraid image pull from this repo.

- **Actions-only** (github-actions pins, validate workflow, pip `requirements-dev.txt` for CI, docs) → direct push to `main` (Renovate PRs: merge when CI green; Renovate App installed 2026-10-16); no pre-review; Buddy report: **Actions-only**; "Unraid & Server": none.
- **App-Image / Major** → normally N/A here (no Docker publish / no Magguu container rebuild). No pre-review step; Buddy reviews commits afterwards.

CI/Security setup (2026-10-12): `validate.yml` runs on push, PR and weekly (`17 4 * * 1`); `codeql.yml` (python + actions, SHA-pinned like MagguuBot) runs on push/PR to `main` and weekly. Since 2026-10-14 Renovate (ex-Dependabot, `renovate.json`) covers github-actions + pip (grouped, Monday Europe/Berlin); see 2026-10-14 "Bot & Dashboard" wave 2 (App installed 2026-10-16). No npm ecosystem unless a `package.json` is added.

Merge reports must say **Actions-only vs App-Image** (expect **Actions-only**).

## 2026-10-12 Docs/Bots-Sync

- Helpers (renamed again 2026-10-16, IDs unchanged): "Website" = MagguuUI-Website only; "Bot & Dashboard" = MagguuBot + Magguu-Dashboard; "Addon (Lua)" = addon Lua; "Code-Review" = review on request; "Release" = releases/Tag-Gate; "Unraid & Server" = Unraid; Buddy = front door. Former names: Webcraft, Botsmith, Luaforge, Sentinel, Launchpad, Homebase. Captain and all group chats/rooms were deleted 2026-10-16; Buddy contacts helpers directly; Notion holds only rules and the daily Docs-Abgleich log.
- Buddy makes small MagguuUI-Website design/text changes directly; bigger work goes to the helpers. Since 2026-10-12 helpers and Buddy push directly to `main` (no PRs, no pre-review); Buddy reviews commits afterwards; after a green Docker publish the no-AI Unraid pull/test script (`magguu-pull`, rollback on failure) pulls the new image.
- Addon live v12.1.7 (superseded: live **v12.1.8** since 2026-10-14). "Split names" options are becoming "Two-tone unit-frame names" / "Two-tone party and raid names" (MagguuUI PR #30; `SPLIT_NAMES` keys unchanged): half the name in the default color, half in the class color.
- Website live build: auto-deployed, current SHA at https://ui.magguu.xyz/api/health (history in `MEMORY.md`); legal notice = "free, non-commercial project operated from Switzerland" + `contact@magguu.xyz` (no name, no address).
- Unchanged: WIM removed, Whisper Messenger used; "Apply Magguu profiles"; Node 26 live (Bot + Website); locked TS 7, h3 2, @types/node 26; uid 99 + Cosign; `engines.node >=26` (Website >=26.12.0); no tags without Marco's yes; never remove third-party author names.

## 2026-10-14 "Bot & Dashboard" wave 2

- Renovate replaces Dependabot (`renovate.json`; `.github/dependabot.yml` removed): Monday, Europe/Berlin, groups github-actions + pip, automerge only minor/patch after green CI, majors manual; TypeScript <7, h3 <2, satori ~0.41 guards. Renovate GitHub App installed 2026-10-16 (Dependency Dashboard #12).
- New subview `dienste` („Magguu-Dienste“, linked from System): Website status, MagguuBot uptime/build, last Docker deploy (Bot + Website), last bot webhook per source. Shared include `shared/views/dienste.yaml` for mobile + tablet.
- Sensors live in optional package `docs/optional/magguu_dienste.yaml` (REST, secrets only via !secret: `magguu_bot_status_url`, `magguu_bot_status_auth`, `magguu_website_status_url`, `github_status_auth`). TODO in `docs/entities.md`; "Unraid & Server" copies it to /config/packages/ once secrets exist. Bot side: `GET /api/status` (Bearer `STATUS_API_TOKEN`). Website `/api/status` does not exist yet ("Website") – interim `/api/health`.

## Renovate automerge & pre-push hook (2026-10-16)

- `renovate.json`: minor/patch/pin/digest automerge with `automergeType: "branch"` + `platformAutomerge` (lands directly on `main` only after required status checks / CI are green; `ignoreTests: false`). Majors never automerge. Locked majors stay blocked via `allowedVersions`: TypeScript <7, @types/node <25 (stricter than <26).
- In-repo pre-push hook `.githooks/pre-push` runs `python -m unittest discover -s tests` + `python validate.py` (no package.json) plus `actionlint` (.github/workflows) and `shellcheck` (tracked `*.sh`); missing tools only warn and skip. Enable once per checkout: `git config core.hooksPath .githooks` (set on the Ubuntu VM checkout).
- Security (2026-10-16): `scorecard.yml` (ossf/scorecard-action v2.5.0, SHA-pinned; push main + weekly; SARIF → code scanning, upload-sarif SHA = codeql.yml SHA, bump together) and `dependency-review.yml` (actions/dependency-review-action v5.0.0, PRs, fails on >= moderate). Secret scanning + push protection enabled via `gh api` (verified enabled).
- Quality (2026-10-16): `.github/workflows/quality.yml` runs `tools/drift-check.sh` (banned addon names outside AGENTS/MEMORY/CHANGELOG/tests, EllesmereUI min 9.0.6 in TOCs, Docker uid 99, engines.node = `${NODE_ENGINE:->=26}`), actionlint 1.7.12 + zizmor 1.31.1 (medium+) + shellcheck + osv-scanner 2.7.0 (downloads sha256-verified). All workflows hardened for zizmor: checkout `persist-credentials: false`, validate.yml actions SHA-pinned + contents:read.

## Docs drift (2026-10-22)

- `tools/docs-drift.sh` (generic, copied 1:1 from MagguuUI-Website; keep identical across repos) reads `.github/docs-drift-rules.txt` (`regex<TAB>reason[<TAB>allow[<TAB>file-scope]]`, `@files`, `@allow`, `@ignorecase`, `@health-url`) and prints `file:line: reason`; exit 1 on hits. Rules flag old helper names (written in history lines with "formerly"/"Old names"/dated prefix are allowed), Captain, the banned whisper addon (written as `[W]IM` in the rules), the old PR/pre-review flow, Dependabot as active updater, Node 26 as locked, locked majors (TypeScript 7, h3 2, js-yaml 5, `@types/node` 26) presented as done, and any live `sha-…`/`sha256:` in AGENTS.md (history belongs in MEMORY.md). No `@health-url`: this repo has no endpoint of its own.
- `.github/workflows/docs-drift.yml` (Mon 05:17 UTC + dispatch) opens/updates one issue "Docs-Drift" assigned to Derpsen, and closes it when clean. Run locally: `bash tools/docs-drift.sh`.
