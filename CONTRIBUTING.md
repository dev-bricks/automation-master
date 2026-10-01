# Contributing to automation-master

[English](#english) | [Deutsch](#deutsch)

---

<a id="english"></a>
## English

Thank you for your interest in contributing to **automation-master**!

### Architectural Principles & Quality Invariants

`automation-master` is a local-first automation registry, credit governance engine, and event-sourced ledger. All contributions must respect our foundational invariants:

1. **100% Local-First & Zero-Egress (`INV-LOCAL-01`)**: All computation is executed locally in user space without external network calls, sockets, or telemetry.
2. **RunAsInvoker Non-Elevation (`INV-PRIV-02`)**: All operations run strictly in unprivileged user space. Never require root, sudo, or UAC elevation.
3. **Immutable Event Ledger (`INV-IMMUT-03`)**: Append-only SQLite `events` table with SHA-256 payload hashing. Raw events must never be updated or deleted.
4. **Atomic Reservation Integrity (`INV-ATOMIC-04`)**: SQLite `BEGIN IMMEDIATE` transaction boundaries prevent race conditions, double-allocations, and overdrafts.
5. **Fail-Closed Credit Gating (`INV-GATE-05`)**: Default `SHADOW` or `DISABLED` enforcement mode. Throttling decisions fail closed.
6. **Zero Cost for Inactive Runs (`INV-NOWORK-06`)**: `NO_WORK` preflight checks release holds immediately with 0 credit deduction.
7. **Guaranteed Critical Exemption (`INV-EXEMPT-07`)**: Safety-critical tasks and health probes retain protected baseline allowances.
8. **30-Day Receipt Retention (`INV-RETENT-08`)**: Deterministic 30-day rich diagnostic projections; immutable audit summaries for older events.
9. **Multi-OS Operating Parity (`INV-PARITY-09`)**: Deterministic standard library path normalization and UTF-8 encoding across Windows, POSIX, and macOS.
10. **Cloud Sync Directory Isolation & 48h SLA (`INV-ISOLAT-10`)**: Databases are placed in local appdata outside cloud sync directories (OneDrive, Dropbox); 48h response SLA.

### Development Guidelines

- **Plan D Architecture**: Development, git operations, and tests occur strictly in the local git repository clone (`C:\_Local_DEV\repos\automation-master`).
- **Python Version Support**: Compatible with Python 3.10 through 3.13. Zero external runtime dependencies (`dependencies = []`).
- **Pre-commit Quality Gates**:
  - Bytecode compilation: `python -m compileall -q src tests`
  - Linting: `ruff check src tests`
  - Automated test suite: `pytest -ra -v` (100% green required)
- **Security Vulnerabilities**: Please do not report security vulnerabilities publicly. Follow our [SECURITY.md](SECURITY.md) guidelines for responsible disclosure (48h response SLA).

---

<a id="deutsch"></a>
## Deutsch

Vielen Dank für Ihr Interesse an einer Mitarbeit an **automation-master**!

### Architektur-Prinzipien & Qualitäts-Invarianten

`automation-master` ist ein lokales Automations-Register, ein Credit-Governance-System und ein ereignisgesteuertes Hauptbuch. Alle Beiträge müssen unsere grundlegenden Invarianten einhalten:

1. **100% Local-First & Zero-Egress (`INV-LOCAL-01`)**: Sämtliche Verarbeitung erfolgt lokal im Benutzerkontext ohne externe Netzwerkaufrufe, Sockets oder Telemetrie.
2. **RunAsInvoker Non-Elevation (`INV-PRIV-02`)**: Alle Operationen werden strikt im unprivilegierten Benutzermodus ausgeführt. Keine Root-, Sudo- oder UAC-Elevation erforderlich.
3. **Unveränderliches Ereignis-Hauptbuch (`INV-IMMUT-03`)**: Reines Anhängen (Append-Only) in der SQLite-Tabelle `events` mit SHA-256-Payload-Hashing. Rohereignisse dürfen weder modifiziert noch gelöscht werden.
4. **Atomare Reservierungs-Integrität (`INV-ATOMIC-04`)**: SQLite `BEGIN IMMEDIATE`-Transaktionsgrenzen verhindern Wettlaufsituationen und Doppelbelegungen.
5. **Fail-Closed Credit-Gating (`INV-GATE-05`)**: Standardmäßig im `SHADOW`- oder `DISABLED`-Modus; Drosselungsentscheidungen schließen im Zweifel fehlersicher.
6. **Null Kosten für inaktive Läufe (`INV-NOWORK-06`)**: `NO_WORK`-Vorabprüfungen geben Reservierungen sofort mit 0 Credit-Abzug frei.
7. **Garantierte kritische Ausnahmeregelung (`INV-EXEMPT-07`)**: Sicherheitskritische Aufgaben und Integritätsprüfungen behalten geschützte Basiskontingente.
8. **30 Tage Aufbewahrung (`INV-RETENT-08`)**: Deterministische 30-Tage-Projektionen für Diagnostik; unveränderliche Audit-Zusammenfassungen für ältere Ereignisse.
9. **Multi-Betriebssystem-Parität (`INV-PARITY-09`)**: Deterministische Pfadnormalisierung und UTF-8-Codierung über Windows, Linux und macOS.
10. **Isolation von Cloud-Sync-Ordnern & 48h SLA (`INV-ISOLAT-10`)**: SQLite-Datenbanken liegen außerhalb von Cloud-Sync-Verzeichnissen (OneDrive, Dropbox) in lokalen Zustandsordnern; 48h Reaktions-SLA.

### Richtlinien für Entwickler

- **Plan D Architektur**: Entwicklung und Tests erfolgen ausschließlich im lokalen Git-Repository (`C:\_Local_DEV\repos\automation-master`).
- **Python-Unterstützung**: Python 3.10 bis 3.13. Null externe Laufzeit-Abhängigkeiten (`dependencies = []`).
- **Qualitäts-Tore vor Commits**:
  - Bytecode-Prüfung: `python -m compileall -q src tests`
  - Linter: `ruff check src tests`
  - Testsuite: `pytest -ra -v` (100% grün erforderlich)
- **Sicherheitsmeldungen**: Sicherheitslücken bitte nicht öffentlich melden, sondern gemäß [SECURITY.md](SECURITY.md) vertraulich einreichen (48h Reaktions-SLA).
