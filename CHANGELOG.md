# Changelog

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
