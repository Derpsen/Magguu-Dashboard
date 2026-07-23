# Roadmap

## Phase 1 – Audit und Basis

- [x] gesamte Include-Struktur prüfen
- [x] verwendete Custom Cards inventarisieren
- [x] Rooms-Duplikate zwischen Mobile und Tablet entfernen
- [x] zentralisierte Design-Tokens definieren
- [x] YAML-Prüfung automatisieren (`validate.py` vorhanden; lokale Ausführung benötigt Python)
- [x] Architektur, Risiken und Migrationsplan in `docs/audit.md` dokumentieren

## Phase 2 – Räume

- [x] ein wiederverwendbares Room-Card-Template fertigstellen
- [x] Wohnzimmer
- [x] Esszimmer
- [x] Küche
- [x] Badezimmer
- [x] Schlafzimmer
- [x] Kinderzimmer
- [x] responsive Raster für Mobile, Tablet und Desktop definieren
- [ ] visuelle Prüfung auf realen Zielgeräten durchführen

## Phase 3 – Home

- [x] Begrüßung und Statuschips
- [x] kompakte Wetterkarte
- [x] nächste Schicht
- [x] nächste Müllabfuhr
- [x] kombinierte Termine
- [x] Schnellaktionen
- [x] Abfuhr-Countdown mit Hervorhebung für heute und morgen
- [x] situative Warnungen bei offenem Fenster und aktivem Heizvorgang
- [x] Wetter-, Akku- und Abwesenheitswarnungen
- [x] sichere Modi für Gute Nacht, Haus verlassen und Filmabend
- [x] dezente Warnanimationen mit Reduced-Motion-Unterstützung
- [x] bedingte Medienkarte
- [x] Abfuhrkarte nach Müllart dynamisch gestalten
- [x] Raumdetailseiten mit gemeinsamem Statuskopf verdichten
- [x] wichtigsten aktuellen Hinweis zentral priorisieren
- [x] Sicherheits- und Wartungsstatus auf Home verlinken
- [x] kontextabhängige Modi für Morgen, Kochen, Besuch und Gaming ergänzen

## Phase 4 – Kalender und Klima

- [x] Kalenderseite vereinheitlichen
- [x] Temperaturdarstellung und Einheiten prüfen
- [x] Heizungssteuerung vereinfachen
- [x] gemeinsame responsive Seitenmodule für Mobile und Tablet erstellen

## Phase 5 – Sicherheit

- [ ] Ring-Entitäten exportieren und dokumentieren
- [ ] Nuki-Entitäten exportieren und dokumentieren
- [x] Sicherheitsseite mit vorhandenen Öffnungs-, Anwesenheits- und OpenCCU-Daten erstellen
- [x] Ring- und Nuki-Bereiche ohne erfundene Entitäten vorbereiten
- [ ] sichere Bestätigung für Entriegeln

## Phase 6 – Medien und System

- [x] Soundbar und TV
- [x] gemeinsame Medienseite für Mobile und Tablet
- [ ] Plex/Musik
- [ ] Unraid/Docker
- [ ] AdGuard
- [x] Backups und Updates
- [x] Dashboard-Version, Update-Status und letzte erfolgreiche Aktualisierung anzeigen
- [x] priorisierte Wartungszentrale ergänzen
- [x] Energie-Einstieg und Messquellen-Checkliste vorbereiten
- [x] System-Hub für Sicherheit, Medien, Energie und Infrastruktur ergänzen

## Phase 7 – Veröffentlichung

- [ ] Installationsskript testen
- [ ] Updateablauf testen
- [ ] Screenshots ergänzen
- [ ] GitHub Release erstellen
- [ ] HACS-Strategie prüfen
