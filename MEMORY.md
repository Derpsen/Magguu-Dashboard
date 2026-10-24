# MEMORY.md

Helper memory for Magguu-Dashboard. Rules, design system and QA live in `AGENTS.md`.

## Hotfix (2026-10-24, 6.10.1-dev): abgeschnittene button-card-Templates

Rollback: `rollback/pre-hotfix-a25fc4b` (= `a25fc4b`, Endstand Runde 5). Tabelle ergänzt:

| Branch | zeigt auf | Bedeutung |
| --- | --- | --- |
| `rollback/pre-hotfix-a25fc4b` | `a25fc4b` | Endstand Runde 5 (6.10.0-dev) = „vor Hotfix“ |

- Lehre: ein `'` innerhalb eines YAML-Single-Quote-Strings beendet ihn; der Rest der Zeile (ab ` #`) wird still Kommentar, das YAML bleibt gültig und der Raw-Text-Regex-Check fand es nicht. In `[[[ ]]]`-Templates in Single-Quotes daher nur Doppelquotes oder Backticks im JS. `validate_button_card_js` prüft jetzt geparste Strings (Klammerpaare, Ende `]]]`).
- Dark `secondary-text-color` auf `#9da1b4` angehoben, damit der Hero-Worst-Case 4.5:1 erreicht (4.55).

## Runde 5 (2026-10-24, 6.10.0-dev): Befunde aus der Live-Prüfung von 6.9.0-dev

Rollback: `rollback/pre-round5-29338f2` (= `29338f2`, Endstand Runde 4). Tabelle ergänzt:

| Branch | zeigt auf | Bedeutung |
| --- | --- | --- |
| `rollback/pre-round5-29338f2` | `29338f2` | Endstand Runde 4 (6.9.0-dev) = „vor Runde 5“ |

(Weitere Branches: Tabellen unter Runde 4 und Runde 3.)

- System „Bereiche & Erweiterungen“: derselbe Flex-Umbruch wie in der Sicherheit (min. 150 px), damit Energie auf dem Handy vollbreit ist.
- button-card: `variables` kann beim Kaltstart kurz `undefined` sein (`reading 'accent'`). Alle JS-Templates nutzen jetzt `variables?.x`, `states?.[…]`, `entity?.…`; `validate.py::validate_button_card_js` verbietet die ungeschützten Formen. Ursache nicht im echten HA nachgestellt.
- **Kamera-Korrektur zu Runde 4:** `visibility`/conditional-card UNTERSTÜTZEN Attribute (`attribute:` an `state`/`numeric_state`, siehe `validate-condition.ts`; fehlendes Attribut = `unknown`). Für den 500er hilft das nicht: `Camera.entity_picture` (HA-Core `camera/entity.py`) liefert immer `/api/camera_proxy/<id>?token=…`, das Attribut ist also auch bei defektem Proxy gesetzt. Gewählt: Bild nur bei `streaming`/`recording` (dann gibt es einen Live-Feed), sonst kompakte Kachel mit Tipp → more-info (dort läuft die Live-Ansicht). Nachteil: ein funktionierendes Standbild im Zustand `idle` wird nicht mehr gezeigt.
- Theme-Test Wetter: gemessen über dem Hero-Verlauf; dunkel lag der Worst Case (Glow-Ecke) für Sekundärtext bei 4.28:1; im Hotfix 6.10.1-dev per hellerem `secondary-text-color` auf 4.55:1 behoben, Latte wieder 4.5.

Untested im echten HA: Flex-Umbruch System (2+1 bzw. 2+2), defensive Templates beim Kaltstart, Kamera-Kachel (Zustände streaming/idle/unavailable), Hell-Wetter-Kachel.

## Runde 4 (2026-10-24, 6.9.0-dev): Politur nach Live-Prüfung von 6.8.0-dev

Rollback: `rollback/pre-round4-4b59979` (= `4b59979`, Endstand Runde 3). Tabelle ergänzt:

| Branch | zeigt auf | Bedeutung |
| --- | --- | --- |
| `rollback/pre-round4-4b59979` | `4b59979` | Endstand Runde 3 (6.8.0-dev) = „vor Runde 4“ |

(Die übrigen Branches stehen in der Tabelle unter Runde 3.)

