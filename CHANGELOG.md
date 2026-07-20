# Changelog

## 6.0.0-dev – 2026-07-16

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
