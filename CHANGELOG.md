# Changelog

## Unreleased – CI

- Renovate: Automerge jetzt als PR (`automergeType: pr`, ohne Platform-Automerge; Renovate wartet auf alle Checks), nur patch/pin/digest und stabile (nicht 0.x) minor, 0.x-minor und Majors manuell, Gruppen nur non-major, `internalChecksFilter: strict`, 3 Tage Release-Alter auch für github-actions minor/patch und pip; `fileMatch` → `managerFilePatterns`. Gesperrte Majors unverändert.

- CI-Fehleralarm, Redaction verschärft: Log-Zeilen werden vor dem Versand auch von nackten Tokens (`ghp_`/`gho_`/`ghs_`/`github_pat_`), JWTs, URLs, Bearer-Werten und langen Hex/Base64-Strings bereinigt (nicht nur per Keyword-Zeile); Test `tests/test_ci_alarm_redact.py` führt die echte Funktion mit Fake-Werten aus.
- CI-Fehleralarm (nur Actions, kein Dashboard-Code): wiederverwendbarer Workflow `.github/workflows/ci-alarm.yml`, aufgerufen von `validate` und `quality` (nur Push auf main, nur bei `failure()`). Sendet Repo, Workflow, SHA, Run-URL und die letzten ~20 geschwärzten Logzeilen als JSON an das Repo-Secret `ESCALATION_WEBHOOK_URL` (`Authorization: Bearer` aus `ESCALATION_BEARER`, nur per env, nie ausgegeben). Leeres Secret oder kein https = stilles Überspringen, `continue-on-error`, 10 s Timeout, kein Alarm bei Re-Runs, `Idempotency-Key` = sha256(repo|workflow|sha).

## 6.10.1-dev – 2026-10-24

Hotfix zu 6.10.0-dev (Rollback-Branch `rollback/pre-hotfix-a25fc4b`, kein Tag). Offline validiert, nicht im echten HA gesehen:

- `quick_v5` (button-card): der Default `|| '#9b8cff'` stand in einem YAML-Single-Quote-String, das innere `'` beendete ihn (Rest wurde stillschweigend Kommentar), das Template war abgeschnitten, Akzent-Hintergrund und Icon-Farbe der 19 quick_v5-Kacheln fielen weg. Jetzt Doppelquotes. Es gab genau 2 betroffene Stellen (`img_cell` background, `icon` color); alle YAML-Dateien wurden geparst, weitere kaputte Templates gibt es nicht
- `validate.py` prüft jetzt die GEPARSTEN Template-Strings: `[[[`/`]]]` müssen paarweise vorkommen, ein Template muss mit `]]]` enden; zusätzlich Meldung für `variables["x"]` und `hass?.states[…]`. Tests mit gutem/schlechtem Fall
- Dark-Theme: `secondary-text-color` `#989caf` → `#9da1b4` (4.55:1 auf dem Hero-Worst-Case); WCAG-Latte im Wetter-Test wieder 4.5 für beide Modi

## 6.10.0-dev – 2026-10-24

Fünfte Runde nach Marcos Live-Prüfung von 6.9.0-dev (Rollback-Branch `rollback/pre-round5-29338f2`, kein Tag). Alles nur offline validiert, nicht im echten HA gesehen:

- System Handy, „Bereiche & Erweiterungen“: die Kacheln brechen per Flex-Umbruch um (min. 150 px); die letzte Kachel (Energie) füllt die Zeile, bei sichtbarer Dienste-Kachel 2 + 2
- button-card-JS-Templates defensiv (Kaltstart-Fehler `ButtonCardJSTemplateError: Cannot read properties of undefined (reading 'accent')`): `variables?.x`, `states?.[…]`, `entity?.…`, Default-Hex für den Raumakzent; `validate.py` meldet ungeschützte Zugriffe in `[[[ … ]]]` (Tests mit gutem/schlechtem Beispiel)
- Kinderzimmer-Kamera (`camera.kinderzimmer_live_ansicht`): Bild nur noch bei `streaming`/`recording`, sonst eine kompakte Kachel („Tippen für die Live-Ansicht“ bzw. „Kamera nicht erreichbar“, Tipp öffnet more-info). Begründung in MEMORY.md: attribute-Bedingungen gibt es zwar, `entity_picture` ist bei Kameras aber immer gesetzt und erkennt den 500er nicht
- Theme-Test Wetter-Kachel: Kontrast über dem Hero-Verlauf (Glow über `mag-surface-strong`) statt über dem Seitenhintergrund, Alpha-Minimum 0.6 und Luminanz > 0.9 im Hell-Modus; lokaler Mutationstest mit Alpha 0.3/0.5 wird rot (nicht committet)

