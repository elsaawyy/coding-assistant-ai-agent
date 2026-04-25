# 🤖 Coding Assistant AI Agent

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An intelligent autonomous agent that analyzes GitHub repositories, detects issues, and applies improvements**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Output Report](#-output-report)
- [Project Structure](#-project-structure)
- [Examples](#-examples)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Coding Assistant AI Agent** is an autonomous system that:

- ✅ Clones and analyzes GitHub repositories
- ✅ Detects code issues using AST and static analysis
- ✅ Prioritizes issues using a rule-based decision engine
- ✅ Applies fixes automatically (when possible)
- ✅ Generates detailed analysis reports

> Unlike simple LLM chatbots, this agent demonstrates true autonomous behavior with explicit control flow, decision-making, and iterative processing.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Coding Assistant Agent                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │  Repository  │──▶│     Code     │──▶│  Knowledge   │   │
│  │    Loader    │   │   Analyzer   │   │   Builder    │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
│         │                  │                  │             │
│         └──────────────────▼──────────────────┘             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Issue Detector (Rule Engine)             │  │
│  │    • Code Smells  • Security  • Complexity  • Dupes  │  │
│  └──────────────────────────────┬───────────────────────┘  │
│                                 │                           │
│                                 ▼                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Decision Engine (Core Agent Logic)          │  │
│  │      • Priority Queue  • Strategy  • State Machine   │  │
│  └────────┬─────────────┬────────────┬──────────────────┘  │
│           │             │            │                      │
│           ▼             ▼            ▼            ▼         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Fix    │  │ Validate │  │ Generate │  │ Reporter │  │
│  │Generator │  │ (Tests / │  │  Patch   │  │          │  │
│  │  (LLM)  │  │ Linting) │  │          │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Current Features

| Feature | Status | Description |
|---|---|---|
| Repository Cloning | ✅ | Clone GitHub repositories with GitPython |
| AST Analysis | ✅ | Parse Python code and extract structure |
| Issue Detection | ✅ | Detect code smells, complexity, missing docstrings |
| Priority Scoring | ✅ | Rank issues by severity and context |
| Decision Engine | ✅ | Rule-based autonomous decision making |
| Auto Fixes | ✅ | Apply simple fixes (docstrings, formatting) |
| Validation | ✅ | Syntax validation for applied fixes |
| JSON Reports | ✅ | Generate comprehensive analysis reports |

### Detection Rules

| Rule | Severity | Threshold |
|---|---|---|
| Long Function | `MEDIUM` | > 50 lines |
| High Complexity | `HIGH` | Complexity > 10 |
| Very High Complexity | `CRITICAL` | Complexity > 20 |
| Missing Docstring | `LOW` | No docstring present |
| Too Many Parameters | `MEDIUM` | > 5 parameters |
| Large File | `MEDIUM` | > 500 lines |
| Empty Class | `LOW` | No methods/attributes |
| TODO Comments | `INFO` | Contains TODO/FIXME |

### Planned Features

- [ ] LLM integration for complex refactoring
- [ ] Multi-file context analysis
- [ ] Call graph visualization
- [ ] Automatic PR creation
- [ ] Support for JavaScript/TypeScript
- [ ] Incremental learning from past runs

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/coding-assistant-agent.git
cd coding-assistant-agent

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the agent
python main.py https://github.com/psf/requests
```

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Git
- pip package manager

### Step-by-Step

```bash
# Create project directory
mkdir coding-assistant-agent && cd coding-assistant-agent

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python --version
pip list | grep "gitpython"     # Linux/Mac
pip list | findstr "gitpython"  # Windows
```

---

## 📖 Usage

### Basic

```bash
# Analyze with default settings
python main.py https://github.com/psf/requests

# Analyze a specific branch
python main.py https://github.com/psf/requests --branch main

# Dry run — analyze only, no fixes applied
python main.py https://github.com/psf/requests --dry-run

# Limit the number of fixes
python main.py https://github.com/psf/requests --max-fixes 10
```

### Advanced

```bash
# Analyze multiple file types
python main.py https://github.com/psf/requests --extensions .py .pyx

# Set minimum severity (0=INFO, 1=LOW, 2=MEDIUM, 3=HIGH, 4=CRITICAL)
python main.py https://github.com/psf/requests --min-severity 2

# Custom output location
python main.py https://github.com/psf/requests --output ./reports/analysis.json

# Quiet mode
python main.py https://github.com/psf/requests --quiet

# Combined options
python main.py https://github.com/psf/requests \
    --branch develop \
    --max-fixes 15 \
    --min-severity 2 \
    --output report.json \
    --workspace ./temp
```

---

## ⚙️ Configuration

### Command Line Options

| Option | Short | Default | Description |
|---|---|---|---|
| `repo_url` | — | Required | GitHub repository URL |
| `--branch` | `-b` | `main` | Branch to analyze |
| `--max-fixes` | `-m` | `20` | Maximum fixes to apply |
| `--min-severity` | `-s` | `1` | Minimum severity level (0–4) |
| `--output` | `-o` | `analysis_report.json` | Output report file path |
| `--workspace` | `-w` | `./workspace` | Workspace directory |
| `--extensions` | `-e` | `.py` | File extensions to analyze |
| `--dry-run` | `-d` | `False` | Analyze only, no fixes |
| `--quiet` | `-q` | `False` | Suppress detailed output |

### Severity Levels

| Level | Value | Description |
|---|---|---|
| `INFO` | 0 | Informational only (e.g., TODO comments) |
| `LOW` | 1 | Minor improvements (e.g., missing docstrings) |
| `MEDIUM` | 2 | Moderate issues (e.g., long functions) |
| `HIGH` | 3 | Significant issues (e.g., high complexity) |
| `CRITICAL` | 4 | Severe issues requiring immediate attention |

### Configuration File

Edit `config/agent_config.yaml` to customize detection rules:

```yaml
detection:
  rules:
    long_function:
      enabled: true
      max_lines: 50
      severity: "MEDIUM"

    high_complexity:
      enabled: true
      max_complexity: 10
      severity: "HIGH"

decision:
  min_severity: 1
  max_fixes_per_run: 20
  max_retries: 3
```

---

## 📊 Output Report

The agent generates a structured JSON report:

```json
{
  "summary": {
    "repository": "https://github.com/psf/requests",
    "files_analyzed": 45,
    "total_issues": 127,
    "fixes_applied": 15,
    "fixes_failed": 3,
    "success_rate": 0.833,
    "elapsed_time_seconds": 45.2,
    "severity_breakdown": {
      "CRITICAL": 2,
      "HIGH": 8,
      "MEDIUM": 45,
      "LOW": 72
    }
  },
  "issues": [
    {
      "type": "high_complexity",
      "severity": "HIGH",
      "file": "requests/models.py",
      "line": 156,
      "message": "High cyclomatic complexity",
      "suggestion": "Simplify control flow or split function",
      "context": {
        "function": "prepare_request",
        "complexity": 15
      }
    }
  ],
  "applied_fixes": [],
  "failed_fixes": [],
  "timestamp": "2026-04-25T14:30:00"
}
```

### Sample Console Output

```
🤖 CODING ASSISTANT AI AGENT
============================================================
Repository: https://github.com/psf/requests
Started at: 2026-04-25 14:30:00
============================================================

📦 Phase 1: Loading Repository
----------------------------------------
Cloning https://github.com/psf/requests...
✅ Repository cloned to: ./workspace/requests
📁 Found 45 source files to analyze

📄 [1/45] Analyzing: __init__.py
----------------------------------------
🐛 Found 3 issues:
  🟠 HIGH: 1
  🟡 MEDIUM: 2

  🔧 Attempting to fix: High cyclomatic complexity
     Strategy: simplify_logic
     Confidence: 75%
     ✅ Fix applied successfully

📄 [2/45] Analyzing: api.py
----------------------------------------
🐛 Found 5 issues:
  🔴 CRITICAL: 1
  🟠 HIGH: 1
  🟡 MEDIUM: 2
  🔵 LOW: 1

  🔧 Attempting to fix: Very high cyclomatic complexity
     Strategy: manual_review
     Confidence: 45%
     ⏭️  Skipping — low confidence

============================================================
📊 FINAL REPORT
============================================================

📈 Statistics:
  • Files analyzed:   45
  • Total issues:     127
  • Fixes applied:    15
  • Fixes failed:     3
  • Success rate:     83.3%
  • Time elapsed:     45.2s

🐛 Issues by severity:
  🔴 CRITICAL:  2
  🟠 HIGH:      8
  🟡 MEDIUM:   45
  🔵 LOW:      72

💾 Report saved to: analysis_report.json
✨ Analysis completed successfully!
```

---

## 📁 Project Structure

```
coding-assistant-agent/
│
├── src/                          # Source code
│   ├── agents/                   # Agent core logic
│   │   ├── __init__.py
│   │   ├── core_agent.py         # Main orchestrator
│   │   └── decision_engine.py    # Decision making
│   │
│   ├── analyzers/                # Code analysis
│   │   ├── __init__.py
│   │   └── code_analyzer.py      # AST parsing
│   │
│   ├── detectors/                # Issue detection
│   │   ├── __init__.py
│   │   └── issue_detector.py     # Rule-based detection
│   │
│   ├── loaders/                  # Repository loading
│   │   ├── __init__.py
│   │   └── repo_loader.py        # Git operations
│   │
│   ├── builders/                 # Knowledge building
│   │   └── __init__.py
│   │
│   ├── generators/               # Fix generation
│   │   └── __init__.py
│   │
│   ├── validators/               # Validation
│   │   └── __init__.py
│   │
│   └── reporters/                # Reporting
│       └── __init__.py
│
├── config/
│   └── agent_config.yaml         # Agent settings
│
├── tests/
│   ├── __init__.py
│   └── fixtures/
│
├── workspace/                    # Cloned repositories (auto-created)
├── cache/                        # Analysis cache (auto-created)
├── logs/                         # Log files (auto-created)
│
├── main.py                       # Entry point
├── requirements.txt              # Dependencies
├── README.md                     # This file
└── .gitignore
```

---

## 💡 Examples

**Basic dry-run analysis:**
```bash
python main.py https://github.com/psf/requests --dry-run
```

**Aggressive mode — fix everything LOW and above:**
```bash
python main.py https://github.com/psf/requests --max-fixes 50 --min-severity 1
```

**Critical issues only:**
```bash
python main.py https://github.com/psf/requests --min-severity 4 --dry-run
```

**Timestamped report:**
```bash
python main.py https://github.com/psf/requests --output ./reports/$(date +%Y%m%d)_report.json
```

---

## 🗺️ Roadmap

**Phase 1 — Core Infrastructure** ✅ Complete
- Repository loading and cloning
- AST analysis
- Issue detection framework
- Rule-based decision engine

**Phase 2 — Enhancement** 🔄 In Progress
- LLM integration for complex fixes
- Multi-language support
- Call graph analysis
- Performance optimizations

**Phase 3 — Advanced Features** 📅 Planned
- Automatic PR creation
- Learning from past runs
- Web dashboard
- CI/CD integration
- Custom rule definitions

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linter
pylint src/

# Format code
black src/
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [GitPython](https://gitpython.readthedocs.io/) — Git repository handling
- [Python AST](https://docs.python.org/3/library/ast.html) — Code parsing
- [Radon](https://radon.readthedocs.io/) — Code complexity metrics

---

## 📧 Contact

**Author:** Mohamed Mosbah 
**Email:** mohamedmosbah3017@gmail.com 
**GitHub:** [@elsaawyy](https://github.com/elsaawyy)

---

<div align="center">
  <sub>Built with ❤️ by Mohamed Elsawy ;)</sub>
</div>