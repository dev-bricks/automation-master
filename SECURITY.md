# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

---

<a name="english"></a>
## English: Security & Trust Model

### Trust Defaults & Local-First Invariants

- **Private by Default**: `automation-master` is designed for local-first operations and private-by-default workflows.
- **Zero-Egress**: Runtime network access is not required and not initiated.
- **Non-Elevation (User-Mode)**: The module operates exclusively in standard user mode without requiring administrative or root privileges.
- **Fail-Closed Trust Policy**: Deployment activation and module imports are denied unless explicitly permitted by a local trust policy.
- **Manifest & Hash Integrity**: Manifest SHA-256 hashes and semantic versions are strictly validated before import; foreign target nodes and version downgrades are rejected.

### Data Handling & Storage Isolation

- **No Credential Logging**: Event payloads belong to the local application and may contain operational metadata. Never put credentials, API keys, private tokens, contact details, or raw private documents into event payloads.
- **Diagnostic Hash Export**: Diagnostic export helpers expose event metadata and SHA-256 payload hashes only, rejecting raw payloads and common credential patterns.
- **Sync Directory Isolation**: Live SQLite databases must remain outside synchronized folders (such as OneDrive or Dropbox). Replications must use verified closed SQLite snapshots (e.g. via `sqlite-transit-sync`).

### Concurrency, Recovery & Retention

- **Atomic Reservations**: Local reservations use `BEGIN IMMEDIATE` SQLite transactions to prevent race conditions.
- **Eventual Consistency Across Hosts**: Cross-host synchronization operates with independent credit envelopes; ledger history is append-only and never rewritten.
- **Retention Invariant**: Detailed receipt projections are retained for 30 days, after which an audit summary containing immutable event metadata and payload hashes is preserved.

### Supported Versions / Unterstützte Versionen

| Version | Supported / Unterstützt | Status |
| :--- | :---: | :--- |
| `0.1.x` | :white_check_mark: | Active Development & Security Updates |
| `< 0.1.0` | :x: | Experimental Pre-Release |

### Reporting Security Vulnerabilities

If you discover a potential security issue or vulnerability, please report it privately:
- **Email**: `security@ellmos.ai`
- **Alternative**: `support@lukasgeiger.com`
- **Umbrella Security**: `lukas@open-bricks.org`
- **GitHub Security Advisories**: [Open a private advisory](https://github.com/dev-bricks/automation-master/security/advisories)

Please include reproduction steps and environment details. Do not open public GitHub issues containing event payloads, private configurations, or local filesystem paths.

---

<a name="deutsch"></a>
## Deutsch: Sicherheitsrichtlinie & Vertrauensmodell

### Vertrauensleitplanken & Local-First-Invarianten

- **Standardmäßig privat**: `automation-master` ist für den lokalen, privaten Betrieb und abgeschlossene Workflows ausgelegt.
- **Null Netzwerk-Egress**: Zur Laufzeit wird kein Netzwerkzugriff benötigt und keinerlei externe Verbindung aufgebaut.
- **User-Mode (Keine Elevation)**: Das Modul läuft vollständig im Standard-Benutzermodus und benötigt keine administrativen Rechte.
- **Fail-Closed Sicherheitsmodell**: Modul-Aktivierungen und Deployment-Pläne werden standardmäßig blockiert, sofern sie nicht explizit durch eine lokale Trust-Policy freigegeben sind.
- **Manifest- & Hash-Integrität**: Vor einem Import werden SHA-256 Manifest-Hashes und semantische Versionen strikt geprüft; fremde Zielknoten und Versions-Downgrades werden abgewiesen.

### Datenbehandlung & Speicher-Isolation

- **Keine Speicherung von Zugangsdaten**: Event-Payloads dienen ausschließlich lokalen Betriebsmetadaten. Zugangsdaten, API-Tokens, Passwörter oder vertrauliche Rohdaten gehören niemals in Event-Payloads.
- **Diagnostischer Hash-Export**: Diagnose-Exporteure geben nur Metadaten und Payload-Hashes aus; Rohinhalte und typische Geheimnismuster werden gefiltert.
- **Isolation vor Cloud-Synchronisation**: Produktiv-Datenbanken verbleiben außerhalb von Cloud-Sync-Ordnern (z. B. OneDrive/Dropbox). Die Replikation erfolgt über geprüfte geschlossene Snapshots (z. B. via `sqlite-transit-sync`).

### Nebenläufigkeit & Aufbewahrung

- **Atomare Reservierungen**: Lokale Budgetreservierungen nutzen `BEGIN IMMEDIATE` SQLite-Transaktionen gegen Race Conditions.
- **Eventual Consistency**: Die Replikation über Hosts hinweg erfolgt über unabhängige Budgets; das Event-Ledger ist unveränderlich (Append-Only).
- **Aufbewahrungs-Invariante**: Detaillierte Belegprojektionen bleiben 30 Tage erhalten; danach sichert eine kompakte Audit-Zusammenfassung mit Metadaten und Payload-Hashes die dauerhafte Nachvollziehbarkeit.

### Meldung von Sicherheitslücken

Sicherheitsrelevante Schwachstellen bitte vertraulich per E-Mail melden:
- **E-Mail**: `security@ellmos.ai`
- **Alternativ**: `support@lukasgeiger.com`
- **Dachverband**: `lukas@open-bricks.org`
- **GitHub Security Advisories**: [Private Sicherheitsmeldung eröffnen](https://github.com/dev-bricks/automation-master/security/advisories)

