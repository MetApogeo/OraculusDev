<p align="center">
  <img src="docs/src/oraculus%20svg.svg" width="180" alt="Oraculus Logo" />
</p>

<h1 align="center">Oraculus</h1>
<p align="center"><strong>Financial Telemetry & Technical Debt Auditor</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License MIT"/>
  <img src="https://img.shields.io/badge/i18n-es%20%7C%20en%20%7C%20fr-orange?style=flat-square" alt="i18n: es | en | fr"/>
  <img src="https://img.shields.io/badge/CLI-Rich%20Terminal-9cf?style=flat-square" alt="Rich CLI"/>
</p>

---

**Oraculus** is an advanced analytical engine and CLI tool designed to bridge the communication gap between technical development and business decision-makers. It translates complex software repository metrics (commits, cyclomatic complexity, change volume) into **clear, tangible, interactive financial indicators**.

---

## Features

| Area | Capability |
|------|-----------|
| **Financial Audit** | Real cost of development effort calculated from commits, team salary, and implementation time |
| **Efficiency Index (IEF)** | Compares consumed cost vs. assigned budget with real-time alerting on deviations |
| **Technical Debt** | Identifies quality-degrading commits and estimates accumulated debt cost |
| **Business Risk** | 4-tier risk assessment (LOW / MODERATE / HIGH / CRITICAL) with delay probability |
| **Code Quality** | 4-tier classification per commit: `OPTIMIZATION`, `CLEAN_FEATURE`, `TECH_DEBT`, `NEUTRAL` |
| **Safe Local Analysis** | Auto-clones repos to `~/.oraculus_cache/` — never touches your working directory |
| **HTML Reports** | Interactive Plotly charts with SVG branding, exportable to PDF |
| **History & Trends** | Full analysis history with trend tracking, stats, and side-by-side comparisons |
| **i18n Support** | Multi-language CLI and reports — `es` (Spanish), `en` (English), `fr` (French) |
| **Merge Filtering** | Automatically filters merge commits for accurate LOC analysis |
| **IQR Anomaly Detection** | Interquartile Range filter spots outlier commits automatically |
| **LOC Capping** | Realistic cap at 8 hours of work per commit to avoid distortion |

---

## CLI Commands

### `oraculus analyze`

Analyze a repository and generate a financial report.

```bash
oraculus analyze [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--repo` | TEXT | `.` | Local repo path or `user/repo` for remote |
| `--limite` | INTEGER | `10` | Number of commits to analyze |
| `--salario` | FLOAT | *(prompted)* | Average monthly salary (USD) |
| `--horas` | INTEGER | `160` | Effective working hours per month |
| `--loc-por-hora` | FLOAT | `60.0` | Average LOC written per hour |
| `--python` | FLAG | — | Force Python code quality analysis (Radon) |
| `--php` | FLAG | — | Force PHP quality analysis *(coming soon)* |
| `--js` | FLAG | — | Force JavaScript quality analysis *(coming soon)* |

If no language flag is given, the CLI will ask interactively — or auto-detect based on the project's file extensions.

**Example:**

```bash
oraculus analyze --repo MetApogeo/OraculusDev --salario 3000 --limite 12
```

**Efficiency Traffic Light:**

- **IEF < 0.8** — `[OK]` Completed faster than expected (Neon Green)
- **0.8 ≤ IEF ≤ 1.2** — `[OK]` Acceptable range (Lavender / Yellow)
- **IEF > 1.2** — `[ALERT]` Budget exceeded (Neon Red)

### `oraculus history`

Track, compare, and clean your analysis reports.

```bash
oraculus history [OPTIONS]
```

| Option | Description |
|--------|-------------|
| *(none)* | List all analyses in a table with trend panel |
| `--open <N>` | Open report N in your default browser |
| `--compare <A> <B>` | Side-by-side comparison of two analyses |
| `--stats` | Consolidated statistics (avg IEF, worst/best, total debt) |
| `--clean` | Interactive menu to delete reports (all / keep last 3 / cancel) |

**History list** automatically shows a **trend panel** when multiple analyses exist for the last repo:

```
+-------- === TENDENCY: MetApogeo/OraculusDev === --------+
|   IEF:   0.14 -> 2.07 -> 0.90 [^ Deteriorating]           |
|   Debt:  $0 -> $0 -> $0 [= Stable]                        |
+----------------------------------------------------------+
```

### `oraculus config lang`

Switch the CLI and report language on the fly.

```bash
oraculus config lang <idioma>
```

| Language | Code |
|----------|------|
| Spanish  | `es` |
| English  | `en` |
| French   | `fr` |

The setting persists in `~/.oraculus/config.json`. On first run, Oraculus auto-detects your system locale.

---

## Code Quality Classification

Each commit is classified using cyclomatic complexity density and conventional commit prefixes:

| Class | Meaning |
|-------|---------|
| `OPTIMIZATION` | Complexity decreased — clean-up or refactor |
| `CLEAN_FEATURE` | Clean feature addition with acceptable complexity |
| `TECH_DEBT` | Complexity grew >50% — debt detected |
| `NEUTRAL` | No significant complexity change |

The system also applies:
- **Business Risk:** 4 levels (LOW / MODERATE / HIGH / CRITICAL) with % delay probability
- **LOC Capping:** Any commit exceeding 8 hours of work is capped to prevent outlier distortion
- **Merge Filtering:** Commits starting with "Merge" are excluded from analysis
- **IQR Filter:** Statistical outlier detection on commit volume

---

