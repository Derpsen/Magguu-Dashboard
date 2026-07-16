# Vollständiger Startauftrag für Codex

Kopiere ab der nächsten Trennlinie vollständig in Codex.

---

Du bist der verantwortliche Entwickler für das vollständige Repository **Magguu-Dashboard**. Arbeite direkt im geöffneten VS-Code-Projektordner.

## Hauptziel

Entwickle aus dem vorhandenen funktionierenden Dashboard ein hochwertiges, modernes und langfristig wartbares Home-Assistant-Dashboard für Smartphone, Tablet und Desktop.

Die Oberfläche soll sich wie eine eigenständige Premium-Smart-Home-App anfühlen. Sie soll nicht wie eine Sammlung einzelner Lovelace-Standardkarten aussehen.

Die wichtigste visuelle Richtung ist:

- dunkles Midnight-Design
- große zusammenhängende Raumkarten
- ruhige hochwertige Flächen
- weiche Radien und dezente Schatten
- klare Hierarchie
- aktive Geräte mit passender Akzentfarbe und sanftem Glow
- kompakte Informationsdichte ohne Überladung
- Smartphone mit Bottom Navigation
- Tablet und Desktop mit sinnvoller maximaler Inhaltsbreite

Erstelle keine pixelgenaue Kopie eines fremden Dashboards. Übernimm lediglich das UX-Prinzip moderner Room-Dashboards.

## Verbindliche Projektquellen

Lies vor jeder Umsetzung vollständig:

1. `AGENTS.md`
2. `README.md`
3. `docs/entities.md`
4. `docs/design.md`
5. `TASKS.md`
6. `CHANGELOG.md`
7. alle bestehenden Dateien unter `dashboard/`, `packages/` und `themes/`

`docs/entities.md` ist die verbindliche Quelle für vorhandene Entitäts-IDs. Erfinde keine Entitäten. Ring, Nuki, Unraid, Plex und AdGuard dürfen erst umgesetzt werden, sobald deren echte Entitäts-IDs dokumentiert wurden. Lege dafür zunächst saubere Platzhalterkonzepte oder TODOs an, aber keine kaputten Karten.

## Arbeitsmodus

Arbeite in klaren Phasen. Beginne nicht sofort mit einem großflächigen Rewrite.

### Phase 1 – Vollständiger Audit

Analysiere zuerst das gesamte Repository und ändere noch keine Dashboarddateien.

Prüfe insbesondere:

- Ordner- und Include-Struktur
- YAML-Syntax
- nicht vorhandene oder widersprüchliche Entitäten
- Custom-Card-Abhängigkeiten
- Unterschiede und Duplikate zwischen Mobile und Tablet
- Button-Card-Templates
- Theme-Variablen
- feste Pixelgrößen und problematische Breakpoints
- überflüssige oder tote Dateien
- potenzielle Darstellungsfehler
- Temperatur- und Einheitendarstellung
- Navigationspfade
- Performance
- Barrierefreiheit und Touch-Ziele
- Möglichkeiten, gemeinsame Codebasis und Templates zu verbessern

Erstelle anschließend in `docs/audit.md`:

- aktuellen Architekturüberblick
- konkrete Fehler und Risiken
- priorisierte Verbesserungen
- Abhängigkeitsliste
- Migrationsplan in kleinen Schritten

Führe `python validate.py` aus. Behebe in dieser Phase nur eindeutige Syntax-, Include- oder Referenzfehler, die den aktuellen Stand unmittelbar beschädigen. Dokumentiere jede Änderung.

### Phase 2 – Designsystem und Architektur

Erstelle oder verbessere ein zentrales Designsystem:

- Farben
- Abstände
- Radien
- Schriftgrößen
- Schatten
- aktive Zustände
- Warn- und Fehlerzustände
- responsives Raster

Nutze möglichst bestehende Theme-Variablen und wiederverwendbare Button-Card-Templates. Vermeide wiederholtes CSS und lange duplizierte JavaScript-Templates.

Entscheide anhand des bestehenden Codes, wie Mobile und Tablet eine gemeinsame Basis erhalten können, ohne Home-Assistant-Includes unnötig kompliziert zu machen. Ändere die Struktur nur kontrolliert und aktualisiere alle Include-Pfade gemeinsam.

### Phase 3 – Rooms-Seite als Priorität

Setze zuerst die Rooms-Seite vollständig neu und hochwertig um.

Jeder Raum erhält eine große zusammenhängende Karte. Die Raumkarte soll enthalten:

- Raumname
- großes Raumicon oder eine abstrahierte Raumillustration
- Temperatur
- Luftfeuchtigkeit, sofern vorhanden
- Fenster-/Türstatus, sofern vorhanden
- Anzahl aktiver Lichter
- vier bis fünf wichtigste direkte Aktionen
- Navigation zur vorhandenen Raumdetailseite
- klar erkennbare aktive Zustände
- Warnung bei offenem Fenster oder offener Tür

Die Hauptaktion darf nicht versehentlich durch Antippen eines kleinen Zwischenraums ausgelöst werden. Verwende ausreichend große Touch-Ziele.

Raumspezifische Funktionen:

#### Wohnzimmer

- Hauptlicht und weitere Lichtgruppe sinnvoll zusammenfassen
- Fernseher
- Computer
- drei Rollläden als gruppierte Aktion oder Popup
- Fensterstatus
- Soundbar nur dort anzeigen, wo es UX-seitig sinnvoll ist

