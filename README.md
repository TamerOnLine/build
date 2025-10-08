# CodeSentry — Intelligent Python Project Auditor & Cleaner

> Audit your Python repo (FastAPI + Streamlit + ReportLab friendly), merge **static analysis** with **runtime coverage**, classify files, and generate a **clean, deploy‑ready build**.

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-blue" />
  <img alt="OS" src="https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-informational" />
  <img alt="Status" src="https://img.shields.io/badge/Status-Alpha-orange" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-lightgrey" />
</p>

---

## ✨ What it does

CodeSentry crawls your repository from given entry points, builds an **import graph**, optionally ingests a `coverage.xml` report, and then **classifies every file** into:  
- `core` — essential runtime code (e.g., `api/`, `streamlit/`, `api/pdf_utils/*`, `themes/`, `layouts/`)  
- `support` — helpers and developer tools (e.g., `tools/`, `dev_tools/`, `debug_*`, etc.)  
- `non_essential` — docs, samples, outputs  
- `generated` — build artifacts and temporary files

From this, it produces:  
- `project_file_roles.json` — a machine‑readable report  
- Safe delete scripts: `safe_delete.ps1` / `safe_delete.sh` (move to `.trash/`, **never** hard‑delete)  
- Optional **clean build** directory `clean_build/` containing only what's required to run.

> Built and tested on projects that combine **FastAPI**, **Streamlit**, and **ReportLab**, but adaptable to other Python layouts.

---

## 🧩 Why CodeSentry?
- **Coverage‑aware**: combines static imports with real execution traces.
- **Layout/theme awareness**: can scan `layouts/*.json` and `themes/*` to include referenced assets and blocks.
- **Cross‑platform**: works on Windows, Linux, macOS. Generates both `.ps1` and `.sh` helpers.
- **Non‑destructive by default**: everything goes to `.trash/` until you confirm.
- **Clean deploys**: produce a minimal `clean_build/` for packaging or hosting.

---

## 📦 Installation

Clone or copy the tool into your repository (common path: `dev_tools/audit_files_pro.py`). Ensure you have Python 3.9+.

```bash
python -m pip install --upgrade pip
python -m pip install coverage uvicorn streamlit
```

> You do **not** need Docker. CodeSentry is a plain Python CLI.

---

## 🚀 Quickstart

1) **(Optional)** Generate a runtime coverage report while hitting your endpoints/UI:

```bash
coverage run -m uvicorn api.main:app --host 127.0.0.1 --port 8000 & coverage xml
```

```bash
streamlit run streamlit/app.py
```


2) **Audit + produce reports**:
```bash
python dev_tools/audit_files_pro.py --coverage-xml coverage.xml
```

3) **Create a clean build**:
```bash
python dev_tools/audit_files_pro.py --coverage-xml coverage.xml --make-clean-build
```

4) **Move non‑essentials to `.trash/`**:
```bash
./safe_delete.ps1
bash ./safe_delete.sh
```

---

## 🔒 Safety
- No hard deletes.
- Move to `.trash/` only.
- `--protect` can whitelist paths.

---

## 🌍 عربي — ملخص سريع
- **CodeSentry** أداة تفحص مشروعك بايثون وتُنشئ مجلد **clean_build/** جاهز للنشر.
- الأوامر الأساسية:
  - `python dev_tools/audit_files_pro.py --coverage-xml coverage.xml --make-clean-build`
  - `safe_delete.ps1/.sh` لنقل الملفات الزائدة.