- HA-Sections-View ist ein reines CSS-Grid mit `grid-auto-flow: row` (kein Masonry): Sections liegen zeilenweise, eine Section mit `column_span: 1` nach einer Section mit Span 2 landet in der nächsten Zeile ganz links. Will man etwas in die rechte Spalte neben einer langen Section, muss es in dieselbe Section (Quelltext `hui-sections-view.ts` geprüft, dev-Branch).
- Flex-Umbruch (`display:flex; flex-wrap:wrap; flex: 1 1 160px` per card_mod auf `#root` des Grid-Cards) statt `auto-fit`: die letzte Kachel einer Zeile füllt den Rest.
- Kamera (in Runde 5 korrigiert: Attribute gehen, helfen hier aber nicht): Conditions/visibility prüfen nur Zustände. Offline-Ring-Kamera (`unavailable`/`unknown`) → Platzhalter-Kachel. `idle` ohne Bild (HTTP 500 auf dem Kamera-Proxy) bleibt per Config unlösbar; Ursache liegt bei Ring/Integration.
- **Befund Konsolenfehler `this._layoutElement.setConfig is not a function`** (nur Kaltstart Overview): Der Text steht in HAs `hui-view.ts` (`_setConfig`: `else { this._layoutElement.setConfig(viewConfig); }`), nicht in layout-card 2.4.7 (dort `setConfig?.()` und `_layoutElement` ist ein anderes Feld). Der Ablauf passt zu einem Ladereihenfolge-Rennen im Frontend: `sections` ist ein lazy geladener View-Typ (`LAZY_LOAD_LAYOUTS`); wird `_setConfig` auf einem noch nicht per Import definierten `hui-sections-view` ein zweites Mal aufgerufen (Neuaufbau beim Kaltstart), existiert `setConfig` noch nicht. Das Repo nutzt `custom:layout-card`/`grid-layout` in keiner View mehr (Test), die Config ist also nicht die Ursache; Fix per Config nicht möglich, Auswirkung vermutlich nur Konsole. Nicht gegen das echte HA-2026.10.2-Frontend nachgestellt (Quelltext nur dev-Branch).

Untested im echten HA: Flex-Umbruch der Sicherheits-Reihen, Szenen & Modi als Stack in der Schnellzugriff-Section (Abstände), Navbar-Padding 112 px, Wetter-Kachel hell, Kamera-Platzhalter, multiline-Untertitel.

## Runde 3 (2026-10-24, 6.8.0-dev): Layout-Feinschliff nach Live-Prüfung

Rollback: `rollback/pre-round3-ce7de7a` (= ce7de7a, Endstand Runde 2). Reverts nur ab dem neuesten Commit rückwärts.

Rollback-Branches, exakt (geprüft mit `git rev-parse`):

| Branch | zeigt auf | Bedeutung |
| --- | --- | --- |
| `rollback/pre-overhaul-fcf36c1` | `fcf36c1` | Stand vor der gesamten Überholung (6.5.x) |
| `rollback/pre-round2-2b3ae4a` | `2b3ae4a` | Endstand Runde 1 (6.6.0-dev) = strikt „vor Runde 2“ (nachträglich angelegt) |
| `rollback/pre-round2-3528f6c` | `3528f6c` | erster Commit der Runde 2, Kind von `2b3ae4a`; ändert nur CHANGELOG/MEMORY/README/`validate.py`/Tests (keine Dashboard-Inhalte) |
| `rollback/pre-round3-ce7de7a` | `ce7de7a` | Endstand Runde 2 (6.7.0-dev) = „vor Runde 3“ |

Für „vor Runde 2“ ist `2b3ae4a` formal korrekt; `3528f6c` ist inhaltlich gleich (Dashboard unverändert), enthält aber schon die README-/`validate.py`-Versionsprüfung und wäre als Rollback-Ziel dieselbe Optik.

Entscheidungen und Gründe:

- Verschachtelte `type: grid`-Karten in Sections: Standard-`grid_options.columns` ist 12 = halbe Breite einer 2-Spalten-Section (24 Spalten). Deshalb überall `columns: full`, `rows: auto` (Test). Die dreispaltigen Sicherheitsreihen bekommen zusätzlich `card_mod` `#root { grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)) !important }` (hui-grid-card setzt die Spalten über `--grid-card-column-count` im Inline-Style; Quelle geprüft, Wirkung im echten HA offen).
- Leere „umrandete Zellen“ waren leerer Rasterplatz bei ungerader Kachelzahl (der Kartenrand der stack-in-card scheint durch). Lösung: letzte Kachel außerhalb des 2-Spalten-Grids als volle Zeile; Flur bleibt (Conditional, dynamisch). Tablet-Übersicht: `modes-compact.yaml` (Span 1) füllt die rechte Spalte, `modes.yaml` (Span 2) bleibt für die Räume-Seite.
- Navbar-card: laut Karten-Doku zentriert „floating bottom“ mit Auto-Padding unten; bei `position: left` lag sie links neben dem Inhalt. Jetzt unten und auf allen Seiten inkl. Raumseiten (Test).
- Dienste: Unterseite bleibt (Funktionserhalt), Link bedingt, Hero-Untertitel „Optional“; keine Navigation.
- Light-Mode: Raumakzente per Theme-Mix statt Hex (Tokens `mag-room-accent-strength`/`-ink`, bewusst ohne Präfix `mag-accent-`, weil der Test diese als Farben liest).
- Doppelte YAML-Schlüssel: `HomeAssistantLoader.construct_mapping` in `validate.py` bricht ab.