## 6.9.0-dev – 2026-10-24

Vierte Runde (kleine Politur) nach Marcos Live-Prüfung von 6.8.0-dev (Rollback-Branch `rollback/pre-round4-4b59979`, kein Tag; Reverts nur ab dem neuesten Commit rückwärts). Alles nur offline validiert, nicht im echten HA gesehen:

- Handy Sicherheit: die dreikachligen Reihen (Hausstatus, Vordereingang, Kinderzimmer) brechen per Flex-Umbruch um; die letzte Kachel füllt die Zeile (2 + 1 volle Breite) statt halbbreit allein; Mindestbreite 160 px (auf dem Tablet nicht mehr „Letzte Ak…“)
- System: Untertitel der Bereichs-Kacheln Medien/Energie brechen um (`multiline_secondary`) statt „Wiedergabe und S…“
- Tablet-Übersicht: HA legt Sections zeilenweise ins Raster, die eigene Section „Szenen & Modi“ landete deshalb unter den Räumen in Spalte 1. Sie liegt jetzt als Stack in der Schnellzugriff-Section (rechte Spalte, gleiche Zeile wie „Wohnbereiche“); `modes-compact.yaml` entfällt. Navbar-Bottom-Padding 86 → 112 px (Medien-Leiste 90 → 118), live waren nur ~7 px Abstand
- Hell-Modus: Wetter-Kachel im Hero nutzt das neue Theme-Token `mag-weather-surface` (hell: weiß, 72 %) statt des Overlay-Grautons; WCAG-Test deckt Text darauf ab. Küche: Raumkarte nutzt wie die anderen Räume das Standard-Label (Beschreibungs-Override entfernt); eine Farbhervorhebung von „Licht“ war in den Vollbild-Screenshots nicht nachweisbar (vermutlich Skalierungsartefakt)
- Kinderzimmer-Kamera (`camera.kinderzimmer_live_ansicht`): bei `unavailable`/`unknown` erscheint statt des kaputten Bildes (HTTP 500) eine Kachel „Kamera nicht erreichbar“. Gewählt, weil Conditions nur den Zustand prüfen können; `idle` ohne Bild lässt sich nicht erkennen (dann bleibt die Kamera sichtbar, Dokumentation in MEMORY.md)
- Konsolenfehler `this._layoutElement.setConfig is not a function` beim Kaltstart: Befund in MEMORY.md (stammt aus dem HA-Frontend `hui-view`, nicht aus layout-card; keine Config-Änderung nötig/möglich)
- Version `6.9.0-dev`; Tests jetzt 86

## 6.8.0-dev – 2026-10-24

Dritte Runde nach Buddys Prüfung von 6.7.0-dev im echten HA (Rollback-Branch `rollback/pre-round3-ce7de7a`, kein Tag; Reverts nur ab dem neuesten Commit rückwärts). Alles nur offline validiert (Unit-Tests, `validate.py`), nicht im echten HA gesehen:

