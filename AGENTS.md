# Magguu Dashboard – Arbeitsregeln für Assistenten

## Ziel

Dieses Repository enthält ein vollständig YAML-basiertes Home-Assistant-Dashboard für Smartphone, Tablet und Desktop. Es soll sich wie eine hochwertige Smart-Home-App anfühlen und nicht wie eine lose Sammlung von Lovelace-Karten.

## Grok Bot / Buddy

## Arbeitscomputer (2026-10-15)

- Checkout: Unraid-VM `Ubuntu`, machineId `3ff4cee8-7e7c-4cc9-a262-ebf10016d570`, path `~/Projekte/Magguu-Dashboard` (repos ready).
- Marcos PC nur WoW-AddOns-Deploy; Status nur an Buddy, nie 1:1 Marco.
- Reporting an Buddy (ab 2026-10-23): genau eine Done-Meldung pro Auftrag, max. ~800 Zeichen plus Pfad/Commit für Details; Zwischenstände nur bei Aufträgen über 30 Minuten.


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
- button-card-JS-Templates (`[[[ ]]]` in name/label/state/custom_fields) werden als HTML gerendert: externe Strings (Kalendertitel, Entity-States/-Attribute, Namen) immer mit `esc()` (`&<>"'` → Entities) einsetzen; nur feste Markup-Teile und Zahlen roh. Regressionstest: `tests/test_security.py` (führt die Templates mit node aus).
- `script.magguu_dashboard_aktualisieren` ist admin-only: erster Schritt `homeassistant.reload_custom_templates` (admin-only Core-Service, prüft `is_admin` des Aufrufer-Kontexts; Nicht-Admins bekommen Unauthorized, bevor etwas passiert). Nicht entfernen. Card-Visibility per `condition: user` braucht Marcos HA-User-ID; die steht nicht im Repo (nicht raten).
- `shell_command` ist für jeden HA-User direkt aufrufbar (kein Admin-Gate): nur der feste Befehl `sh /config/magguu-dashboard-update.sh`, keine Templates (`{{ }}`/`{% %}`/`{# #}`), keine weiteren Einträge. `update-ha.sh` liest weder Argumente noch Umgebungsvariablen (`CONFIG_DIR=/config`, `ARCHIVE_URL` fest auf `Derpsen/Magguu-Dashboard` main). `validate.py` erzwingt beides (`validate_shell_commands`, `validate_updater`); `tests/test-install.sh` testet eine per `sed` umgebogene Kopie.
- Updater-Sperre/Rotation: `update-ha.sh` läuft nur einmal gleichzeitig (`flock -n` auf `/config/.magguu-dashboard-update.lock`, falls vorhanden; sonst `mkdir`-Lock `/config/.magguu-dashboard-update.lockdir`, älter als 10 min = veraltet und wird übernommen; Freigabe per `trap` EXIT). Ein Parallellauf loggt eine Zeile und endet mit Exit 0 ohne Wirkung. `magguu_install_dashboard` behält in `/config/backups/` nur die 5 neuesten Magguu-Backups (striktes Muster `magguu-dashboard-YYYYMMDD-HHMMSS`, nur echte Verzeichnisse, das aktuelle bleibt immer); alles andere dort bleibt unberührt. Der Updater läuft komplett in `main; exit $?` (eine Zeile), weil der Installer die laufende Datei überschreibt. Busybox-/POSIX-sh-kompatibel halten; Tests: `tests/test-install.sh` (`LOCK_MODE` per `sed` auf `mkdir`).
- Version + Commit + Update-Hinweis (System-Seite, Karte „Dashboard-Version“): `VERSION` ist die Versionsquelle (Format `X.Y.Z[-dev]`, aktuell `6.10.3-dev`; alle Stellen: `VERSION`, `packages/magguu_dashboard.yaml` Sensor `magguu_dashboard_version`, `tests/test-install.sh` liest `VERSION`). Der Installer stempelt Version und Commit-SHA als Literal in `sensor.magguu_dashboard_version` / `sensor.magguu_dashboard_commit` (nur volle 40-stellige Hex-SHA, sonst `unbekannt`; Quelle: tar-pax-Header des GitHub-Archivs in `update-ha.sh` oder `git rev-parse HEAD` bei Klon-Installation, nie aus Umgebung/Argumenten). `sensor.magguu_dashboard_main_commit` ist ein REST-Sensor auf die öffentliche GitHub-API (feste URL, ohne Token/Secret/Authorization, `scan_interval` >= 3600, Fallback `unbekannt`); `sensor.magguu_dashboard_update_hinweis` vergleicht beide (`aktuell` / `verfuegbar` / `unbekannt`, SHA per `regex_match` geprüft). Das Update-Script lädt danach `template.reload` und `homeassistant.update_entity` (beide `continue_on_error`). `validate_update_hint` in `validate.py` erzwingt das; Tests: `tests/test_update_hint.py` (Templates laufen nur mit installiertem `jinja2`, in der CI ohne jinja2 übersprungen). Nichts davon darf Secrets oder `shell_command`-Argumente bekommen. Ein Versions-Bump braucht `VERSION` + Package-Sensor gleichzeitig (`validate.py` prüft Drift).
- Updater-Download: nur HTTPS (`CURL_PROTO='=https'` mit `--proto`/`--proto-redir`) und zeitbegrenzt (`--max-time`); die Tests biegen `CURL_PROTO` per `sed` auf `=file`. `validate.py` erzwingt die festen Zeilen.

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