Untested im echten HA: `auto-fit` per card_mod auf dem Sicherheits-Grid, `grid_options` auf verschachtelten Grids, Navbar unten zentriert (Padding/Überdeckung durch Medien-Leiste), vollbreite letzte Raumkachel, Szenen in der rechten Tablet-Spalte, Hell-Modus-Akzente (Abdunkelung auf 40 %), Wetter-Kürzung und Textumbruch auf dem Handy.

## Runde 2 (2026-10-24, 6.7.0-dev): Sections für alle Seiten, Light-Theme

Rollback: Branch `rollback/pre-round2-3528f6c` (zeigt auf `3528f6c`, den ersten Commit der Runde; strikt „vor Runde 2“ = `rollback/pre-round2-2b3ae4a`, siehe Tabelle in Runde 3; Tags verboten). `git revert` nur ab dem neuesten Commit rückwärts (spätere Commits bauen auf früheren auf, z. B. Sections-Dateien auf den Raum-Conditions); alles auf einmal per `git checkout rollback/pre-round2-3528f6c -- .` plus Commit.

Entscheidungen und Gründe:

- Eine Quelle der Wahrheit: `shared/sections/*.yaml`; Geräteunterschiede nur über `max_columns` (HA begrenzt `column_span` selbst auf die sichtbare Spaltenzahl, deshalb darf `column_span` > `max_columns` sein; der Validator-Check dazu wurde entfernt).
- Gehobene layout-card-Grids wurden zu Karten mit `grid_options` (je Karte `columns`), damit das Layout der Section-Breite folgt; vorhandene verschachtelte `grid`-Karten (N-up) bleiben.
- `rows: auto` auf mushroom-template/conditional/stack: HA gibt diesen Karten sonst eine feste 56-px-Zeile; `grid_options.rows` numerisch = feste Höhe (`fit-rows`), `auto` = natürliche Höhe.
- Navbar-card: als Karte in der ersten Section (Hero-Section, immer sichtbar). Doku der Karte beschreibt Sections nur knapp, feste Positionierung bleibt daher ungetestet; sicherste Variante ist die immer sichtbare erste Section mit `columns: full`, `rows: auto`.
- Überschriften: Entities-/auto-entities-Karten behalten ihre Funktion; ihr Kopf bekommt per card_mod die Schriftvariablen der Heading-Karte (`--ha-heading-card-title-*`), statt auto-entities zu ersetzen.
- Fehlende Entities werden ausgeblendet, nicht gelöscht (laut `docs/entities.md` optional/dokumentiert): `calendar.erinnerungen`, Dienste-Link (`sensor.magguu_bot_status`, `sensor.magguu_website_status`; optionales Paket), Bad-Licht, Festavia, „Tür öffnen“-Button, Lichterkette. Nur gemeldet, nicht geändert: `binary_sensor.magguu_watch_akkuwarnung` (in Templates mit Fallback sicher) und der Backup-Sensor.
- Räume-Seite: Flur + Modi als Füller; bei zwei Spalten bleibt bei ungerader Zahl eine Lücke. „Schnell starten“ kann bei sichtbarem Morgen-Conditional ungerade enden (in verschachteltem Grid nicht lösbar).
- Light-Theme: ohne `modes.light` definiert ein Dark-only-Theme im Hell-Modus nichts, die dunklen `--mag-*`-Fallbacks kollidierten mit dunkler Standardschrift (unlesbare Kacheln). Jetzt eigene Palette, Tokens identisch, Kontrast per Test.
- `section_mode` der button-card nicht genutzt (ohne Grid-Optionen = 12 Spalten, natürliche Höhe).

