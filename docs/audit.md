# Phase-1-Audit

Stand: 2026-07-16

## Kurzfazit

Der V5-Stand ist eine grundsätzlich schlüssige YAML-Basis mit getrennten Mobile- und Tablet-Dashboards, gemeinsam eingebundenen Raumdetailseiten, einem zentralen Button-Card-Template, einem Home-Assistant-Package und einem Theme. Die Include-Ziele existieren und die Navigation der aktiven Mobile-Hauptseiten ist konsistent. Die größten Wartungsrisiken liegen in den fast vollständig duplizierten Hauptansichten, umfangreichen Inline-Stilen und JavaScript-Templates sowie einer nicht vollständig dokumentierten Abhängigkeits- und Entity-Grenze.

Eine visuelle Neugestaltung wurde in Phase 1 nicht begonnen. Unmittelbar defekte Referenzen wurden klein und nachvollziehbar korrigiert.

## Architekturüberblick

- `dashboard/magguu-dashboard/mobile/` und `tablet/` sind eigenständige Lovelace-Einstiege. Beide laden gemeinsame Button-Card-Templates und ihre Views über `!include_dir_merge_list`.
- Die sechs Raumdetailseiten unter `shared/rooms/` werden von Mobile und Tablet gemeinsam eingebunden. Das ist die derzeit stärkste Wiederverwendung im Repository.
- Die Hauptseiten Overview, Räume, Klima, System und Kalender existieren dagegen je Gerätetyp separat. Klima und System sind nahezu identisch; Räume unterscheiden sich hauptsächlich durch Layout und Navigationspfade; Overview weist erhebliche inhaltliche Abweichungen auf.
- `packages/magguu_dashboard.yaml` definiert Gruppen, globale Aktionen, normalisierte Temperaturwerte, Zähler und kombinierte Öffnungssensoren.
- `shared/templates/button_card.yaml` bündelt sechs UI-Templates, enthält aber zugleich viele feste Maße, Inline-Farben und längere JavaScript-Ausdrücke.
- `themes/magguu_midnight.yaml` stellt eine gute Midnight-Basis bereit, deckt aber Abstände, Typografie, Schatten, Statusflächen und responsive Tokens noch nicht zentral ab.

## Include- und Dateistruktur

- Alle gefundenen skalaren `!include`-Ziele existieren.
- Mobile bindet die Navbar in allen fünf Hauptansichten ein; Raumdetails sind Subviews ohne Navbar.
- Tablet bindet seine vorhandene `cards/navbar.yaml` derzeit nirgends ein. Die Datei ist daher aktuell toter bzw. vorbereiteter Code.
- Die Tablet-Navbar enthält keine Kalenderroute, obwohl eine Tablet-Kalenderansicht existiert.
- Die Include-Wrapper der Raumdetails sind bewusst minimal und für Mobile und Tablet identisch.
- Der Ordner `Magguu-Dashboard` ist in der aktuellen Workspace-Struktur kein eigenständiges Git-Repository. Das übergeordnete `.git` ist nicht als gültiges Repository nutzbar; dadurch sind Status- und Diff-Prüfungen gegen einen Commit-Bestand derzeit nicht möglich.

## YAML und Validierung

- `validate.py` lädt alle `.yaml`- und `.yml`-Dateien mit einem Loader, der Home-Assistant-Tags toleriert. Das ist ein sinnvoller Basissyntaxcheck, prüft aber weder Include-Semantik noch Lovelace-Schema, Template-Ausführung oder Entity-Existenz.
- Der vorgeschriebene Aufruf `python validate.py` wurde versucht. Auf dem Audit-System verweist `python.exe` nur auf den Microsoft-Store-Alias; eine Python-Laufzeit und der `py`-Launcher sind nicht installiert. Der Validator konnte deshalb lokal nicht ausgeführt werden.
- Ein separater statischer Include-Zielcheck war erfolgreich.
- Die Dateien selbst sind gültig als UTF-8 lesbar. Falsch dargestellte Umlaute in der PowerShell-Standardausgabe sind ein Terminal-Encodingproblem, kein nachgewiesener Dateischaden.

## Entity-Audit

`docs/entities.md` wurde als verbindliche Quelle verwendet. Repository-eigene `sensor.magguu_*`, `binary_sensor.magguu_*`, Scripts und die Lichtgruppe werden aus `packages/magguu_dashboard.yaml` erzeugt und sind damit nachvollziehbar.

Gefundene und in Phase 1 behobene Referenzfehler:

- Wohnzimmer, Schlafzimmer und Kinderzimmer verwiesen in den gemeinsamen Detailseiten auf `binary_sensor.magguu_*_offnung`. Das Package erzeugt anhand der dokumentierten Namen und `unique_id` jeweils `binary_sensor.magguu_*_oeffnung`.
- Mobile und Tablet verwendeten vier Leistungssensoren, die weder in `docs/entities.md` dokumentiert noch im Package definiert waren. Der ausschließlich daraus bestehende Verbrauchstab wurde entfernt. Er kann nach Dokumentation echter IDs wieder ergänzt werden.

