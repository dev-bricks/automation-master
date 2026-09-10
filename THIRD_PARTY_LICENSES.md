# Third-Party Licenses & Software Inventory

**Project:** `automation-master`  
**License:** [MIT License](LICENSE)  
**Audit Date:** 2026-09-10  
**Status:** Invariant Confirmed — Zero External Runtime Dependencies  

---

## Runtime Architecture & Dependencies

`automation-master` is engineered as a zero-egress, local-first automation governance and credit budgeting system. To preserve maximum operational reliability, deterministic multi-OS execution, and eliminate supply-chain attack vectors, `automation-master` enforces a strict **Zero-Runtime-Dependency** invariant.

### Runtime Dependencies

| Package | Version Spec | License | Scope | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| *(None)* | `N/A` | `N/A` | `runtime` | 100% pure Python standard library (`sqlite3`, `hashlib`, `json`, `pathlib`, `typing`, `dataclasses`, `argparse`, `os`, `sys`) |

All core subsystems—including the append-only SQLite event store, the explainable reward policy calculator, epoch-scoped budget envelopes, and narrow scheduler/transit seam adapters—run entirely on the Python Standard Library without third-party wheels.

---

## Development & Test Dependencies

The following tools and libraries are utilized exclusively during development, code style verification, packaging, and automated contract testing:

| Package / Tool | Version Spec | License | Scope | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| [pytest](https://pytest.org/) | `>=8.0` | MIT | `[dev]` | Automated unit, contract, regression, and metadata test execution |
| [ruff](https://github.com/astral-sh/ruff) | `>=0.9` | MIT OR Apache-2.0 | `[dev]` | High-performance Python linter, style enforcer, and AST validation |
| [setuptools](https://github.com/pypa/setuptools) | `>=68.0` | MIT | `[build-system]` | Standard PEP 517/PEP 621 build backend and sdist/wheel packager |

---

## External Tools & Binaries (System Level)

| Binary / Tool | Recommended Version | License | Scope | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| [Python](https://www.python.org/) | `>=3.10` | PSF License | System Runtime | Multi-OS execution environment (`Windows`, `Linux`, `macOS`) |
| [Git](https://git-scm.com/) | `>=2.40` | GPL-2.0 | Version Control | Plan-D source-of-truth management and release tagging |

---

## License Texts & Attribution

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
