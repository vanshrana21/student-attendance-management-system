"""Student Attendance Management System: beginner-friendly command-line app."""
from datetime import date
import pandas as pd
from excel_handler import ExcelHandler
from student_manager import StudentManager
from attendance_manager import AttendanceManager
from report_manager import ReportManager


def ask(prompt):
    return input(prompt).strip()


def show(frame):
    if frame.empty:
        print("No records found.")
    else:
        print(frame.to_string(index=False))


def main():
    excel = ExcelHandler()
    students = StudentManager(excel)
    attendance = AttendanceManager(excel)
    reports = ReportManager(excel)
    print("Student Attendance Management System")
    print(f"Excel files are stored in: {excel.folder}")
    while True:
        print("\n1 Dashboard  2 Register student  3 List/search students  4 Edit student")
        print("5 Mark attendance  6 View daily attendance  7 Student report  8 Export report  0 Exit")
        choice = ask("Choose: ")
        try:
            if choice == "1":
                day = ask(f"Date [YYYY-MM-DD, Enter for today {date.today()}]: ") or date.today().isoformat()
                data = reports.dashboard(day)
                print(f"\nStudents: {data['total']} | Present: {data['present']} | Absent: {data['absent']} | Overall: {data['overall']}%")
                print("Students below 75% (based on all recorded Present/Absent entries):")
                show(data["low"][["Student ID", "Student Name", "Attendance %"]])
            elif choice == "2":
                fields = [ask(label + ": ") for label in ("Student ID", "Student name", "Department", "Semester", "Section")]
                students.add_student(*fields)
                print("Student registered.")
            elif choice == "3":
                query = ask("Search by ID/name (Enter to list all): ")
                show(students.search(query) if query else students.list_students())
            elif choice == "4":
                sid = ask("Student ID to edit: ")
                fields = [ask(label + ": ") for label in ("New name", "New department", "New semester", "New section")]
                students.edit_student(sid, *fields)
                print("Student details updated.")
            elif choice == "5":
                day = ask("Date (YYYY-MM-DD): ")
                current = students.list_students()
                if current.empty:
                    print("Register students before marking attendance.")
                    continue
                print(current[["Student ID", "Student Name"]].to_string(index=False))
                existing = attendance.daily(day)
                correct = not existing.empty and ask("Records already exist. Correct/replace entered students? (y/N): ").lower() == "y"
                statuses = {}
                for row in current.itertuples(index=False):
                    status = ask(f"{row[0]} {row[1]} [P=Present, A=Absent, L=On Leave, Enter=skip]: ").upper()
                    if status:
                        statuses[row[0]] = {"P": "Present", "A": "Absent", "L": "On Leave"}.get(status, status.title())
                if statuses:
                    attendance.mark_attendance(day, statuses, correct_existing=correct)
                    print(f"Saved {len(statuses)} attendance record(s). Skipped students have no record.")
                else:
                    print("Nothing to save.")
            elif choice == "6":
                show(reports.daily_report(ask("Date (YYYY-MM-DD): ")))
            elif choice == "7":
                sid = ask("Student ID (Enter for all): ")
                start = ask("Start date YYYY-MM-DD (optional): ") or None
                end = ask("End date YYYY-MM-DD (optional): ") or None
                dept = ask("Department (optional): ") or None
                sem = ask("Semester (optional): ") or None
                show(reports.student_summary(sid or None, start, end, dept, sem))
            elif choice == "8":
                day = ask("Daily report date (YYYY-MM-DD), or Enter for student summary: ")
                if day:
                    report = reports.daily_report(day)
                    sheet = "Daily " + day
                else:
                    report = reports.student_summary()
                    sheet = "Student Summary"
                excel.save_report(report, sheet)
                print(f"Report exported to {excel.reports_file} (sheet: {sheet}).")
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Choose one of the displayed menu numbers.")
        except (ValueError, OSError, KeyError) as error:
            print(f"Could not complete that action: {error}")


if __name__ == "__main__":
    main()
