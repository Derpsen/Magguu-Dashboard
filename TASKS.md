# Roadmap

Arbeitsregeln und Buddy-Hub-Publish: siehe `AGENTS.md`.

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
- [x] Home-Overview-Raumkarten auf gemeinsame Includes umgestellt (Wohnzimmer/Esszimmer/Küche)
- [x] Mobile-Home an Tablet-Schnellzugriff und Küchenkarte angeglichen
- [x] Flur- und Sonstiges-Lichter auf der Räume-Seite verdrahtet

## Phase 4 – Kalender und Klima

- [x] Kalenderseite vereinheitlichen
- [x] Temperaturdarstellung und Einheiten prüfen
- [x] Heizungssteuerung vereinfachen
- [x] gemeinsame responsive Seitenmodule für Mobile und Tablet erstellen

## Phase 5 – Sicherheit

- [x] Ring-Entitäten exportieren und dokumentieren (Vordereingang-Klingel + Kinderzimmer-Kamera)
- [ ] Nuki-Entitäten exportieren und dokumentieren
- [x] Sicherheitsseite mit vorhandenen Öffnungs-, Anwesenheits- und OpenCCU-Daten erstellen
- [x] Ring-Klingel und Kinderzimmer-Kamera verdrahtet; Nuki ohne erfundene IDs vorbereitet und ausgeblendet
- [x] sichere Bestätigung für Entriegeln vorbereitet (Confirm-Muster; UI ausgeblendet bis echte lock-ID)
- [x] Unverdrahtete Nuki-/Unraid-/Plex-/AdGuard-Platzhalterkarten ausgeblendet

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
- [x] Medien- und Energie-Views in der gemeinsamen Navbar verlinkt

## Phase 7 – Veröffentlichung

- [ ] Installationsskript testen
- [ ] Updateablauf testen
- [ ] Screenshots ergänzen
- [ ] GitHub Release erstellen
- [x] HACS-Strategie: YAML+Packages ist kein HACS-Dashboard (in README dokumentiert)
- [x] POSIX-`install.sh` für HA-OS-ash (kein `BASH_SOURCE`)
- [x] `VERSION` als einzige Versionsquelle, Package-Sensor bleibt synchron
- [x] `docs/audit.md` als historischer Snapshot gekennzeichnet
- [x] `configuration.yaml`: packages/themes/lovelace per Merge ergänzen (Backup, keine vorhandenen Keys überschreiben)

## Phase 8 – Sections-Migration (6.6.0-dev / 6.7.0-dev)

- [x] `validate.py`: strukturelle Dashboard-/Theme-Prüfung offline
- [x] Theme auf `modes.dark`
- [x] `mushroom-title-card` → Heading-Karten
- [x] sechs Raumdetailseiten auf native Sections
- [ ] visuelle Prüfung von Theme, Heading-Karten und Raum-Sections im echten HA (Mobile + Tablet)
- [x] Home, Räume, Klima, System, Kalender, Sicherheit, Medien, Energie, Dienste auf Sections migriert (6.7.0-dev; Navbar-card-Platzierung und Stack-in-Card-Verhalten in Sections noch im echten HA prüfen)
- [x] `modes.light` im Theme + WCAG-Test
- [ ] Sichtprüfung 6.7.0-dev im echten HA (Mobile, Tablet, Hell/Dunkel): Hero-Breite, Navbar, Lücken in den Sections, `.card-header`-Schrift, Light-Mode, Conditions/Visibility
- [x] Raumakzente im Light-Mode per Theme-Mix tokenisiert, WCAG-Test (6.8.0-dev)
- [ ] Sichtprüfung 6.8.0-dev im echten HA: Sicherheits-Kachelreihen (auto-fit), Navbar unten zentriert + Raumseiten, vollbreite letzte Raumkachel, Szenen rechts im Tablet, Hell-Modus-Akzente, Handy-Kürzungen
- [ ] Sichtprüfung 6.9.0-dev im echten HA: Sicherheits-Reihen (Handy 2+1), Szenen rechts im Tablet, Navbar-Abstand, Wetter-Kachel hell, Kamera-Platzhalter; Konsolenfehler `_layoutElement.setConfig` beobachten (Befund in MEMORY.md)
- [x] Runde 4 (6.9.0-dev): Flex-Umbruch, Szenen-Stack, Navbar-Padding, Wetter-Token, Kamera-Platzhalter
- [x] Dienste als optionale Unterseite markiert; Nicht-erreichbar-Ausnahmen; Backup „Noch kein Backup“; doppelte YAML-Keys geprüft (6.8.0-dev)
- [ ] View-Badges für Status-Chips prüfen
- [ ] `condition: user` für „Dashboard aktualisieren“, sobald Marcos User-ID vorliegt (optional)