Untested im echten HA (nur offline validiert, 70 Tests + `validate.py`): Optik aller Sections (Spaltenumbruch, Lücken), Hero-Breite, Navbar-card in Sections, `visibility`/conditional-Verhalten, Tablet-Spans bei 3 Spalten, `.card-header`-Schrift, kompletter Light-Mode (Raumakzente: seit 6.8.0-dev per Theme-Mix), `modes.dark` unverändert erwartet.

## Overhaul 2026-10-24: Inventar, Recherche, Plan (6.6.0-dev)

Rollback: Branch `rollback/pre-overhaul-fcf36c1` (= main vor dem Umbau; Tags sind verboten). `git revert` läuft nur ab dem neuesten Commit rückwärts sauber (Commits bauen aufeinander auf, ein einzelner älterer Revert kollidiert oder bricht Folgeänderungen); alles auf einmal ohne History-Umschreiben per `git checkout rollback/pre-overhaul-fcf36c1 -- .` plus Commit.

### Inventar (Stand fcf36c1)

- Dashboards: `magguu-mobile` / `magguu-tablet` (YAML-Mode), je 15 Views per `!include_dir_merge_list views/`: Home, Räume, Klima, System, Kalender, Sicherheit, Medien, Energie, Magguu-Dienste (Subview) und 6 Raum-Subviews (Wohnzimmer, Esszimmer, Küche, Badezimmer, Schlafzimmer, Kinderzimmer). Inhalte liegen gemeinsam in `shared/cards/`, `shared/rooms/`, `shared/views/`; nur die View-Hüllen unterscheiden Mobile/Tablet.
- Layout: alle Views `type: custom:grid-layout` (layout-card, Grid-Areas + Media-Queries per `view_layout`), dazu verschachtelte `custom:layout-card` (7x). Keine nativen Sections-Views, keine View-Badges.
- Kartentypen (Anzahl grob): button-card 78 (Templates in `shared/templates/button_card.yaml`: `mag_card`, `hero_v5`, `page_header_v6`, `room_detail_header_v7`, `room_visual_v5`, `room_action_v5`, `room_link_v5`, `quick_v5`, `next_event_v5`, `waste_event_v6`), tile 43 (Features: light-brightness, target-temperature, cover-open-close/-position, toggle, media-player-*, numeric-input), mushroom-title-card 40, mushroom-template-card ~47, vertical-stack 34, conditional 22, grid 18, stack-in-card 7, mini-graph-card 7, auto-entities 3, navbar-card 1 (pro View via `shared/navbar.yaml`), plus calendar, weather-forecast, picture-entity, markdown, entities.
- Custom-Frontend-Abhängigkeiten (README): Mushroom, Button Card, Layout Card, Card Mod, Mini Graph Card, Auto Entities, Navbar Card, Stack In Card. Alle sind schon vorhanden; es kommt keine neue hinzu.
- Theme: `themes/magguu_midnight.yaml` ein Theme im Legacy-Format (Top-Level-Variablen, Basis = Standard-Light-Theme), Tokens `mag-*`.
- Packages: `packages/magguu_dashboard.yaml` (Template-Sensoren, Wartung, Version/Commit/Update-Hinweis, shell_command, Script „Dashboard aktualisieren“), optional `docs/optional/magguu_dienste.yaml`.
- Installer/Updater: `install.sh`, `update.sh`, `update-ha.sh` (Tarball, Sperre, Backup-Rotation), `scripts/install-dashboard.sh`; Tests `tests/test-install.sh`; CI validate/CodeQL/Scorecard/quality/zizmor/docs-drift.
- Prüfungen: `validate.py` (YAML, Includes, Entitäts-IDs gegen `docs/entities.md`, Sicherheits-Invarianten), 37 Unit-Tests (`tests/`, vor dem Umbau).

### Recherche (nur Verifiziertes; Stand 2026-10-24)