Risiken:

- Generierte Package-Entitäten fehlen in `docs/entities.md`. Eine eigene Sektion „vom Repository erzeugt“ würde den Abgleich eindeutig machen.
- Template-Sensoren behandeln `unknown` und `unavailable` meist defensiv, aber der Durchschnitt liefert bei vollständig fehlenden Daten `0`; das kann wie eine reale Messung wirken.
- Öffnungszustände mischen Binärsensoren und Stringsensoren. Weitere reale Zustandsvarianten müssen anhand von Home Assistant verifiziert werden.
- Ring, Nuki, Unraid, Plex und AdGuard werden richtigerweise noch nicht referenziert.

## Custom-Card-Abhängigkeiten

Tatsächlich verwendet werden:

- Mushroom Cards
- Bubble Card
- Button Card
- Layout Card (`custom:grid-layout`)
- Card Mod
- Mini Graph Card
- Auto Entities
- Navbar Card
- Clock Weather Card
- Simple Tabs Card
- Stack In Card

`Stack In Card` wird im README nicht unter den Voraussetzungen genannt. Umgekehrt sollte die spätere Installationsprüfung sicherstellen, dass jede aufgeführte Abhängigkeit tatsächlich erforderlich und als Frontend-Ressource registriert ist. Eine neue Abhängigkeit ist für Phase 2 oder 3 nicht nötig.

## Mobile-/Tablet-Abweichungen und Duplikate

- Klima und System sind praktisch doppelt gepflegt; bereits kleine Unterschiede zeigen Drift-Risiko.
- Die Räume-Seiten duplizieren sechs große Kartenblöcke sowohl innerhalb einer Datei als auch zwischen Mobile und Tablet. Das bestehende `room_card_v5` abstrahiert nur den Kopf, nicht Aktionen und Layout.
- Overview ist auf Tablet deutlich umfangreicher als auf Mobile. Einige Unterschiede sind sinnvoll, andere sind strukturelle Duplikation derselben Kartenlogik.
- Kalender besitzt getrennte Layout-Hüllen bei weitgehend gleicher Datenbasis.
- Die beiden Navbar-Dateien unterscheiden sich neben den URL-Präfixen auch funktional: Tablet hat keine Kalenderroute. Da die Tablet-Datei nicht eingebunden ist, bleibt die beabsichtigte Navigation unklar.

## Designsystem, Responsive Verhalten und Darstellung

- Positiv: maximale Inhaltsbreiten von 1320 bis 1460 px und Breakpoints für Tablet-Layouts verhindern extrem breite Inhaltskarten.
- Kritisch: Radien, Hintergründe und Borders werden vielfach inline wiederholt. Änderungen am Designsystem würden zahlreiche Dateien betreffen.
- `button_card.yaml` nutzt feste Höhen, Breiten, Offsets und Fontgrößen. Besonders die Raumillustration mit absolut positionierten Pixelmaßen ist bei vergrößerter Schrift und schmalen Geräten fragil.
- Mobile-Hauptansichten reservieren mit 92 bis 96 px ausreichend Platz für Bottom Navigation; die tatsächliche Navbar nutzt zusätzlich Auto-Padding. Doppelte Polsterung sollte visuell geprüft werden.
- Der 768-px-Wechsel der Navbar und die Layout-Breakpoints 680/760/850/950/1050/1080 px sind nicht zentral abgestimmt.
- Temperaturwerte werden im Package nach Celsius normalisiert. Die Prüfung auf Fahrenheit berücksichtigt nur `°F` und `F`; unbekannte Einheiten werden unverändert als Celsius ausgegeben. Das sollte in einer späteren Klima-Phase defensiver werden.

## Bedienbarkeit und Barrierefreiheit

- Direkte Aktionen besitzen meist ausreichend hohe Karten, klare Icons und Hold-Aktionen für Details.
- Mehrere kleine Room-Actions liegen in Drei- oder Vier-Spaltenrastern. Auf schmalen Smartphones müssen reale Touch-Ziele, Abstände und Beschriftungsumbruch geprüft werden.
- Die großen Room-Header navigieren als Ganzes; Aktionen liegen außerhalb davon. Das reduziert versehentliches Auslösen, benötigt aber noch einen expliziten visuellen Navigationhinweis und Fokusprüfung.
- Aktive Farben sind verständlich, doch Zustände werden teilweise primär über Farbe kommuniziert. Text/Icon-Varianten und Kontrast sollten geprüft werden.
- Für Custom Cards ist keine dokumentierte Tastatur-, Screenreader- oder Reduced-Motion-Prüfung vorhanden.

## Performance- und Wartungsrisiken