## Interactive HTML Reports

After analysis, you'll be prompted to generate an HTML report:

```text
Generate HTML report? [Y/n]: Y
```

Saved to `oraculus_reports/` and auto-opened in your browser. Includes:

- **Plotly Cyberpunk charts** — horizontal bar chart (cost per commit, color-coded by quality) and quality distribution donut
- **SVG brand logo** with neon gradients
- **Business risk & tech debt cards** with PM recommendations
- **PDF export** via `@media print` CSS — works in Chrome, Firefox, Edge

---

## Installation

```bash
git clone https://github.com/MetApogeo/OraculusDev.git
cd OraculusDev
pip install -e .
```

Dependencies (`requests`, `python-dotenv`, `click`, `rich`) are installed automatically. The `oraculus` command is registered globally.

**(Optional)** Create a `.env` file for GitHub API rate limit avoidance:

```env
GITHUB_TOKEN=your_token_here
```

---

## Financial Logic

| Formula | Description |
|---------|-------------|
| $$C_h = \frac{\text{Monthly Salary}}{\text{Effective Hours}}$$ | Cost per hour |
| $$T_{hours} = \frac{LOC_{commit}}{60}$$ | Time per commit |
| $$C_{commit} = C_h \cdot T_{hours}$$ | Cost per commit |
| $$C_{debt} = 3 \cdot \sum C_{commit\_debt}$$ | Technical debt estimate (3x multiplier) |

---

## 📜 The Story Behind the Code

Oraculus was born not in front of a monitor, but in the spaces between classes and free hours while teaching.

### 1. First Seeds (Paper Sketches)

It all started with the need to centralize communication between GitHub branches and Jira tasks. These initial sketches were drawn "between classes," capturing the essence of what is now the analysis ecosystem.

![Initial architecture of the flow between Jira, GitHub, and Story Point calculation](https://github.com/MetApogeo/OraculusDev/blob/f732e9130c537b9e068e3f364435c52b7e059ef1/docs/img/hoja_ruta_boceto1.jpg)
*Figure 1: Initial architecture of the flow between Jira, GitHub, and Story Point calculation.*

![Strict schema definition with Pydantic and mapper logic between PHP and Python](https://github.com/MetApogeo/OraculusDev/blob/f732e9130c537b9e068e3f364435c52b7e059ef1/docs/img/hoja_ruta_boceto2.jpg)
*Figure 2: Strict schema definition with Pydantic and mapper logic between PHP and Python.*

### 2. Mathematical Formalization (The Whiteboard)

During a free hour, ideas became formulas. On **May 7, 2026**, the financial logic that powers the current system was defined, including the **Interquartile Range (IQR)** filter for anomaly detection in commits.

![Definition of the Financial Efficiency Index (IEF) and cost-per-commit formulas](https://github.com/MetApogeo/OraculusDev/blob/f732e9130c537b9e068e3f364435c52b7e059ef1/docs/img/pizarra_calculo1.jpg)
*Figure 3: Definition of the Financial Efficiency Index (IEF) and cost-per-commit formulas.*

### 3. Current Development State

Today, Oraculus has evolved from paper scribbles into a functional CLI tool applying solid software engineering principles:

- **DTO Architecture:** `dataclasses` for clean, typed data transport
- **Single Responsibility (SRP):** Separated into stations — data connectors, metrics logic (Calculator), and presentation (CLI)
- **Safe Local Git Analysis:** Auto-clones to `.oraculus_cache/` for safe comparisons without interfering with your active workspace
- **Smart File Filtering:** Automatically ignores lock files, `vendor/`, `node_modules/`, `dist/`, `build/`, and minified assets
- **Remote Fallback:** Falls back to GitHub API when local cloning fails

---

## Roadmap

- [ ] **GraphQL Migration** — Solve N+1 API calls with a single request
- [x] **Local Git Analysis** — Direct `.git` folder reading for maximum speed
- [ ] **Jira Integration** — Cross-reference costs with Story Points (v0.2)

---

## 💎 Oraculus Editions

Oraculus operates under an **Open Core** model. The analytical core will always be free, with advanced solutions for enterprise teams.

### 🟢 Oraculus Community Edition (CE)

The version hosted in this repository. 100% open source (MIT License), free forever, built for individual developers and local evaluations.

- Local analysis via Git telemetry and Radon
- Base financial engine (IEF calculation, Costs, Technical Debt)
- Manual HTML report generation with native PDF export
- Interactive history in the local terminal

### 🟣 Oraculus Pro / Enterprise (Coming Soon)

Designed exclusively for Tech Leads, Project Managers, and Software Agencies who need financial telemetry at scale and process automation. *Close-source, distributed under a commercial license.*

- **Native Jira Cloud integration** (Story Point-based cost calculation)
- **Full multi-language support** (PHP, JavaScript/TypeScript, etc.)
- **CI/CD automation:** Automated PDF report delivery at Sprint close
- **Multi-repo consolidation:** Simultaneous audit across repositories and microservices

> 📩 **Interested in Oraculus Pro for your company or agency?**
> We are currently developing the Enterprise version. If you want early access or a commercial demo, contact me directly or watch for the official launch.

---

## License

Open source (MIT).

> _"From the whiteboard to deployment: Systemic architecture for logical decisions."_

---

<p align="center">
  <sub>Available in <strong>Español</strong> · <strong>English</strong> · <strong>Français</strong></sub>
  <br>
  <sub>Switch with <code>oraculus config lang es|en|fr</code></sub>
</p>