- Übersicht: Raumkarten mit ungerader Kachelzahl enden mit einer vollbreiten Kachel statt einer leeren Zelle (Wohnzimmer Soundbar, Esszimmer Heizung, Küche, Schlafzimmer Heizung; Flur hat eine dynamische Anzahl). Auf dem Tablet liegt „Szenen & Modi“ (`shared/sections/modes-compact.yaml`, eine Spalte) in der freien rechten Spalte; die Räume-Seite nutzt weiter die zweispaltige `modes.yaml` als Füller (beide teilen `modes-cards.yaml`)
- Handy: Wetter-Karte kürzt lange Zustände, Kachel-Texte der button-card brechen um bzw. werden mit `min-width: 0`/Ellipsis begrenzt (Wettertitel, „5km run Decksteiner“), System-Untertitel gekürzt („Wiedergabe und Szenen“, „Verbrauch und Messquellen“)
- Sicherheit/System: verschachtelte Grid-Karten hatten Standardbreite 12 und füllten in 2-Spalten-Sections nur die Hälfte; jetzt `grid_options.columns: full`, die dreispaltigen Kachelreihen in Sicherheit passen sich per `auto-fit` (min. 140 px) an („Letzte A…“, „Lautstär…“ entfallen). Test sichert alle verschachtelten Grids ab
- Navbar-card: unten zentriert (`desktop.position: bottom`, floating) statt links neben dem Inhalt, und in der ersten Section aller Seiten inkl. der sechs Raumseiten (einheitlich)
- Dienste: bleibt optionale Unterseite (nicht in der Navbar, Link nur sichtbar, wenn das Paket `docs/optional/magguu_dienste.yaml` Sensoren liefert); Hero-Untertitel markiert sie als „Optional“. Begründung: ein View lässt sich nicht per Entitätszustand ausblenden, Löschen würde die Funktion verlieren
- System: „Nicht erreichbar“ ignoriert `light.badezimmer_licht_bad` und `light.sonstiges_festavia_string_lights` (optional/dauerhaft unavailable); Backup-Karte zeigt bei `unknown` „Noch kein Backup“
- Räume-Seite: Abschnitt „Szenen & Modi“ (`shared/sections/raeume.yaml`, Füller mit den Modi-Kacheln aus Runde 2) ist hier nachgetragen
- Doppelter `card_mod`-Schlüssel in `shared/rooms/schlafzimmer.yaml` entfernt (der zweite überschrieb den ersten still); `validate.py` lehnt doppelte YAML-Schlüssel jetzt ab (Merge-Keys/Anker erlaubt)
- Theme: Raumakzente (Hex wie `#ffd166`, ca. 1,5:1 auf Weiß) laufen im Hellmodus über `mag-room-accent-strength`/`-ink` (Mischung zum Text-Ton); Dunkelmodus unverändert (100 %). WCAG-Test prüft alle verwendeten Akzent-Hex in beiden Modi (≥ 4,5:1 auf Karte und Seite)
- Version `6.8.0-dev`; Tests jetzt 83

## 6.7.0-dev – 2026-10-24

Zweite Runde nach Marcos Prüfung im echten HA 2026.10.2 (Rollback-Branch `rollback/pre-round2-3528f6c`, kein Tag; Reverts nur ab dem neuesten Commit rückwärts):

- Alle neun Seiten (Home, Räume, Klima, System, Kalender, Sicherheit, Medien, Energie, Dienste) in Mobile und Tablet sind native `type: sections`-Views; die Inhalte liegen einmal in `dashboard/magguu-dashboard/shared/sections/` (Mobile `max_columns: 1`, Tablet `max_columns: 3`, `column_span` wird von HA automatisch auf die sichtbare Spaltenzahl begrenzt). `custom:grid-layout`/`layout-card` werden nicht mehr benutzt (Handy-Überlauf durch das Grid-Layout entfällt)
- Hero ist breit über alle Spalten (`grid_options.columns: full`), Navbar-card liegt als Karte in der ersten (immer sichtbaren) Section mit `grid_options` full/auto (feste Positionierung in Sections im echten HA ungetestet; Alternative wäre eine eigene Section am Ende)
- Karten mit `rows`-Standardhöhe (mushroom-template, conditional, stack) bekommen `rows: auto`, damit nichts bei 56 px abgeschnitten wird; `validate.py` erzwingt das
- Überschriften der Entities-/auto-entities-Karten (Updates, Batteriewarnungen, Nicht erreichbar, Klingel-Lautstärke) nutzen per card_mod die Schrift der Heading-Karten; Szenen-Untertitel gekürzt, `quick_v5`-Labels brechen um, Telefonnamen kürzer
- Fehlende Entities blenden sich aus statt Fehler zu zeigen: `calendar.erinnerungen`, Dienste-Link/-Karten, Bad-Licht, Festavia, „Tür öffnen“, Lichterkette (Conditions/`visibility`, kein Konsolenfehler); leere Zellen mit Füllkarten (Modi) geschlossen
- Theme: `modes.light` ergänzt (helle Palette, dieselben `mag-*`-Tokens); `modes.dark` optisch unverändert. Fest verdrahtete dunkle Flächen/Pill-Farben in den button-card-Templates laufen jetzt über Tokens (`mag-surface-strong`, `mag-overlay`, `mag-overlay-border`, `mag-hero-glow`, `mag-accent-*`). WCAG-AA per Rechnung (`tests/test_theme.py`: Text ≥ 4,5:1, Akzente ≥ 4,5:1, Zustandsfarben ≥ 3:1, Dark/Light-Parität)
- Tile-Features (Helligkeit, Rollladen-Position, Zieltemperatur) per Test abgesichert; Heizungen auf der Klima-Seite mit Zieltemperatur-Feature
- Version `6.7.0-dev`; README-Version wird von `validate.py` geprüft; Tests jetzt 70

