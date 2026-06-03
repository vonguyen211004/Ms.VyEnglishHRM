# Project Context for AI Code Agents

## Overview

This repository is a Django HR management system for Ms.Vy English. The app is server-rendered with Django templates and Bootstrap 5.

Main domains:

- `employees`: employees, departments, positions, contracts, work history, salary history.
- `attendance`: work shifts, daily attendance, detailed attendance records, monthly summaries.
- `payroll`: payroll periods, payroll details, allowances, deductions and Excel export.

## Local Commands

Run commands from `LTWNhom06/hr_management` unless noted otherwise.

```bash
python manage.py check
python manage.py test
python manage.py migrate
python manage.py runserver
```

Dependencies are declared in `hr_management/requirements.txt`.

## Routing Conventions

Use English URL paths for public routes:

- `/employees/`
- `/attendance/`
- `/payroll/`
- `/api/employees/search/`

Keep Django URL names stable and use `{% url 'route_name' %}` or `{% url 'namespace:route_name' %}` in templates. Do not hard-code app paths in templates for navigation state; prefer `request.resolver_match.url_name`.

Important attendance names:

- `attendance:work_shift_add`
- `attendance:work_shift_edit`
- `attendance:attendance_detail_add`
- `attendance:attendance_detail_edit`
- `attendance:attendance_summary_add`
- `attendance:attendance_summary_edit_form`

## UI Conventions

- Base layout is `hr_management/templates/base.html`.
- Employee pages include `employees/sidebar.html`.
- Payroll pages should extend `payroll/base_payroll.html` so the payroll sidebar remains visible.
- Attendance pages use `attendance/sidebar.html` through the `module_sidebar` block.
- Required fields must show a red `*`. The base template has global support for this; keep labels associated with fields using `for`/`id` where possible.
- Filter selects should auto-apply on `change` when that is the expected workflow.

## Data and Runtime Files

Treat these as local/runtime artifacts:

- `hr_management/db.sqlite3`
- `hr_management/debug.log`
- `hr_management/venv/`
- `__pycache__/`
- `*.pyc`

Avoid editing or committing them unless explicitly requested.

## Known Environment Note

In this workspace, rendering pages that query SQLite may fail with `sqlite3.OperationalError: disk I/O error`. `python manage.py check` can still pass because it does not query application tables. If this appears, check DB file permissions, disk space, file locks and whether another process is holding `db.sqlite3`.
