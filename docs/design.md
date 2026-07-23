# Designbriefing

## Referenzrichtung

Das Dashboard orientiert sich konzeptionell an modernen Smart-Home-Oberflächen mit großen Raumkarten, reduzierter Navigation, klaren Zuständen und einer dunklen hochwertigen Gestaltung. Es soll keine pixelgenaue Kopie eines fremden Dashboards sein.

## Home

- dynamische Begrüßung
- kompakte Statuschips
- Wetter kompakt, aber informativ
- nächste Arbeitsschicht
- nächste Müllabfuhr
- nächste private Termine
- wenige wichtige Schnellaktionen
- bestätigte Modi für Gute Nacht, Haus verlassen und Filmabend
- situative Hinweise nur bei Wettergefahr, niedrigem Akku, Abwesenheit oder Heizverlust
- genau einen wichtigsten Hinweis priorisieren und weitere Zustände über Sicherheit und System erreichbar halten
- Medienkarte nur bei aktiver Wiedergabe
- Sicherheitsstatus von Ring und Nuki, sobald Entitäten vorhanden sind

## Räume

- responsive Kartenübersicht
- pro Raum eine große Karte
- großes Raumicon oder dezente Illustration
- Kennzahlen oben
- vier bis fünf Hauptaktionen direkt erreichbar
- weitere Funktionen über Raumdetailseite oder Popup
- Raumdetailseiten mit einem gemeinsamen Statuskopf statt doppelter Kennzahlen strukturieren

## Kalender

- gemeinsame Agenda aus Arbeit, Privat, Termine und Abfuhr
- Müllabfuhr zusätzlich als hervorgehobene nächste Abholung
- Abfallart aus dem Kalendertext erkennen und mit passender Farbe sowie passendem Icon darstellen
- mobile Ansicht kompakt, Tablet mit 7-Tage-Agenda

## Sicherheit

- vorhandene Anwesenheits-, Öffnungs- und OpenCCU-Daten bereits ohne Zusatzintegration zusammenführen
- Nuki-Status und sichere Bedienung
- Ring-Vorschau bzw. Snapshot nur, wenn technisch verfügbar
- offene Fenster und Türen
- kritische Aktionen wie Entriegeln nicht versehentlich per einfachem Tap ausführen

## Medien

- Soundbar, Fernseher und Computer auf einer gemeinsamen responsiven Seite bündeln
- Steckdosen und geräteübergreifende Szenen nur mit klarer Bestätigung schalten
- Plex und weitere Musikquellen erst mit verifizierten Entitäts-IDs einbinden

## Energie und System

- zum integrierten Energie-Dashboard führen, solange keine verifizierten Messentitäten vorliegen
- Wartung aus Updates, OpenCCU-Meldungen, Erreichbarkeit und Akkustatus priorisieren
- Unraid, Docker und AdGuard als vorbereitete Erweiterungen zeigen, aber keine Zustände simulieren

## Responsive Ziele

- Smartphone: eine Spalte, Bottom Navigation
- Tablet: zwei oder drei Spalten je nach Breite
- Desktop: maximale Inhaltsbreite, keine extrem breiten Karten