## 6.6.0-dev – 2026-10-24

- Überholung auf den Stand Home Assistant 2026.10 (kleine Commits, Reverts nur ab dem neuesten rückwärts; Rollback-Branch `rollback/pre-overhaul-fcf36c1`, kein Tag):
  - `validate.py` prüft offline die Dashboard- und Theme-Struktur (View-/Section-Schlüssel, eindeutige View-Pfade, Navigationsziele, Theme-Name und `modes`, Tile-Features, Heading-Karten, erlaubte Kartentypen, `column_span`, definierte `--mag-*`-Tokens); 18 neue Unit-Tests (`tests/test_dashboard_schema.py`), insgesamt 55
  - Theme „Magguu Midnight“ nutzt `modes.dark` (Standard-Dark als Basis, sonst unveränderte `mag-*`-Tokens); `mag-accent-danger` und `mag-accent-media` ergänzt (waren nur als Fallback verwendet) – Optik im echten HA ungetestet
  - 40 `custom:mushroom-title-card` durch native Heading-Karten ersetzt (Titel + Untertitel als zwei Heading-Karten); Mushroom-Titelkarte nicht mehr erlaubt
  - Die sechs Raumdetailseiten (Mobile + Tablet gemeinsam) nutzen native Sections (`max_columns: 2`, Hero über zwei Spalten, eine Section je Bereich); Entitäten, Bestätigungsdialoge und Funktionen unverändert, Layout im echten HA ungetestet. Kehrt die frühere Umstellung Sections → `custom:grid-layout` nur für diese Seiten bewusst um
  - Version `6.6.0-dev` (`VERSION` + Package-Sensor)
- Update: „Dashboard aktualisieren“ ausführen, HA neu laden bzw. Browser/App neu laden (Theme neu laden)

## 6.5.0-dev – 2026-10-24