## Layout und Validierung (seit 6.6.0-dev, Sections für alle Seiten seit 6.7.0-dev)

- Neue/geänderte Raum-Subviews: `type: sections` (`max_columns: 2`, Hero-Section mit `column_span: 2`, je Bereich eine Section mit Heading-Karte). Titel/Untertitel immer als native `type: heading` (`heading_style: title|subtitle`), nie wieder `custom:mushroom-title-card`.
- Alle Seiten sind `type: sections`. Inhalte stehen einmal in `dashboard/magguu-dashboard/shared/sections/` (Listen-Dateien per `sections: !include`, Einzel-Sections als Map-Dateien, nie Liste-in-Liste); Mobile (`max_columns: 1`) und Tablet (`max_columns: 3`) unterscheiden sich nur in der View-Hülle. Neue Seiten/Karten dort ergänzen, nicht in zwei Geräten doppeln. `custom:layout-card`/`grid-layout` nicht mehr einführen.
- Karten in Sections: Hero/Navbar mit `grid_options: {columns: full, rows: auto}`; verschachtelte `type: grid`-Karten direkt in Sections ebenso (sonst nur halbe Breite in 2-Spalten-Sections; Test); die Navbar-card steht in der ersten Section jeder Seite inkl. Raumseiten und ist unten zentriert; mushroom-template-, conditional- und stack-Karten immer mit `rows: auto` (sonst 56-px-Höhe, `validate.py` erzwingt das). Fehlende/optionale Entities mit `visibility` bzw. `conditional` ausblenden statt Fehler zu zeigen.
- Raumakzente (`accent`-Hex in Karten/Rooms) im Vordergrund nur über `color-mix(... var(--mag-room-accent-strength) ... var(--mag-room-accent-ink))`; neue Akzent-Hex werden vom WCAG-Test in `tests/test_theme.py` geprüft. `validate.py` lehnt doppelte YAML-Schlüssel ab.
- Sections liegen zeilenweise im CSS-Grid (nicht Masonry): Inhalte für die rechte Spalte neben einer langen Section gehören in dieselbe Section. Dreier-Kachelreihen: Flex-Umbruch (siehe `sicherheit.yaml`), nie festes `columns: 3` ohne Umbruch. Kameras/optionale Entities: Condition auf Zustand (Kinderzimmer: Bild nur bei `streaming`/`recording`, sonst kompakte Kachel; `entity_picture` ist immer gesetzt). button-card-JS (in YAML-Single-Quotes nur Doppelquotes im JS, sonst wird das Template still gekürzt): nur `variables?.x`, `states?.[…]`, `entity?.…` (validate.py prüft).
- Theme: Dark und Light definieren dieselben `mag-*`-Tokens; keine festen dunklen Farben (`rgba(24,25,39,…)`, weiße Overlays) in Templates, sondern Tokens. Kontrast prüft `tests/test_theme.py` (WCAG AA).
- Theme: `themes/magguu_midnight.yaml` nutzt `modes.dark` und `modes.light`; jedes in Dashboards verwendete `var(--mag-*)` muss im Theme stehen (`validate.py` prüft das). Neue Tokens zuerst im Theme definieren.
- `validate.py` prüft die View-/Section-/Heading-/Tile-Feature-Schemata, View-Pfade, Navigationsziele und erlaubte Kartentypen. Neue Custom-Karten nur nach Begründung in `ALLOWED_CUSTOM_CARDS` aufnehmen. Tests: `tests/test_dashboard_schema.py`.
- Nichts davon ersetzt eine Sichtprüfung im echten HA: Ergebnisse als „ungetestet“ kennzeichnen, solange Marco sie nicht bestätigt hat.

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

