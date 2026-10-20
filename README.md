# Student Attendance Management System

A beginner-friendly Python project that uses Pandas to manage students and attendance in Excel workbooks. The first version uses a menu in the terminal so you can follow each operation clearly; Tkinter can be added later without changing the managers.

## Architecture

- `main.py` — menu and user input/output.
- `student_manager.py` — register, list, search, and edit students.
- `attendance_manager.py` — validate dates/statuses and save or correct attendance.
- `report_manager.py` — daily report, filters, dashboard, and percentage calculations.
- `excel_handler.py` — creates and reads/writes the Excel files using Pandas and OpenPyXL.
- `Students.xlsx`, `Attendance.xlsx`, `Reports.xlsx` — data files in the project folder. The first two workbooks are created automatically with headers if missing.

## Install and run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Use Python 3.10 or newer. Close a workbook in Excel before updating it from the program.

## Excel formats

`Students.xlsx` columns: `Student ID`, `Student Name`, `Department`, `Semester`, `Section`.

`Attendance.xlsx` columns: `Date` (YYYY-MM-DD), `Student ID`, `Status` (`Present`, `Absent`, or `On Leave`). Each student can have at most one row per date. Missing rows mean “not recorded,” not “Absent.”

Sample student rows: `CS101 | Aanya Mehta | Computer Science | 3 | A`; `CS102 | Rohan Das | Computer Science | 3 | A`. Sample attendance: `2026-01-05 | CS101 | Present`; `2026-01-05 | CS102 | Absent`; `2026-01-06 | CS101 | On Leave`.

Attendance percentage is `Present / (Present + Absent) × 100`. Approved leave is shown separately and excluded from the denominator. Only dates with a recorded Present or Absent status count. Consequently, the report does not invent absences for missing records.

## Key functions

- `StudentManager.add_student` validates required fields and rejects duplicate IDs.
- `StudentManager.search` uses Pandas text filters to find ID/name matches.
- `AttendanceManager.mark_attendance` validates the entire submission before saving; corrections require `correct_existing=True`.
- `ReportManager.student_summary` combines student data with grouped attendance counts, applies date/department/semester filters, and computes percentages.
- `ReportManager.daily_report` joins that date’s recorded attendance onto the student list; missing statuses remain blank.
- `ExcelHandler.save_report` exports/replaces the named report sheet while retaining other report sheets.

## Manual checks

1. Register a student with every field filled; confirm it appears in option 3.
2. Try registering that same Student ID again; it should show a duplicate error.
3. Mark a date using P, A, L, and Enter (skip). Check `Attendance.xlsx`: P/A/L become records and the skipped student has no row.
4. Mark the same date and student again without accepting correction; it should reject the duplicate. Accept correction and enter a new status to update it.
5. Generate a student report. Confirm leave is excluded and a student with no records has 0 counted classes and 0%.
6. Export a daily report and student summary; check the sheets in `Reports.xlsx`.

## Common errors

- `No module named pandas/openpyxl`: activate the environment and run `python -m pip install -r requirements.txt`.
- Excel file is missing required columns: use the exact headings documented above.
- Workbook cannot be updated: close it in Excel and try again.
- Invalid date: use `YYYY-MM-DD`, such as `2026-01-05`.
- Duplicate student ID or date/ID attendance: search the existing row or use the correction prompt.

## Later improvements

A Tkinter interface, teacher login, attendance calendar, semester-specific class schedules, charts, and a configurable leave policy can be added after the core data rules are understood.

## Example report output

With the included sample data, the dashboard for `2026-01-05` shows 10 registered students, 7 present, 2 absent, and 77.78% overall (the one On Leave student is excluded). The student summary shows `IT202` at 66.67% and `IT203` at 33.33%; both are below 75%. These examples are based on the included fictional records.
