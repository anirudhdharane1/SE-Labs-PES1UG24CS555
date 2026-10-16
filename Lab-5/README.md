# Lab 5: Static Code Analysis - IT Helpdesk Ticket Allocator

**Forked repo URL:** https://github.com/anirudhdharane1/L5_06_it_helpdesk

## Contents

| File | Purpose |
|------|---------|
| `helpdesk_system.py` | Cleaned and fixed script |
| `issues.md` | Issues table (what was found and how it was fixed) |
| `reports/` | Before and after reports from Pylint, Bandit and Flake8 |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.53/10 | 10.00/10 |
| Bandit | 4 issues (1 High, 3 Low) | 0 issues |
| Flake8 | 15 issues | 0 issues |

## Reports

- `reports/pylint_report_before.txt`, `reports/pylint_report_after.txt`
- `reports/bandit_report_before.txt`, `reports/bandit_report_after.txt`
- `reports/flake8_report_before.txt`, `reports/flake8_report_after.txt`

## Running the program

The admin password is no longer hardcoded. Set it as an environment variable before closing tickets.

PowerShell:

```powershell
$env:HELPDESK_ADMIN_PASSWORD = "your-password"
python helpdesk_system.py
```

Linux/Mac:

```bash
export HELPDESK_ADMIN_PASSWORD="your-password"
python3 helpdesk_system.py
```

## Re-running the analysis

```
pip install pylint bandit flake8
pylint helpdesk_system.py
bandit -r helpdesk_system.py
flake8 helpdesk_system.py
```
