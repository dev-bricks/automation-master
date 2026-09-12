# TODO.md — Active work

**Version:** 0.1.3<br>
**Updated:** 2026-09-12<br>
**Reason:** Pfad B Discoverability, 16-Point Navigation, PEP 621 URLs & Metadata Contract<br>
**Purpose:** Track only work that remains open and provide status visibility.

## STATUS

| Category | Status | Evidence / next gate |
|---|---|---|
| Core Engine & Event Ledger | DONE | Append-only SQLite event ledger, deterministic projections, and atomic reservations verified (all tests green). |
| Credit & Reward Policies | DONE | Weighted reward scoring, budget epoch envelopes, and fail-closed credit gating implemented. |
| Seam Adapters | DONE | Contract adapters for `ellmos-scheduler`, `system-gap-master`, `sqlite-transit-sync`, and Antigravity prompt-repair verified. |
| Release Hygiene & Gate Compliance | DONE | Gate 1-10 compliance achieved, .gitignore hardened, PEP 639 license inventory established. |
| Discoverability & Visual Architecture | DONE | 16-point quick navigation, dual mermaid diagrams, 4 personas, 5-way competitive matrix, 10 canonical invariants, PEP 621 extended URLs. |
| Synthetic Pilot & Calibration | OPEN | 14-tägiger Shadow-Pilot auf Workstation und Laptop sowie Kalibrierung der Credit-Umrechnung. |
| Public Release Gate | USER | MIT License hinterlegt; finale Freigabe für öffentliche Sichtbarkeit obliegt dem Nutzer. |

## Formalized next tasks

- [ ] **TASK-AM-01: 14-Tage Shadow-Pilot & Credit-Kalibrierung** (`effort=medium`, `scope=pilot`, priority `normal`).
  - **Ziel:** Durchführung des 14-tägigen Shadow-Piloten auf Workstation und Laptop; Kalibrierung der Reward-Gewichte und Credit-Konvertierung aus Echtdaten.
  - **Definition of Done:** Belege und Konvergenzberichte validiert; keine unberechtigten Eingriffe in den Scheduler.

- [ ] **TASK-AM-02: Operator-Review & Policy-Override-UI** (`effort=medium`, `scope=ui`, priority `low`).
  - **Ziel:** Bereitstellung einer visuellen Oberfläche für manuelle Operator-Eingriffe und versionskontrollierte Policy-Overrides.
  - **Definition of Done:** CLI/GUI-Schnittstelle zur sicheren Einsicht in Receipts und Budgets.

- [x] **TASK-AM-03: Release-Hygiene & Final-Gate-Härtung (v0.1.2)** (`effort=low`, `scope=hygiene`, priority `high`).
  - **Ergebnis:** Alle 10 Final Gates bestanden (.gitignore, Sprachreinheit, STATUS-Tabelle, PII/Secrets/Pfadneutralität), `THIRD_PARTY_LICENSES.md` angelegt, Plan-D-Spiegelung synchronisiert.

- [x] **TASK-AM-04: Pfad B Discoverability, 16-Point Navigation & Metadata Contracts (v0.1.3)** (`effort=low`, `scope=marketing`, priority `high`).
  - **Ergebnis:** 16-Punkte-Schnellnavigation mit 100% reziproker Ankerparität, 4 Personas, 5-Wege-Wettbewerbsmatrix, 10 kanonische Invarianten-IDs (`INV-LOCAL-01` bis `INV-ISOLAT-10`), PEP 621 URLs in `pyproject.toml`, erweiterte Vertragstests (71/71 Tests bestanden).

---
<!-- REMEMBER: ENDUSERTEXTE BEKOMMEN ECHTE UMLAUTE Ü Ö Ä ß -->
