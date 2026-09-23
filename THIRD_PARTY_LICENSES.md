# Third-Party Licenses & Software Inventory

**Project:** `automation-master`<br>
**License:** [MIT License](LICENSE)<br>
**Notice:** [NOTICE](NOTICE)<br>
**Version:** 0.1.5<br>
**Audit Date:** 2026-09-24 (Pfad A Re-Audit: 2026-09-24; Baseline: 2026-09-20)<br>
**Status:** Invariant Confirmed — Zero External Runtime Dependencies (100% Permissive)

---

## 1. Runtime Architecture & Zero-Dependency Invariant

`automation-master` is engineered as a zero-egress, local-first automation governance and credit budgeting system. To preserve maximum operational reliability, deterministic multi-OS execution, and eliminate supply-chain attack vectors, `automation-master` enforces a strict **Zero-Runtime-Dependency** invariant (`dependencies = []`).

### Runtime Footprint

| Package / Module | Version Spec | License | Scope | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Python Standard Library** | `>=3.10` | [PSF License 2.0](https://docs.python.org/3/license.html) | `runtime` | 100% pure Python standard library (`sqlite3`, `hashlib`, `json`, `pathlib`, `typing`, `dataclasses`, `argparse`, `os`, `sys`) |

All core subsystems—including the append-only SQLite event ledger, explainable reward policy calculator, epoch-scoped budget envelopes, and narrow scheduler/transit seam adapters—run entirely on the Python Standard Library without third-party wheels.

---

## 2. Level 1 Software Bill of Materials (SBOM)

In compliance with local-first governance transparency standards, the complete inventory of all components, direct runtime modules, development dependencies, and system-level dependencies is detailed below:

| Component | Scope | Version | License | Zero-Copyleft Status | Elev. Required | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `automation_master` | Core Runtime | `0.1.5` | MIT | Permissive (Author) | No (`RunAsInvoker`) | Automation governance, credit envelopes, reward policy, event store |
| `python.stdlib.sqlite3` | Core Runtime | Standard | PSF-2.0 | Permissive | No (`RunAsInvoker`) | Local append-only event ledger & atomic `BEGIN IMMEDIATE` transactions |
| `python.stdlib.hashlib` | Core Runtime | Standard | PSF-2.0 | Permissive | No (`RunAsInvoker`) | SHA-256 cryptographic payload hashing for immutable event integrity |
| `pytest` | Test Runner | `>=8.0` | MIT | Permissive | No (`RunAsInvoker`) | Automated contract, invariant, regression, and metadata verification |
| `ruff` | Dev Linter | `>=0.9` | MIT / Apache-2.0 | Permissive | No (`RunAsInvoker`) | Fast Python linter, style enforcer, and AST validation |
| `setuptools` | Build System | `>=68.0` | MIT | Permissive | No (`RunAsInvoker`) | Standard PEP 517/PEP 621 build backend and wheel packaging |
| `Python` | System Runtime| `>=3.10` | PSF-2.0 | Permissive | No (`RunAsInvoker`) | Multi-OS execution environment (Windows, Linux, macOS) |
| `Git` | Version Control| `>=2.40` | GPL-2.0 | Tool Only (Isolated) | No (`RunAsInvoker`) | Plan-D source-of-truth management and release tagging |

---

## 3. Invariant Cross-Reference Matrix

The software architecture and dependency footprint directly uphold the 10 Governance Invariants:

| Invariant ID | Software Invariant & Guarantee | Implementation Evidence | Verification Mechanism |
| :--- | :--- | :--- | :--- |
| **`INV-LOCAL-01`** | 100% Local-First & Zero-Egress | Zero external socket or network modules in `src/automation_master/` | AST import scan & `ellmos-module.v2.json` network boundary (`"none"`) |
| **`INV-PRIV-02`** | Non-Elevation (RunAsInvoker) | User-space execution, no Administrator/root privilege requests | Windows manifest RunAsInvoker & test suite unprivileged runner |
| **`INV-IMMUT-03`** | Immutable Event Ledger | Append-only SQLite `events` table with SHA-256 payload hashes | Integration tests verifying rejection of `UPDATE`/`DELETE` operations |
| **`INV-ATOMIC-04`** | Atomic Reservation Integrity | SQLite `BEGIN IMMEDIATE` transaction boundaries | Concurrency test suite verifying zero overdraft races and double-spending |
| **`INV-GATE-05`** | Fail-Closed Credit Gating | Default `SHADOW` or `DISABLED` enforcement modes | Unit tests verifying unconfigured policies never throttle critical jobs |
| **`INV-NOWORK-06`** | Zero Cost for Inactive Runs | `NO_WORK` preflight checks release holds with 0 credit deduction | Adapter tests verifying 0 balance decrement on empty work queues |
| **`INV-EXEMPT-07`** | Guaranteed Critical Exemption | Safety-critical jobs retain protected baseline credit allowance | Reservation tests asserting uninterrupted health and safety runs |
| **`INV-RETENT-08`** | 30-Day Receipt Retention | Deterministic 30-day rich diagnostic projections; immutable audit summaries | Retention tests asserting data tiering without ledger corruption |
| **`INV-PARITY-09`** | Multi-OS Operating Parity | Pure POSIX/NT standard library path normalization and UTF-8 encoding | GitHub Actions CI matrix running on Ubuntu, Windows, and macOS |
| **`INV-ISOLAT-10`** | Cloud Sync Directory Isolation & 48h SLA | Database placement in `%LOCALAPPDATA%` / `$XDG_STATE_HOME`; 48h SLA | Path validator rejecting cloud sync folders (`OneDrive`, `Dropbox`) |

---

## 4. Zero-Copyleft & Non-Elevation Certification

- **Zero-Copyleft Isolation**: All runtime components are 100% permissive (MIT, PSF License 2.0, Apache-2.0). There are zero GPL, AGPL, or LGPL dependencies linked or required at runtime.
- **RunAsInvoker Certification**: All tools, CLI operations, and library APIs operate with unprivileged standard user permissions. No UAC elevation, `sudo`, or system-level administrative credentials are ever requested or required.

---

## 5. Security Reporting & Contact Contacts

For vulnerability reporting, licensing inquiries, or compliance audits:
- **Security Team**: `security@open-bricks.org`
- **Alternative**: `security@ellmos.ai`
- **Maintainer**: `support@lukasgeiger.com`
- **Lead Maintainer**: `lukas@open-bricks.org`
- **Response SLAs**: Initial response within 48 hours; triage assessment within 5 business days.

---

## 6. Full License Texts

### MIT License (`automation-master`, `pytest`, `setuptools`, `ruff`)

```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Python Software Foundation License Version 2.0 (Python Standard Library)

```text
1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and
the Individual or Organization ("Licensee") accessing and otherwise using this
software ("Python") in source or binary form and its associated documentation.

2. Subject to the terms and conditions of this License Agreement, PSF hereby
grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
analyze, test, perform and/or display publicly, prepare derivative works, distribute,
and otherwise use Python alone or in any derivative version, provided, however, that
PSF's License Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001-2026
Python Software Foundation; All Rights Reserved" are retained in Python alone or
in any derivative version prepared by Licensee.
```

### Apache License 2.0 (`ruff` dual-licensed)

```text
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