- Neu: Die System-Seite zeigt unter „Dashboard-Version“ die installierte Version samt Commit-SHA (7 Zeichen) und einen Update-Hinweis (aktuell / neuer Stand auf main / unbekannt). Der Installer (`update-ha.sh`, `install.sh`) stempelt die SHA in `sensor.magguu_dashboard_commit`; `sensor.magguu_dashboard_main_commit` fragt höchstens stündlich die öffentliche GitHub-API ab (ohne Token/Secret, bei Fehlern „unbekannt“ statt Fehlermeldungen). Nach einem erfolgreichen Update lädt das Script die Template-Sensoren neu und aktualisiert den main-Commit. `validate.py` erzwingt den Aufbau (feste URL, keine Secrets, mindestens 3600 s Intervall, SHA-Format, Fallbacks)
- Version auf `6.5.0-dev` angehoben (`VERSION`, Package-Sensor, Test); `validate.py` prüft das Format `X.Y.Z[-dev]`
- Updater: Download nur per HTTPS (`--proto`/`--proto-redir =https`) und mit Zeitlimit (`--max-time 120`, `--retry-max-time 300`), damit ein Lauf die 10-min-Sperrgrenze nicht erreicht; `validate.py` erzwingt das
- Sicherheit (seit 6.4.0-dev, siehe unten): HTML-Escaping in button-card-Templates, Admin-Gate für „Dashboard aktualisieren“, gehärteter `shell_command` + Updater, Update-Sperre + Backup-Rotation, zizmor-Workflow, shellcheck-Fixes (SC1007, SC2317)
- Updater: Sperre gegen Parallelläufe (`flock`, sonst `mkdir`-Lock mit 10-min-Stale-Übernahme; zweiter Lauf endet mit Exit 0 ohne Wirkung) und Backup-Rotation (nur die 5 neuesten `magguu-dashboard-YYYYMMDD-HHMMSS`-Backups in `/config/backups/`, andere Dateien bleiben unberührt)
- Sicherheit: `shell_command.magguu_dashboard_update` bleibt ein fester Befehl ohne Templates; `update-ha.sh` liest keine Argumente/Umgebungsvariablen mehr (feste Pfade, festes Repo-Archiv). `validate.py` prüft beides
- Sicherheit: Kalendertitel, nicht parsebare Startzeiten und Wetter-/Sensor-States in button-card-Templates werden HTML-escaped (kein Markup aus Kalendern/Entities mehr; Darstellung für normalen Text unverändert)
- Sicherheit: „Dashboard aktualisieren“ nur noch für HA-Admins (erster Script-Schritt ist der admin-only Core-Service `homeassistant.reload_custom_templates`; Nicht-Admins scheitern mit Unauthorized, bevor etwas geändert wird)
- CI: beratender zizmor-Workflow (`.github/workflows/zizmor.yml`, blockiert nie, kein Required Check)
- Neue Unterseite „Magguu-Dienste“ (Mobile + Tablet über ein gemeinsames Include, Einstieg von System): Website-Status, MagguuBot-Uptime/Build, letzter Docker-Deploy (Bot + Website) und letzter Bot-Webhook je Quelle. REST-Sensoren als optionales Paket `docs/optional/magguu_dienste.yaml` (nur `!secret`, TODO in `docs/entities.md`); Website-`/api/status` steht noch aus, vorläufig `/api/health`
- Dependabot durch Renovate ersetzt (`renovate.json`: Montag, Europe/Berlin, Gruppen github-actions/pip, Automerge nur Minor/Patch nach grüner CI)
- Dependabot-Gruppen (github-actions, pip); AGENTS.md auf Stand 2026-10-12 (u. a. Whisper Messenger, übernimmt PR #7)

- Mobile-/Tablet-View-Shells: Navbar-Clearance und schmale max-width auf Theme-Tokens (--mag-space-navbar-clearance, --mag-content-max-width-narrow); Overview-Reststyles auf Surface/Border-Tokens; Validator sichert Shell-Token-Vertrag
- Home-Overview Mobile/Tablet: Layout-Abstände und max-width auf Theme-Tokens (--mag-space-page-*, --mag-content-max-width) mit denselben Fallbacks wie die übrigen Views
- Licht, Klima, Rollläden, Medien und Schalter nutzen HA-Tile-Cards statt Bubble/Mushroom-Spezialkarten (HA 2026.8 / Mushroom 5)
- OpenCCU-Servicemeldungen zeigen den Gerätetext; Sabotage wird ignoriert (defekter Kontakt, Fehlalarme)
- Homematic-Batterien aller Räume, iPhone, Watch, Klingel und Kamera sind in der Wartung und den Batteriewarnungen
- Mobile-Home zeigt die Küche und denselben Schnellzugriff wie das Tablet (Licht, Rollläden auf/zu, Fernseher)
- Räume-Seite steuert Flur, Lichterkette und sonstige Lichter
- Lichtzähler nutzt `group.magguu_alle_lichter` statt einer unvollständigen Teilliste
- Wohnzimmer- und Küchen-Öffnungen fallen auf die dokumentierten Binärsensoren zurück; ein fehlender Sensor macht den Raum nicht mehr komplett unsichtbar
- Durchschnittstemperatur und -luftfeuchte sind `unavailable`, wenn keine Messwerte vorliegen, statt `0`
- Klingel- und Kamera-Akkus unter 20 % zählen zur Wartung und erscheinen in den Batteriewarnungen
- 7-Tage-Kalender enthält `calendar.erinnerungen`
- Home-Overview: Wohnzimmer/Esszimmer/Küche über gemeinsame Raumkarten-Includes statt Inline-Duplikate
- Navbar um Medien und Energie ergänzt (Views waren schon vorhanden)
- `VERSION` als Versionsquelle; Package-Sensor und Validator bleiben synchron
- `docs/audit.md` als historischer Snapshot gekennzeichnet
- `install.sh` ergänzt fehlende packages/themes/lovelace-Blöcke in `configuration.yaml` per Merge mit Backup, ohne vorhandene Keys zu überschreiben

- POSIX-`install.sh` und `update.sh` ohne Bashisms; HA-OS-ash-tauglich
- Ring verdrahtet: Klingel Vordereingang (`event.*`, Türöffnen mit Bestätigung) und Kinderzimmer-Kamera
- README: primärer Updateweg ist die System-Aktion (Tarball); Git-`update.sh` nur optional mit Klon
- `CODEX_MASTER_PROMPT.md` entfernt; AGENTS/Buddy bleibt die einzige Arbeitsquelle
- README-Updatepfade zu einem Abschnitt „Aktualisieren“ zusammengeführt (`update.sh` oder System-Seite)
- klargestellt: YAML+Packages-Layout ist kein HACS-Dashboard
- unverdrahtete Nuki-, Unraid-, Plex- und AdGuard-Platzhalterkarten ausgeblendet; `docs/entities.md` listet sie ehrlich als nicht verdrahtet
- Nuki-Entriegeln-Bestätigung als Confirm-Muster vorbereitet (ohne Fake-Entity-IDs)
- gemeinsame, POSIX-kompatible Installationslogik für Erstinstallation und Self-Update eingeführt
- lokale Regressionstests für Installation, Legacy-Migration, Backup und Update ergänzt
- Dashboard-Prüfung um Include-Ziele und nicht dokumentierte Entitätsreferenzen erweitert
- reproduzierbare Python-Testabhängigkeit und Unit-Tests für den Validator ergänzt

## 6.4.0-dev – 2026-07-23

- priorisierte „Jetzt wichtig“-Karte für Alarm, Abwesenheit, Heizverlust, Wetter, Abfuhr, Geräte, Akku, Updates und Öffnungen ergänzt
- gemeinsamen Sicherheitsstatus und eine eigene responsive Sicherheitsseite für Mobile und Tablet eingeführt
- Wartungszähler aus Updates, OpenCCU-Meldungen, nicht erreichbaren Geräten und Akkustatus ergänzt
- Systemseite um zentrale Einstiege für Sicherheit, Medien, Energie sowie vorbereitete Server- und Netzwerkdienste erweitert
- eigene Medienseite mit Soundbar, sicheren Steckdosenaktionen, Filmabend und Gaming ergänzt
- Energie-Einstiegsseite mit direkter Navigation zum integrierten Home-Assistant-Energie-Dashboard ergänzt
- Ring, Nuki, Plex, Unraid, Docker, AdGuard und Energiemessung ohne erfundene Entitäten als noch nicht verbundene Erweiterungen gekennzeichnet
- kontextabhängige Morgenroutine sowie Modi für Kochen, Besuch und Gaming ergänzt
- alte, doppelte Einzelwarnkarten durch die zentrale Prioritätslogik ersetzt

## 6.3.0-dev – 2026-07-23

- bedingten Medienbereich mit Wiedergabe- und Lautstärkesteuerung ergänzt
- Abfuhrkarte erkennt Bio-, Wertstoff-, Papier-, Rest- und Glasmüll und passt Icon sowie Farbe an
- alle sechs Raumdetailseiten auf einen gemeinsamen Statuskopf mit Klima, Licht und Öffnungen umgestellt
- doppelte Statuskarten aus den Raumdetailseiten entfernt und die vorhandenen Bedienbereiche beibehalten
- Heizverlust und nicht verfügbare Öffnungssensoren direkt im Raumheader hervorgehoben

## 6.2.0-dev – 2026-07-23

- sichere Modi für Gute Nacht, Haus verlassen und Filmabend ergänzt
- Rollläden in Szenen werden bei geöffneten Fenstern raumweise übersprungen
- nicht verfügbare Öffnungssensoren werden sicher als ungeklärt statt als geschlossen behandelt
- situative Wetter-, iPhone-Akku- und Abwesenheitswarnungen ergänzt
- Warnkarten dezent animiert und `prefers-reduced-motion` berücksichtigt
- gemeinsame Modus- und Heizwarnkarten für Mobile, Tablet und Klima eingeführt

## 6.1.0-dev – 2026-07-23

- Abfuhrkarte um Countdown und Hervorhebung für „heute“ und „morgen“ erweitert
- situative Warnungen für gleichzeitig geöffnete Fenster und aktiv heizende Thermostate ergänzt
- Dashboard-Updater zeigt nun Version, aktuellen Status und Zeitpunkt der letzten erfolgreichen Aktualisierung

## 6.0.0-dev – 2026-07-16

- Systemseite nach dem Overview-Prinzip in Status, kompakte Hinweise und gleich große Verwaltungskarten gegliedert
- Bereich „Medien & Raumklima“ von der Tablet-Home-Seite entfernt
- irreführenden roten Lichtzähler-Badge an der Räume-Navigation entfernt
- Tablet-Wetter kompakt rechts in die Begrüßungskarte integriert und Schnellzugriff sowie Hinweise nach oben verschoben
- Luftfeuchtigkeit in den Raumkarten größer und kontrastreicher dargestellt
- Raumkarten visuell verdichtet und Klimawerte ruhiger in den Kartenkopf integriert
- verschachtelte responsive Raster auf die korrekte Layout-Card-Syntax migriert, damit Systemstatus, Dashboard-Updater, Klima-, Kalender- und Raumkarten zuverlässig dargestellt werden
- Temperatur und Luftfeuchtigkeit als gut sichtbare Klima-Anzeige direkt in die Raumkarten integriert
- Klima, Kalender und System auf gemeinsame responsive Inhaltsmodule umgestellt
- alle sechs Raumdetailseiten vom alten Sections-Layout auf das moderne Midnight-Raster migriert
- einheitliche Seitenheader, Inhaltsbreiten, Abstände und Breakpoints für Mobile, Tablet und Desktop ergänzt
- Rooms-Seite an den neuen Seitenheader angeglichen
- Home und alle Hauptseiten auf eine gemeinsame relative Navbar umgestellt und doppelte Navbar-Dateien entfernt
- Klima um kompakte Kennzahlen, Öffnungshinweise und gemeinsame Temperatur-/Luftfeuchteverläufe erweitert
- Kalender um gemeinsame nächste Termine und eine 7-Tage-Agenda erweitert
- fehleranfällige Clock-Weather-Card auf der Home-Seite durch die eingebaute Wettervorhersage ersetzt
- offene Fenster und Türen auf Mobile und Tablet einzeln anklickbar gemacht
- Bestätigungen für hausweite Licht- und Rollladenaktionen ergänzt
- Bestätigungen für Fernseher- und Computer-Steckdosen an allen Bedienpunkten ergänzt
- direkte Rollladen-Toggles auf der Home-Seite durch sichere Detailbedienung ersetzt
- technische Pfade vollständig von `magguu-flux`/`magguu_flux.yaml` auf `magguu-dashboard`/`magguu_dashboard.yaml` migriert
- bestehende Installationen werden inklusive `configuration.yaml` automatisch und mit Backup auf die neuen Pfade umgestellt
- sicheren Dashboard-Updater mit Bestätigung, Backup und Ergebnismeldung auf der System-Seite ergänzt
- containerkompatibles Update über `curl`, `tar` und POSIX `sh` ergänzt
- Phase 2: zentrale Design-Tokens für Flächen, Farben, Abstände, Radien und Schatten ergänzt
- Phase 2: Room-Header und Room-Actions auf defensive gemeinsame Templates umgestellt
- Phase 3: Mobile und Tablet auf eine gemeinsame Rooms-Kartenbasis migriert
- Phase 3: sechs große Raumkarten mit Status, Warnungen, Lichtzähler und beschrifteten Direktaktionen umgesetzt
- gemeinsame relative Navbar für die Rooms-Seite ergänzt
- generierte Package-Entitäten in der verbindlichen Entitätsdokumentation ergänzt
- Phase-1-Audit mit Architektur-, Abhängigkeits- und Migrationsübersicht ergänzt
- drei fehlerhafte Referenzen auf Öffnungs-Template-Sensoren korrigiert
- nicht dokumentierten Leistungsgraphen aus Mobile und Tablet entfernt
- funktionierenden V5-Stand als Repository-Basis übernommen
- Codex-Regeln in `AGENTS.md` ergänzt
- verifizierte Entitätsliste angelegt
- Designbriefing und Roadmap ergänzt
- GitHub-taugliche Installations- und Update-Skripte hinzugefügt
- automatischen YAML-Basischeck ergänzt
- vollständigen Codex-Master-Prompt beigefügt

## 5.0.0

- Midnight Theme
- neue Home- und Rooms-Basis
- Kalenderintegration
- responsive Mobile- und Tablet-Ansichten
