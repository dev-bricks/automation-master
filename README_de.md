# automation-master

<img src="banner.png" width="100%" alt="automation-master banner">

[![Pytest](https://img.shields.io/badge/pytest-33%20passed-brightgreen.svg)](https://pytest.org)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)
[![Ecosystem: dev-bricks](https://img.shields.io/badge/Ecosystem-dev--bricks-blue.svg)](https://github.com/dev-bricks)
[![Umbrella: open-bricks](https://img.shields.io/badge/Umbrella-open--bricks-purple.svg)](https://github.com/open-bricks)

> [!NOTE]
> Schneller Index für LLMs und KI-Agenten: siehe [llms.txt](llms.txt) für Kontext und Grenzen.

`automation-master` ist ein standardmäßig privates, lokal betriebenes
Control-Modul für wiederkehrende Automatisierungen. Es erfasst
Automatisierungsfamilien und Varianten, berechnet erklärbare Belohnungswerte,
vergibt epochenspezifische Credit-Rahmen und protokolliert Laufbelege.

Das Modul plant oder startet keine Prozesse und ersetzt weder `task-master`
noch `ticket-master`. Der Scheduler erhält nur eine schmale Vorprüfungs- und
Credit-Gate-Schnittstelle.

## Schutzregeln

- Der Startmodus ist `disabled` oder `shadow`; harte Gates sind Opt-in.
- `NO_WORK` kostet keinen Credit. Wird erst nach der Reservierung `NO_WORK`
  festgestellt, wird die Reservierung vollständig freigegeben.
- Normale vergleichbare Läufe können bei fehlendem Guthaben abgelehnt werden.
- Einzigartige, sicherheitskritische oder fristgebundene Läufe behalten eine
  Mindestabdeckung.
- Zustandsänderungen sind unveränderliche Events. Es gibt keine veränderbare
  Saldo-Tabelle und kein Last-write-wins.
- `BEGIN IMMEDIATE` schützt Reservierungen innerhalb eines Hosts. Zwischen
  Hosts gilt Eventual Consistency; globale harte Atomarität wird nicht
  versprochen.
- System-Gap-Importe prüfen Quelle, Ziel, Manifest-Hash, Version und
  Aktivierungsmodus. Fremde Slots werden abgelehnt.
- Detaillierte Laufbelege bleiben 30 Tage in der Projektion; danach bleiben
  Event-Metadaten und der unveränderliche Payload-Hash als Audit-Zusammenfassung
  erhalten. Das Event-Ledger wird durch Retention nicht umgeschrieben.

Die Standarddatenbank liegt außerhalb synchronisierter Ordner unter
`%LOCALAPPDATA%\ellmos\automation-master\automation-master.db`.