- Viele JavaScript-Templates greifen wiederholt auf `states` zu. Für sechs Räume ist das noch überschaubar, sollte aber nicht weiter kopiert werden.
- `mini-graph-card` mit 48 Stunden und mehreren Ansichten erhöht Frontendarbeit; nur sichtbare, entscheidungsrelevante Graphen sollten bleiben.
- Umfangreiche Inline-CSS-Blöcke und `color-mix()` erschweren zentrale Anpassungen und können auf älteren WebViews unterschiedlich wirken.
- Größte Dateien sind Tablet-Overview (421 Zeilen), Tablet/Mobile-Räume (368/361), Package (303) und Button-Templates (276). Weitere Erweiterung ohne Zerlegung würde die Wartbarkeit verschlechtern.

## Priorisierte Verbesserungen

1. Design-Tokens im Theme ergänzen und wiederholte Card-Mod-Werte darauf umstellen.
2. Eine gemeinsame Room-Card-Architektur definieren, die Kopf und Aktionsraster abdeckt; raumspezifische Entities bleiben deklarative Variablen.
3. Mobile und Tablet für Klima, System und Kalender auf gemeinsame Content-Includes mit kleinen Layout-Hüllen umstellen.
4. Generierte Package-Entitäten dokumentieren und den Entity-Check automatisieren.
5. Navbar-Strategie für Tablet festlegen und Kalenderroute konsistent machen.
6. Responsive Maße, Touch-Ziele, Kontrast und Zustandsdarstellung auf echten Gerätebreiten testen.
7. Erst danach Home, Kalender, Klima und zusätzliche Module modernisieren.

## Migrationsplan für Phase 2 und Phase 3

### Phase 2 – Designsystem und Architektur

1. Semantische Theme-Variablen für Surface, Surface-raised, Border, Text, Licht/Klima/Warnung/Fehler, Radius, Schatten und Standardabstände ergänzen.
2. Bestehende Button-Templates auf diese Tokens umstellen, ohne ihre Funktion oder Navigation zu ändern.
3. Gemeinsame Content-Includes zunächst an einer nahezu identischen Seite erproben; Klima oder System eignen sich besser als Overview.
4. Mobile-/Tablet-spezifische Pfade und Raster in kleinen Wrappern belassen. Keine dynamisch konstruierten Include-Pfade verwenden.
5. Nach jedem Schritt YAML, Includes, dokumentierte Entities und beide Zielansichten prüfen.

### Phase 3 – Rooms-Seite

1. `room_card_v5` kontrolliert zu einer vollständigen Raumkarte erweitern: Statuskopf, Warnzustand, Lichtzähler, sichere Navigation und standardisiertes Aktionsraster.
2. Wiederverwendbare Action-Templates für Licht, Switch, Cover, Klima und Öffnung definieren; mindestens 44–48 px Touch-Ziel sicherstellen.
3. Eine deklarative Raumkonfiguration je Raum verwenden. Fehlende Werte wie Luftfeuchte oder Fensterstatus werden ausgelassen, nicht simuliert.
4. Zuerst einen Raum als vertikalen Prototyp auf Mobile und Tablet umsetzen und validieren.
5. Danach die übrigen fünf Räume migrieren, ohne ihre Detailseiten oder Funktionen zu entfernen.
6. Wohnzimmer-Cover als gruppierte Bedienung bzw. sicheren Popup-Kandidaten behandeln; Soundbar nur in Detail- oder aktivem Medienkontext zeigen.
7. Navigation, aktive Zustände, offene Fenster/Türen, unbekannte Werte und schmale/breite Breakpoints abschließend testen.

## Phase-1-Änderungen

- `docs/audit.md` neu erstellt.
- Drei falsch geschriebene Öffnungs-Entity-IDs in gemeinsamen Raumdetailseiten korrigiert.
- Den nicht belegbaren Leistungsgraphen aus beiden Klimaansichten entfernt.
- `TASKS.md` und `CHANGELOG.md` aktualisiert.

## Offene Validierung

Vor Beginn von Phase 2 muss auf einem System mit Python und PyYAML ausgeführt werden:

```bash
python validate.py
```

Danach sollte Home Assistant selbst die Packages und Lovelace-Dashboards laden, weil der lokale Validator keine vollständige HA-Schema- oder Laufzeitprüfung ersetzt.

## Umsetzung nach dem Audit

Phase 2 und Phase 3 wurden am 2026-07-16 umgesetzt:

- Das Theme enthält nun semantische `mag-*`-Tokens für Oberflächen, Zustände, Abstände, Radien, Schatten und maximale Inhaltsbreite.
- Room-Header, Aktionen und interne Navigation liegen in gemeinsamen Button-Card-Templates.
- Mobile und Tablet laden dieselbe deklarative Kartenliste aus `shared/cards/rooms.yaml`; nur die responsive View-Hülle bleibt gerätespezifisch.
- Die Rooms-Seite besitzt eine gemeinsame Navbar mit relativen Routen, damit sie in beiden Dashboard-Pfaden funktioniert.
- Unbekannte Temperatur-, Luftfeuchte- und Öffnungszustände werden defensiv dargestellt.
- Rollläden werden aus der Übersicht nicht blind umgeschaltet: einzelne Cover öffnen `more-info`, gruppierte Cover führen zur Raumdetailseite.
