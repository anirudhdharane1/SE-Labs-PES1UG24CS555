# Issues Table - helpdesk_system.py

Line numbers refer to the **original** script. Ordered by severity.

| # | Issue | Tool / Code | Type | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|---------|-------------|--------------|
| 1 | `shell=True` with string concatenation | Bandit B602 (High) | Security | 38 | Hostname is joined into a shell command, so input like `x; del file` allows command injection | Use `subprocess.run([ping, flag, "1", hostname])` with no shell; validate hostname with a regex; resolve `ping` with `shutil.which` |
| 2 | Hardcoded admin password | Bandit B105 | Security | 8 | Password `helpdesk@123` stored in source and visible in the repo | Read from `HELPDESK_ADMIN_PASSWORD` environment variable; compare with `hmac.compare_digest` |
| 3 | Urgency not validated | Manual (not flagged by tools) | Bug | 13, 52 | A value like `-7` was accepted as a priority, and non-numeric input crashed with `ValueError` | Added `parse_urgency()` that enforces 1-5; callers catch `ValueError` and report the rejection |
| 4 | Bare `except: pass` | Bandit B110, Flake8 E722, Pylint W0702 | Bug / Security | 23 | Hides every error, so a note on a missing ticket silently disappears | Catch `KeyError`, print a message, return `False` |
| 5 | Mutable default argument | Pylint W0102 | Bug | 10 | `audit_trail=[]` is created once and shared across all calls | Default to `None` and create the list inside the function |
| 6 | `close_ticket` on missing id | Manual | Bug | 28 | `del tickets[id]` raises `KeyError` for an unknown ticket | Check the id exists first and return `False` |
| 7 | Global counter | Pylint W0603, C0103 | Design | 7, 11 | Mutable global state modified with `global` | Replaced with `itertools.count(101)` named `TICKET_IDS` |
| 8 | `main()` runs on import | Flake8 E305 | Design | 58 | Importing the module executes the program | Wrapped in `if __name__ == "__main__":` |
| 9 | `== None` comparison | Flake8 E711, Pylint C0121 | Style | 33 | Singleton should be compared by identity | Changed to `is None` |
| 10 | File opened without `with` or encoding | Pylint R1732, W1514 | Resource | 41 | File may stay open on error; encoding depends on platform | `with open(file, "w", encoding="utf-8")` and `json.dump` |
| 11 | `subprocess` import warning | Bandit B404 | Security (Low) | 2 | Informational warning about importing `subprocess` | Acknowledged with `# nosec B404`, since the module is now used without a shell and with validated input |
| 12 | Naming | Pylint C0103 | Style | 30 | `unresolvedHighPriority` is not snake_case | Renamed to `unresolved_high_priority` |
| 13 | Unused variables | Pylint W0612, Flake8 F841 | Cleanup | 47 | `t2` assigned but never used | `t2` is now used when closing a ticket; `t3` removed |
| 14 | `%` string formatting | Pylint C0209 | Style | 14 | Old-style formatting | Replaced with f-strings |
| 15 | Iterating dict keys | Pylint C0206 | Style | 32 | Looks up `tickets[t]` repeatedly | `for ticket_id, ticket in tickets.items():` |
| 16 | Missing docstrings | Pylint C0114, C0116 | Documentation | 1, all functions | No module or function docs | Added docstrings throughout |
| 17 | Blank lines and line length | Flake8 E302, E305, E501; Pylint C0301 | Style | many | PEP 8 formatting violations | Two blank lines between functions; lines wrapped to 79 characters |

## Summary

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.53/10 | 10.00/10 |
| Bandit | 1 High, 3 Low | 0 issues |
| Flake8 | 15 issues | 0 issues |
