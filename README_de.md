# automation-master

<img src="banner.png" width="100%" alt="automation-master banner">

[![Pytest](https://img.shields.io/badge/pytest-45%20passed-brightgreen.svg)](https://pytest.org)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)
[![Ecosystem: dev-bricks](https://img.shields.io/badge/Ecosystem-dev--bricks-blue.svg)](https://github.com/dev-bricks)
[![Umbrella: open-bricks](https://img.shields.io/badge/Umbrella-open--bricks-purple.svg)](https://github.com/open-bricks)
[![LLM-Ready](https://img.shields.io/badge/LLM--Ready-llms.txt-blue.svg)](llms.txt)

> [!NOTE]
> Schneller Index für LLMs und KI-Agenten: siehe [llms.txt](llms.txt) für Kontext, Grenzen und API-Signaturen.

`automation-master` ist ein standardmäßig privates, lokal betriebenes
Control-Modul für wiederkehrende Automatisierungen. Es erfasst
Automatisierungsfamilien und Varianten, berechnet erklärbare Belohnungswerte,
vergibt epochenspezifische Credit-Rahmen und protokolliert Laufbelege.

Das Modul plant oder startet keine Prozesse und ersetzt weder `task-master`
noch `ticket-master`. Der Scheduler erhält nur eine schmale Vorprüfungs- und
Credit-Gate-Schnittstelle.

## Architektur

```mermaid
graph TD
    subgraph ExternalClients ["Externe Aufrufer & Scheduler"]
        SCHED["ellmos-scheduler / Cron"]
        GAP["system-gap-master"]
        TRANSIT["sqlite-transit-sync"]
    end

    subgraph Adapters ["Schmale Adapter-Schnittstellen"]
        GATE["CreditGateAdapter<br/>(Vorprüfung & Autorisierung)"]
        DEP["DeploymentPlan Validator<br/>(Discovery & Health)"]
        SYNC["ImmutableMergePolicy<br/>(Append-Only Union)"]
        PROMPT["PromptRepairContract<br/>(Antigravity-Invarianten-Schutz)"]
    end

    subgraph CoreEngine ["automation-master Kernmodul"]
        SVC["AutomationMaster Service"]
        POLICY["RewardPolicy<br/>(Deterministisches Scoring)"]
        CREDIT["CreditPolicy<br/>(SHADOW / ENFORCED)"]
        RETENTION["ReceiptRetentionPolicy<br/>(30 Tage Details & Audit-Zusammenfassung)"]
    end

    subgraph Storage ["Local-First Event-Speicher"]
        LEDGER[("SQLite Event-Ledger<br/>events-Tabelle (Append-Only)<br/>BEGIN IMMEDIATE Transaktionen")]
        PROJ["Deterministische Projektionen<br/>(Budgets, Läufe, Belege)"]
    end

    SCHED --> GATE
    GAP --> DEP
    TRANSIT --> SYNC
    PROMPT --> SVC

    GATE --> SVC
    DEP --> SVC
    SYNC --> SVC

    SVC --> POLICY
    SVC --> CREDIT
    SVC --> RETENTION
    SVC --> LEDGER
    LEDGER --> PROJ
```

## Reservierungs- & Credit-Governance-Ablauf

```mermaid
sequenceDiagram
    autonumber
    participant S as Scheduler / Aufrufer
    participant G as CreditGateAdapter
    participant M as AutomationMaster
    participant L as SQLite Event-Ledger

    S->>G: Vorprüfung (work_available?)
    alt Keine Arbeit verfügbar
        G->>M: Erfasse NO_WORK (0 Credits)
        M->>L: Hänge DECISION_RECORDED Event an
        G-->>S: Erlaubt (Lauf überspringen, 0 Kosten)
    else Arbeit vorhanden
        G->>M: Reservierung anfordern (credits=N)
        M->>L: BEGIN IMMEDIATE -> Hänge RESERVATION_REQUESTED an
        L-->>M: Reservierung erteilt (held credits += N)
        M-->>G: Entscheidung (ALLOWED / DENIED)
        alt Entscheidung ist ALLOWED
            G-->>S: Ausführung freigeben
            S->>S: Automatisierungsaufgabe ausführen
            S->>G: Laufbeleg melden (Ergebnis & Metriken)
            G->>M: record_receipt(run_id, outcome, useful)
            M->>L: Hänge RECEIPT_RECORDED Event an (held -> spent)
            M->>M: Berechne RewardPolicy & aktualisiere Projektionen
        else Entscheidung ist DENIED (Budget erschöpft)
            G-->>S: Ausführung ablehnen (im Shadow-Modus nur Protokollierung)
        end
    end
```

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

## Schnellstart

```powershell
python -m pip install -e ".[dev]"
automation-master --db .\pilot.db --node workstation init
automation-master --db .\pilot.db --node workstation register-family research "Research"
automation-master --db .\pilot.db --node workstation allocate 2026-W31 research 8 seed-1
automation-master --db .\pilot.db --node workstation status --epoch 2026-W31 --scope research
```

Die Standarddatenbank liegt außerhalb synchronisierter Ordner unter
`%LOCALAPPDATA%\ellmos\automation-master\automation-master.db`.

## Ökosystem & Verwandte Werkzeuge

`automation-master` ist Teil des **dev-bricks** Ökosystems und der **open-bricks** Open-Source-Initiative:

| Projekt | Beschreibung | Rolle in der Suite |
|---|---|---|
| [`DevCenter`](https://github.com/dev-bricks/DevCenter) | Entwickler-Dashboard, Tool-Health & Systemorchestrierung | Systemmonitoring & Entwickler-Cockpit |
| [`CodeBox`](https://github.com/dev-bricks/CodeBox) | Sandbox-Codeausführung & Skript-Runner | Sichere isolierte Laufzeitumgebung |
| [`MethodenAnalyser`](https://github.com/dev-bricks/MethodenAnalyser) | Testmethodik & Psychometrie-Engine | Psychologische Analyse & Validierung |
| [`companion-for-agy`](https://github.com/ellmos-ai/companion-for-agy) | PTY-basierter Stdout-Capture Wrapper für agy/Gemini CLI | Multi-Agent Subprozess-Orchestrierung |
| [`CareCenter-for-Codex`](https://github.com/dev-bricks/CareCenter-for-Codex) | Klienten-Pflegedokumentation & klinischer Prozessassistent | Spezialisierter Assistenz-Workflow-Agent |