#### Esszimmer

- Deckenlicht
- Signe Gradient
- Heizung
- Temperatur und Luftfeuchtigkeit

#### Küche

- Licht
- Rollladen
- Fenster-/Türstatus

#### Badezimmer

- Hauptlicht
- Farblicht oben
- Farblicht unten
- Heizung
- Temperatur und Luftfeuchtigkeit

#### Schlafzimmer

- Hauptlicht
- Bettlicht links
- Bettlicht rechts
- zwei Rollläden
- Fenster-/Türstatus
- Temperatur und Luftfeuchtigkeit

#### Kinderzimmer

- Hauptlicht
- Schranklicht
- Rollladen
- Heizung
- Fensterstatus
- Temperatur und Luftfeuchtigkeit

Nutze eine wiederverwendbare Room-Card-Architektur statt sechs weitgehend kopierter Karten. Raumspezifische Entitätslisten dürfen als Variablen übergeben werden.

### Phase 4 – Home-Seite

Überarbeite anschließend die Home-Seite vollständig.

Sie soll enthalten:

- dynamische Begrüßung
- Anwesenheit
- Anzahl eingeschalteter Lichter
- offene Fenster/Türen
- iPhone-Akkustand
- kompakte Wetterdarstellung
- nächste Arbeitsschicht aus `calendar.arbeiten`
- nächste Müllabfuhr aus `calendar.abfuhr`
- nächster privater Termin aus `calendar.privat`
- nächster allgemeiner Termin aus `calendar.termine`
- wenige wirklich wichtige Schnellaktionen
- Medienbereich nur bei aktiver Wiedergabe
- wichtige Warnungen nur, wenn tatsächlich etwas vorliegt

Vermeide doppelte Informationen und riesige Standardkarten. Die Startseite soll innerhalb weniger Sekunden erfassbar sein.

### Phase 5 – Kalender und Klima

Kalender:

- Arbeit, Privat, Termine und Abfuhr zusammenführen
- 7-Tage-Agenda auf Tablet/Desktop
- kompakte Agenda auf Smartphone
- nächste Müllabfuhr optisch passend zur Abfallart hervorheben

Klima:

- Temperaturen und Einheiten korrekt darstellen
- keine Fahrenheit-Werte mit Celsius-Symbol
- Thermostate übersichtlich und konsistent bedienen
- offene Fenster als Hinweis berücksichtigen, ohne nicht vorhandene Automationen vorzutäuschen

### Phase 6 – Medien, Sicherheit und System

Bereite modulare Seiten vor:

- Medien
- Sicherheit
- System

Noch nicht dokumentierte Ring-, Nuki-, Unraid-, Plex- und AdGuard-Entitäten dürfen nicht erfunden werden. Erstelle stattdessen in `docs/missing-entities.md` eine präzise Liste der benötigten Entitätstypen und Beispiele, welche echten IDs der Benutzer später liefern muss.

Für Nuki gilt später:

- Status gut sichtbar
- Verriegeln als direkte sichere Aktion
- Entriegeln oder Tür öffnen nur mit Bestätigung oder Hold-Aktion

Für Ring gilt später:

- Kameravorschau nur mit realer Kameraentität
- Klingel- und Bewegungsereignisse als Zustände
- keine vorgetäuschte Liveansicht

### Phase 7 – Qualität und Veröffentlichung

Nach jeder Phase:

1. `python validate.py` ausführen.
2. Include-Pfade prüfen.
3. verwendete Entitäten gegen `docs/entities.md` prüfen.
4. Tablet- und Mobile-Dateien auf Abweichungen prüfen.
5. `CHANGELOG.md` aktualisieren.
6. `TASKS.md` aktualisieren.
7. geänderte Dateien zusammenfassen.
8. einen passenden Git-Commit-Titel nennen.

Am Ende:

- `README.md` aktualisieren
- Installation über `install.sh` prüfen
- Update über `update.sh` prüfen
- keine temporären Dateien hinterlassen
- keine Zugangsdaten committen

## Technische Leitlinien

- Bestehende funktionierende HACS-Karten bevorzugen.
- Keine neue Abhängigkeit ohne klaren Mehrwert.
- Home-Assistant-YAML-Tags erhalten.
- JavaScript in Button Card nur dort einsetzen, wo YAML allein nicht sinnvoll reicht.
- Defensive Templates verwenden: unbekannte oder nicht verfügbare Zustände dürfen das Layout nicht zerstören.
- `unknown`, `unavailable`, fehlende Attribute und leere Kalender müssen sauber dargestellt werden.
- CSS möglichst zentralisieren.
- Keine Datei unnötig auf mehrere hundert Zeilen anwachsen lassen.
- Keine Funktion entfernen, nur weil sie noch nicht neu gestaltet wurde.

## Erwartetes Verhalten jetzt

Beginne ausschließlich mit **Phase 1**.

Lies das vollständige Projekt, führe den Audit aus, erstelle `docs/audit.md`, führe die Validierung aus und liefere danach:

1. eine präzise Zusammenfassung des aktuellen Zustands,
2. die wichtigsten gefundenen Fehler,
3. den konkreten Plan für Phase 2 und Phase 3,
4. eine Liste aller Dateien, die du in Phase 1 geändert hast,
5. einen Commit-Vorschlag.

Beginne noch nicht mit der vollständigen visuellen Neugestaltung, bevor der Audit abgeschlossen ist.