- Aktuelle stabile Version: Home Assistant **2026.10** (Release 2026-10-07; Frontend-Release `20260930.5`). Quellen: https://www.home-assistant.io/blog/2026/10/07/release-202610/ , https://github.com/home-assistant/frontend/releases (API `releases/latest`).
- **Sections** ist der Standard-View-Typ (Header mit Titel/Badges, Footer, Section-Hintergrund, Section-Theme, Section-Sichtbarkeit): https://www.home-assistant.io/dashboards/sections/ , https://www.home-assistant.io/dashboards/views/ . YAML-Schlüssel der View (`max_columns`, `dense_section_placement`, `top_margin`, `header`, `footer`, `sections`, `subview`, `back_path`, `visible`) und der Section (`type: grid`, `cards`, `column_span`, `row_span`, `background`, `theme`, `visibility`; `title` ist deprecated, stattdessen Heading-Karte) stammen aus dem Frontend-Quelltext `src/data/lovelace/config/view.ts` / `section.ts` (Branch `dev`, nicht der Release-Tag; deshalb nur die dort stabilen Felder nutzen).
- **Heading-Karte** (`type: heading`, `heading`, `heading_style: title|subtitle`, `icon`, `tap_action`, `badges` vom Typ `entity`/`button`): https://www.home-assistant.io/dashboards/heading/
- **Tile-Karte** (`features`, `features_position: bottom|inline`, `state_content`, `vertical`, `icon_tap_action`, `color`): https://www.home-assistant.io/dashboards/tile/ ; **Features-Liste** (u. a. `light-brightness`, `light-color-temp`, `target-temperature`, `climate-hvac-modes`, `climate-preset-modes`, `cover-open-close`, `cover-position`, `toggle`, `media-player-playback`, `media-player-volume-slider`, `media-player-source`, `numeric-input`, `select-options`, `timer-presets`, `trend-graph`, `update-actions`, `lock-commands`, `lock-open-door`, `alarm-modes`, `bar-gauge`, `temperature-forecast`, `precipitation-forecast`): https://www.home-assistant.io/dashboards/features/
- **Badges** (`entity`, `shortcut`, `entity-filter`; Sichtbarkeit per Bedingungen): https://www.home-assistant.io/dashboards/badges/ . Neu in 2026.10: Visibility-Tab kennt alle Automations-Bedingungen (Template, Sun, Zone, Device) plus Screen/User; bestehende Bedingungen bleiben gültig (Release-Blog oben). Nicht genutzt: `condition: user` braucht Marcos User-ID (nicht im Repo).
- **Themes**: `modes: {dark: …, light: …}` macht ein Theme auf dem Standard-Dark-Theme aufsetzend; das Legacy-Format (Variablen auf oberster Ebene) setzt auf dem Light-Theme auf; nur `dark` definiert → Dark wird automatisch genutzt: https://www.home-assistant.io/integrations/frontend/ (Abschnitt „Dark mode support“; Quelle `source/_integrations/frontend.markdown`). `ha-section-background-color` / `ha-section-border-radius` sind laut Sections-Doku themebar.
- Nicht verfügbar/nicht belegt: **Context7** (`user-Context7`) lieferte „Monthly quota exceeded“ (kein API-Key) → Recherche stattdessen direkt auf home-assistant.io und im Frontend-Quelltext. button-card dokumentiert kein `aria_label`/ARIA-Option (https://custom-cards.github.io/button-card/stable/ , `types.ts` ohne Treffer) → keine A11y-Behauptungen für button-card. navbar-card: Autor nutzt es in Sections-Views (https://github.com/joseluis9595/lovelace-navbar-card Discussion #55); Platzierung innerhalb einer Section ist nicht dokumentiert → **untested**.

### Entscheidungen und Plan (kleine, nacheinander revertierbare Commits)

1. `validate.py`: strukturelle Schema-Prüfungen offline (erlaubte View-/Section-Schlüssel, eindeutige View-Pfade je Dashboard, Navigationsziele existieren, Theme-Name existiert, Tile-Features gegen die verifizierte Liste, Heading-Schlüssel, Theme-Modi) + Unit-Tests. Bestehende Sicherheits-Invarianten bleiben unverändert.
2. Theme: `modes.dark` mit denselben `mag-*`-Tokens statt Legacy-Format (Basis Standard-Dark). Entscheidung: nur `dark`, weil Midnight bewusst dunkel ist; sonst würde der Profilschalter ein ungestyltes Light anbieten. **Untested** im echten HA (Optik).
3. Heading-Karten ersetzen `custom:mushroom-title-card` (40x): natives, themebares, semantisches Element ohne Custom-JS. Untertitel bleiben als `heading_style: subtitle`.
4. Sections-Pilot: die sechs Raum-Subviews (gemeinsame Datei je Raum für Mobile + Tablet) auf `type: sections` (`max_columns: 2`), jede bisherige Grid-Area wird eine Section mit Heading. Alternative (alle 30 View-Hüllen blind migrieren) verworfen: Hero-/Navbar-/Stack-in-Card-Aufbau ist ohne HA-Laufzeit nicht prüfbar; Home/Räume/System/Klima/… bleiben deshalb vorerst auf layout-card (Rest steht in TASKS.md).
5. Bewusst nicht geändert (Begründung): mini-graph-card bleibt (Mehrfach-Entity-Graphen mit Achsen; `trend-graph`-Feature ist nur ein Einzel-Sensor-Verlauf ohne Achsen), button-card-Templates bleiben (kein nativer Ersatz für Hero/Chips), kein Wechsel von Mushroom-Template-Karten (Tile braucht eine Entity).
6. Doku/Version: `6.6.0-dev` (`VERSION` + Package-Sensor gleichzeitig), AGENTS/MEMORY/CHANGELOG/README/TASKS; kein Tag.

### Ergebnis (Umsetzung, 6.6.0-dev)

- Umgesetzt wie geplant (Punkte 1–4 und 6); Reihenfolge der Commits: Plan/Recherche → `validate.py`-Schema-Checks → Theme `modes.dark` → Heading-Karten → Sections-Pilot → Docs/Version. Die Commits sind klein, aber nur ab dem neuesten rückwärts sauber revertierbar; Tests jetzt 55 (vorher 37), `validate.py` und `tests/test-install.sh` grün.
- Der Validator fand beim ersten Lauf echte Drift: `--mag-accent-danger` / `--mag-accent-media` wurden mit Fallback benutzt, waren aber nicht im Theme definiert → beide Tokens mit den Fallback-Werten ergänzt (optisch unverändert).
- Heading-Karten: 40 `mushroom-title-card` → je ein `heading_style: title` plus (falls vorhanden) ein zweites `heading_style: subtitle`. Die Heading-Karte hat kein Untertitel-Feld (Doku https://www.home-assistant.io/dashboards/heading/), daher zwei Karten. `custom:mushroom-title-card` ist im Validator nicht mehr erlaubt. In `shared/sections/hinweise.yaml` liegt die Überschrift in einer Condition → dort `vertical-stack` mit beiden Headings.
- Sections-Pilot: die sechs Raum-Subviews sind `type: sections`, `max_columns: 2`; Hero = erste Section mit `column_span: 2`; je bisherige Grid-Area eine Section; Reihenfolge entspricht der Mobile-Reihenfolge des alten Grids. Tiles, die vorher eine volle Stack-Breite hatten, bekommen `grid_options: {columns: full}`; die Wohnzimmer-Lichter (vorher 2-Spalten-Raster) bleiben bei der Tile-Standardbreite (2 pro Zeile). Entity-IDs, Bestätigungsdialoge und das `&detail_card`-Styling sind unverändert (per Diff der Entity-/Namens-/Confirmation-Menge je Datei geprüft). **Hinweis:** `docs/audit.md`/CHANGELOG 6.x nennen eine frühere Migration Sections → `custom:grid-layout` für diese Seiten; der Pilot kehrt das bewusst um (Entscheidung: nativ, weniger Custom-Abhängigkeit). Rückgängig: nur ab dem neuesten Commit rückwärts per `git revert` (Reihenfolge beachten) oder per Rollback-Branch.
- **Untested im echten HA** (nur offline validiert): Optik von `modes.dark` (Standard-Dark als Basis statt Light), Heading-Karten statt Mushroom-Titeln (Abstände in `vertical-stack` mit zwei Headings), Sections-Layout der Raumseiten (Breite/Zeilenumbruch, `grid_options: columns: full`, mini-graph-card in Sections, Mobile-Umbruch). Navbar-card wird in den umgestellten Seiten nicht benutzt (Subviews), Sections-Platzierung weiterhin ungetestet.
- Nicht gemacht (offen, siehe TASKS.md): Sections-Migration der übrigen Views (Home, Räume, Klima, System, Kalender, Sicherheit, Medien, Energie, Dienste; Navbar/Stack-in-Card-Verhalten in Sections ungeprüft), View-Badges, `condition: user` (User-ID fehlt).
- Validator-Umfang neu (`validate.py`): View-/Section-Schlüssel, eindeutige gültige View-Pfade je Dashboard, View-Typen, Theme existiert, `column_span <= max_columns`, Tile-Features gegen die verifizierte Liste, Heading-Schema, erlaubte Kartentypen (built-in + feste Custom-Liste), `navigation_path`/Navbar-Routen zeigen auf existierende Views des richtigen Dashboards, Theme-`modes`-Schlüssel, jedes `var(--mag-*)` im Theme definiert. Tests: `tests/test_dashboard_schema.py`.

## Security audit fixes (2026-10-23)

- Audit `~/security-audit-skill/magguu-dashboard/run-20261023/REPORT.md` (#1 calendar-title unsafeHTML, #2 non-admin update trigger, both needs_validation). Fixed anyway: `esc()` in `next_event_v5` (message + unparseable start_time), `waste_event_v6` label, `hero_v5` weather state + temperature/battery chips. Rest of the templates only interpolate numbers/fixed text.
- Admin gate: HA Jinja has no `is_admin`; Marco's HA user id is not in the repo → gate via admin-only core service `homeassistant.reload_custom_templates` as the first script step (HA `_async_admin_handler`: `user.is_admin` of the call context; `script.turn_on` keeps the caller's context). Card visibility not changed (core visibility only knows user ids, no admin condition); optional later: `visibility: [{condition: user, users: [<Marco-ID>]}]` once Marco supplies the id from /config/users.

- 2026-10-23 updater lock + backup rotation: `update-ha.sh` takes `flock -n` (if the binary exists; HA container not verified, Ubuntu busybox has no flock applet) else an `mkdir` lock with 10-min stale takeover; a concurrent run exits 0 with one log line and touches nothing. flock has no stale timeout (kernel releases it when the holder dies; a hung live holder is not taken over). Narrow residual race in the mkdir fallback: two runs taking over the same stale lock at the same instant. Rotation keeps the 5 newest Magguu backups (current one always kept) in `/config/backups/`, strict name pattern, real dirs only. Whole updater wrapped in `main; exit $?` because the installer overwrites the running script file. Verified under a busybox-only PATH (mkdir path).
- Code review follow-up (diffreview-20261023): `shell_command.magguu_dashboard_update` is a non-admin service, so any HA user can call it directly (WS/REST) and bypass the script's admin gate. Locked down: fixed command without templates (no service-data input), `update-ha.sh` reads no args/env (fixed `/config` + fixed repo archive; `HA_CONFIG_DIR`/`MAGGUU_DASHBOARD_ARCHIVE_URL`/`MAGGUU_DASHBOARD_SOURCE_DIR` overrides removed), enforced by `validate.py`. **Remaining risk** (only if non-admin HA users exist): such a user can still trigger the fixed update of `main` (backup + reinstall of the dashboard files, no code/args of their choice). Pending Marco's answer on whether non-admin users exist and his HA user id; then optionally hide the card per `condition: user`. Cannot be closed in YAML (HA has no per-service permission for shell_command).

## 2026-10-24 Version/commit display, update hint, full walk

- Bumped `6.4.0-dev` → `6.5.0-dev` (`VERSION`, package sensor `magguu_dashboard_version`, `tests/test-install.sh` now reads `VERSION`); no tag/release. Version lives only in those places (README/CHANGELOG text aside).
- Feature: System page card „Dashboard-Version“ shows `version · 7-char SHA` + hint. Installed SHA is stamped by the installer into `sensor.magguu_dashboard_commit` (GitHub tarball pax header `comment=<sha>` in `update-ha.sh`, `git rev-parse` for clone installs, strict 40-hex, else `unbekannt`). Main commit: REST sensor `sensor.magguu_dashboard_main_commit` (public API `commits/main`, no token, hourly, `unbekannt` on failure); `sensor.magguu_dashboard_update_hinweis` = `aktuell`/`verfuegbar`/`unbekannt`. Update script runs `template.reload` + `homeassistant.update_entity` after success (`continue_on_error`; behaviour in real HA not verified from the VM). Enforced by `validate_update_hint`; tests `tests/test_update_hint.py` (jinja2-dependent ones skip in CI because only PyYAML is installed) and `tests/test-install.sh` (git-archive tarball with real pax header, https-only check, env-injection check).
- Known limits: unauthenticated GitHub API = 60 req/h per IP (hourly poll is far below); the hint can be stale up to 1 h after a new push; the rest sensor reloads only on HA restart / `rest.reload`, a failed fetch shows `unbekannt`; an installed commit newer than main (never expected) would show `verfuegbar`. `flock` availability in the HA container is still unverified (mkdir fallback exists).
- Audit walk vs `run-20261023/REPORT.md` + `diffreview-20261023/REPORT.md`: #1 calendar XSS closed (`esc()`, tests); hardening `button_card.yaml` states escaped (verified, hero/chips use `esc()`, room pills only numbers/fixed text); backup rotation done; curl `--proto`/`--proto-redir '=https'` + `--max-time 120` / `--retry-max-time 300` added now (also keeps a run well under the 10-min stale-lock window). **Not fixed (documented):** (a) #2 non-admin users can call `shell_command.magguu_dashboard_update` directly – cannot be closed in YAML; Marco has one user (admin), accepted, card need not be user-bound; (b) pin/verify the downloaded archive (sha256 of a release tag) – needs releases, which need Marco's yes; (c) `pipx run zizmor==X` in `quality.yml` has no hash pin (pipx has no hash mode; CI-only, low); (d) flock has no stale takeover, the mkdir lock has a tiny TOCTOU race and no owner token (only if flock is missing; not triggerable by a non-admin in practice); (e) flock availability in HA unverified.
- Local checks run 2026-10-24: `python3 -m unittest discover -s tests`, `python3 validate.py`, `sh tests/test-install.sh`, shellcheck on all `*.sh` + `.githooks/*`, actionlint, zizmor 1.31.1 (medium+), osv-scanner, `tools/drift-check.sh` (CI quality.yml has no yamllint; `validate.py` is the YAML lint).
- Installed-state check (item 4): from the Ubuntu VM there is no HA `/config` mount/share and no HA token in env or repo tools; `homeassistant.local:8123` answers but `/api/` requires a token (401). So the installed commit on Marco's HA could not be read. Marco must run „Dashboard aktualisieren“ once (System page) – afterwards the new „Dashboard-Version“ card shows the installed SHA – then restart HA once (new `rest:` sensor and package changes need a restart) and reload the app.

## Knowledge refresh #1 (2026-10-23, repeat every 3 weeks)

- Dependency graph + Dependabot alerts enabled 2026-10-23 (dependency-review green). Renovate: configMigration, vulnerabilityAlerts, monthly lockFileMaintenance, npm minimumReleaseAge 3 days added. Actions behind (Renovate Monday): checkout 7.0.1, setup-python 7.1.0, codeql 4.39.1. Buddy decision same day: pip pinned by hash (requirements-dev.in → pip-compile, CI `--require-hashes`) for Scorecard #8; private vulnerability reporting on + SECURITY.md; dismissed #3/#13 (won't fix). Still open: #9 SAST, #10 SecurityPolicy (should close with SECURITY.md), #11 Fuzzing, #12 License (MIT added 2026-10-23: MagguuUI GPL-3.0 is EllesmereUI-module context, Website unlicensed → MIT; PyYAML MIT, HACS cards not bundled; copyright holder `Magguu`, owner/git identity stay Derpsen), #14 CII.

## Ownership (2026-10-12)

- **"Bot & Dashboard"** (formerly Bot Fixer) owns Magguu-Dashboard and MagguuBot (fixes, Renovate (ex-Dependabot), AGENTS/MEMORY, Notion log). "Website" (formerly Stack Fixer) covers MagguuUI-Website only.
- Results go to **Buddy** (front door) as a short German Done-State. Helpers never ask Marco directly.
- Reporting an Buddy (ab 2026-10-23): genau eine Done-Meldung pro Auftrag, max. ~800 Zeichen plus Pfad/Commit für Details; Zwischenstände nur bei Aufträgen über 30 Minuten.

## Current state (2026-10-12)

- Version: `6.6.0-dev` (`VERSION`, since 2026-10-24; was `6.5.0-dev`, davor `6.4.0-dev`). Last merges (2026-10-12 handover): #8 `279f99e` (Dependabot groups, superseded by Renovate; AGENTS refresh, absorbs #7), #9 `4e47296` (CodeQL python + actions, weekly validate). No open PRs at handover.
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

- 2026-10-23: advisory zizmor workflow `.github/workflows/zizmor.yml` added (zizmor-action v0.8.0 SHA-pinned, non-SARIF, continue-on-error, not required). Findings not fixed yet, pending Buddy review.
- 2026-10-23: first zizmor run clean (0 findings); stale `# actions/checkout@v7.0.0` comments → `v7.0.1` (SHA unchanged).

## 2026-10-22 Docs drift check

- Adopted `tools/docs-drift.sh` (1:1 from MagguuUI-Website) + `.github/docs-drift-rules.txt` + `docs-drift.yml` (Mon 05:17 UTC + dispatch; issue "Docs-Drift" → Derpsen on hits, closed when clean). No `@health-url` (no endpoint in this repo).
- Baseline fix: AGENTS.md no longer names Website live sha/digests (rule scoped to AGENTS.md; history stays in MEMORY.md "Docs/Bots-Sync"); stale "Renovate App not installed" wording fixed.