- Renovate replaces Dependabot (`renovate.json`; `.github/dependabot.yml` removed): Monday, Europe/Berlin, groups github-actions + pip, automerge only minor/patch after green CI, majors manual; TypeScript <7, h3 <2, satori <0.48 (>=0.48 locked) guards (this repo's `renovate.json`, left as is). Website uses satori ^0.47.1; satori >=0.48 is locked without Marco's yes. Renovate GitHub App installed 2026-10-16 (Dependency Dashboard #12).
- New subview `dienste` („Magguu-Dienste“, linked from System): Website status, MagguuBot uptime/build, last Docker deploy (Bot + Website), last bot webhook per source. Shared include `shared/views/dienste.yaml` for mobile + tablet.
- FAQ-Nutzung (6.10.2-dev): `sensor.magguu_bot_status` hat zusätzlich das Attribut `faq` (vom Bot-`/api/status`, nur anonyme Zähler der letzten 7 Tage); die Markdown-Karte „FAQ-Nutzung" in `shared/views/dienste.yaml` nutzt `content: |-` (Zeilenumbrüche der Liste) und bereinigt Titel von Markdown-Zeichen. Fehlt `faq` (älterer Bot), zeigt sie „Keine Daten".
- Ungesehene Medien (Bericht) (6.10.3-dev, Dienste-Seite): `sensor.magguu_bot_status` hat das Attribut `unseen` (vom Bot-`/api/status`; Top 25 große nie/lange nicht gesehene Plex-Titel: Titel, Größe, Bibliothek, letzte Sicht; keine Nutzerdaten). Rein LESEND: es gibt im Dashboard und im Bot keinen Lösch-/Schreibpfad, die Karte sagt das deutlich („Nur Bericht – nichts wird gelöscht“). Admin-Gate wie beim Update-Script: Die Liste steckt in einer `conditional`-Karte auf `input_boolean.magguu_ungesehen_bericht_offen`; nur `script.magguu_ungesehen_bericht_anzeigen` (erster Schritt `homeassistant.reload_custom_templates`, admin-only, `mode: restart`) schaltet ihn für 5 Minuten ein, Nicht-Admins bekommen Unauthorized und sehen nichts. Grenze: HA kennt kein `is_admin` in Karten-Bedingungen und Sensorattribute sind für jeden HA-User lesbar; eine echte Per-User-Sperre geht nur mit `visibility: condition: user` und Marcos User-ID (steht nicht im Repo, nicht raten). Im Template immer `u['items']` (nicht `u.items`, das ist die dict-Methode). Tests: `tests/test_unseen_card.py` (jinja2, in der CI ohne jinja2 übersprungen) + Admin-Gate-Test in `tests/test_security.py`.
- Sensors live in optional package `docs/optional/magguu_dienste.yaml` (REST, secrets only via !secret: `magguu_bot_status_url`, `magguu_bot_status_auth`, `magguu_website_status_url`, `github_status_auth`). TODO in `docs/entities.md`; "Unraid & Server" copies it to /config/packages/ once secrets exist. Bot side: `GET /api/status` (Bearer `STATUS_API_TOKEN`). Website `/api/status` does not exist yet ("Website") – interim `/api/health`.

## Renovate automerge & pre-push hook (2026-10-16)

- `renovate.json` (changed 2026-10-24): automerge as a PR (`automergeType: "pr"`, `platformAutomerge: false`, `ignoreTests: false`) for patch/pin/digest and for minor of stable (non-0.x) versions; Renovate itself waits until ALL checks of the PR are green and merges via API. Branch automerge was dropped: CI runs on `pull_request` only, so a bare `renovate/*` branch never gets checks, and the repo has no branch protection / required checks / auto-merge setting for GitHub-native automerge to rely on. 0.x minors get their own PR (`npm 0.x minor`, no automerge), majors never automerge and are never grouped with non-majors, `internalChecksFilter: strict` + `minimumReleaseAge` 3 days (npm; github-actions minor/patch; pip) hold branches until releases aged. `fileMatch` migrated to `managerFilePatterns`. Locked majors stay blocked via `allowedVersions`: TypeScript <7, @types/node <25 (stricter than <26), h3 <2, satori <0.48 (>=0.48 locked) (no npm deps today). Open recommendation (not changeable via repo files): protect `main` with required checks and enable "Allow auto-merge" so GitHub enforces what Renovate now only checks itself. Since 2026-10-23 also: `configMigration`, `vulnerabilityAlerts` (label `security`; needs GitHub vulnerability alerts, on since 2026-10-23), monthly `lockFileMaintenance`, npm `minimumReleaseAge` 3 days (no npm deps today). pip: `requirements-dev.in` is the source, `requirements-dev.txt` is generated with `pip-compile --generate-hashes --strip-extras --allow-unsafe --no-emit-index-url` and installed in CI with `--require-hashes --no-deps`; Renovate updates it via the `pip-compile` manager (`pip_requirements` manager off). Never hand-edit the `.txt`. Lizenz: MIT (`LICENSE`, `Copyright (c) 2026 Magguu`; Rechteinhaber Magguu, GitHub-Owner/Git-Identität bleiben Derpsen). Fremde Karten (button-card, Mushroom, layout-card, stack-in-card) werden nur referenziert und über HACS installiert, nicht gebündelt; gebündelte Fremd-Assets bräuchten einen THIRD-PARTY-Hinweis. Security: private vulnerability reporting on (`SECURITY.md`, only via Security → Report a vulnerability); Scorecard BranchProtection/CodeReview dismissed as won't fix (direct push to main intentional).
- In-repo pre-push hook `.githooks/pre-push` runs `python -m unittest discover -s tests` + `python validate.py` (no package.json) plus `actionlint` (.github/workflows) and `shellcheck` (tracked `*.sh`); missing tools only warn and skip. Enable once per checkout: `git config core.hooksPath .githooks` (set on the Ubuntu VM checkout).
- Security (2026-10-16): `scorecard.yml` (ossf/scorecard-action v2.5.0, SHA-pinned; push main + weekly; SARIF → code scanning, upload-sarif SHA = codeql.yml SHA, bump together) and `dependency-review.yml` (actions/dependency-review-action v5.0.0, PRs, fails on >= moderate). Secret scanning + push protection enabled via `gh api` (verified enabled).
- Quality (2026-10-16): `.github/workflows/quality.yml` runs `tools/drift-check.sh` (banned addon names outside AGENTS/MEMORY/CHANGELOG/tests, EllesmereUI min 9.0.6 in TOCs, Docker uid 99, engines.node = `${NODE_ENGINE:->=26}`), actionlint 1.7.12 + zizmor 1.31.1 (medium+) + shellcheck + osv-scanner 2.7.0 (downloads sha256-verified). All workflows hardened for zizmor: checkout `persist-credentials: false`, validate.yml actions SHA-pinned + contents:read.

## zizmor advisory (2026-10-23)

- `.github/workflows/zizmor.yml` (zizmorcore/zizmor-action SHA-pinned, `advanced-security: false`, no SARIF/`security-events`, step + job `continue-on-error`, never a required check) logs all zizmor findings on push main/PR/dispatch; `quality.yml` keeps its pinned zizmor (medium+) gate. First run: no findings. Checkout comments corrected to `v7.0.1` on 2026-10-23 (SHA `3d3c42e…` is the v7.0.1 tag).

## Docs drift (2026-10-22)

- `tools/docs-drift.sh` (generic, copied 1:1 from MagguuUI-Website; keep identical across repos) reads `.github/docs-drift-rules.txt` (`regex<TAB>reason[<TAB>allow[<TAB>file-scope]]`, `@files`, `@allow`, `@ignorecase`, `@health-url`) and prints `file:line: reason`; exit 1 on hits. Rules flag old helper names (written in history lines with "formerly"/"Old names"/dated prefix are allowed), Captain, the banned whisper addon (written as `[W]IM` in the rules), the old PR/pre-review flow, Dependabot as active updater, Node 26 as locked, locked majors (TypeScript 7, h3 2, js-yaml 5, `@types/node` 26) presented as done, and any live `sha-…`/`sha256:` in AGENTS.md (history belongs in MEMORY.md). No `@health-url`: this repo has no endpoint of its own.
- `.github/workflows/docs-drift.yml` (Mon 05:17 UTC + dispatch) opens/updates one issue "Docs-Drift" assigned to Derpsen, and closes it when clean. Run locally: `bash tools/docs-drift.sh`.

## Issue routing (2026-10-24)

- `.github/workflows/issue-route.yml` (trigger `issues: [opened, assigned]`, top-level `permissions: {}`, `issues: write` only in the job, no third-party actions, uses the runner's `gh`/`jq`/`curl`): labels by title keywords (`bug`, `security`, `dependencies`, `documentation`; missing labels are created). The issue body is never read; the title only reaches the scripts via `env:`, never via `${{ }}` in `run:`.
- Unclear (no routing label and no keyword) and not yet marked `needs-triage`: ONE JSON POST to the escalation webhook (`ESCALATION_WEBHOOK_URL` + `ESCALATION_BEARER` secrets, both required, https only, config via curl stdin, 10 s timeout, step `continue-on-error`, only the HTTP code is printed). Payload: `kind`, `idempotency_key` (`issue-route-<owner>-<repo>-<number>`, also sent as `Idempotency-Key` header), repo, issue number, URL, title clipped to 120 chars. After a 2xx the label `needs-triage` marks the issue, so `assigned` after `opened` does not call again. No Discord/ops message, no body, no spam.
