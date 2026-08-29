# Vertrag zur Beobachtung der Automation Runtime

## Zweck

`AutomationRuntime` ist der logische Anbieter für `module:automation-runtime`.
Das Modul erfasst begrenzte Nachweise über einen Automatisierungslauf, nachdem
Provider und Scheduler ihre eigenen Daten zurückgelesen haben. Es ist Beobachter
und Belegspeicher, aber weder Definitionsautorität noch Scheduler,
Prozessstarter oder Policy-Engine.

## Erforderliche Nachweise

Jeder Runtime-Beleg enthält:

- eine portable Beleg-ID und die Version der Automatisierungsdefinition;
- eine Ausführungsklasse und bei nicht app-eigenen Läufen einen unveränderlichen
  Ausführungs-Pin;
- Zeitzonen enthaltende Plan-, Start- und Endzeitpunkte;
- native Rücklesedaten von Provider und Scheduler;
- genau einen aufgelösten Autoritätseingang für Regeln, Policies,
  Entscheidungen, Workflows und freigegebene Nutzerpräferenzen;
- ausschließlich SHA-256-Fingerprints der Eingaben;
- eine begrenzte, bereinigte Ergebniszusammenfassung;
- eine Mutationsklasse und optional einen stabilen Rollback-Verweis.

Die Belege verwenden das geschlossene Schema
`ellmos.automation-runtime-receipt.v1`. Unbekannte Felder, fehlende
Autoritätseingänge, Roh-Prompts, persönliche Rohdaten, zugangsdatenähnliche
Werte, veränderliche Ausführungsverweise und Belegspeicher in synchronisierten
Cloud-Verzeichnissen werden abgewiesen.

## Native Rückleseadapter

`read_provider_receipt` liest einen größenbegrenzten UTF-8-JSON-Beleg und gibt
nur die gewählte native Beleg-ID, den Status, den Beobachtungszeitpunkt, die
Quellidentität und einen SHA-256-Hash der exakten Bytes zurück. Quellpfad und
roher Provider-Inhalt werden nicht ausgegeben.

`read_scheduler_run` öffnet eine SQLite-Datenbank des `ellmos-scheduler` mit
einem unveränderlichen Nur-Lese-Zugriff. Die Funktion akzeptiert nur das
erwartete `runs`-Schema, lehnt ein nicht leeres aktives WAL ab und überführt nur
Laufidentität, Planungsmetadaten, Status und Autoritätsfingerprint in einen
Inhaltshash. Ausgabe, Fehlertext, Payload und Dateipfade werden nicht ausgegeben.

Providerspezifische Selektoren können an der CLI-Grenze ausdrücklich angegeben
werden; unbekannte Strukturen werden abgewiesen.

## Speicherung und Statistik

`RuntimeReceiptStore` schreibt für jeden Beleg genau eine neue JSON-Datei
außerhalb konfigurierter OneDrive-Verzeichnisse. Identische Wiederholungen sind
idempotent. Dieselbe Beleg-ID mit abweichendem Inhalt erzeugt einen Konflikt.
Beim Lesen wird der gespeicherte Inhaltshash geprüft.

`AutomationRuntime.statistics()` gibt nur Beleganzahl, Anzahl je Status und den
letzten Endzeitpunkt aus. Automatisierungs-IDs, Eingabedetails und
Ergebniszusammenfassungen werden nicht ausgegeben.

## Zuständigkeitsgrenze

- Automatisierungsdefinition und Freigabestatus verbleiben in der zuständigen
  Registry.
- Fälligkeit, Lease, Dispatch und Wiederholungsentscheidungen verbleiben beim
  Scheduler.
- Regeln, Policies, Entscheidungen, Workflows und Nutzerpräferenzen verbleiben
  bei ihren jeweiligen Autoritäten.
- Die Ausführung verbleibt beim Provider.
- `AutomationRuntime` validiert, speichert und verdichtet ausschließlich
  Nachweise nach dem Lauf.

Dieser Vertrag erlaubt weder Aktivierung noch Provider-Mutation,
Veröffentlichung oder harte Durchsetzung.
