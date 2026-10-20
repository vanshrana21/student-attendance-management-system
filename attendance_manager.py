"""Attendance entry and correction."""
import pandas as pd

VALID_STATUSES = {"Present", "Absent", "On Leave"}


class AttendanceManager:
    def __init__(self, excel):
        self.excel = excel

    @staticmethod
    def validate_date(date_text):
        try:
            return pd.Timestamp(date_text).strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            raise ValueError("Enter a valid date in YYYY-MM-DD format.")

    def mark_attendance(self, date_text, statuses, correct_existing=False):
        date = self.validate_date(date_text)
        students = self.excel.load_students()
        known_ids = set(students["Student ID"])
        attendance = self.excel.load_attendance()
        for student_id, status in statuses.items():
            student_id, status = str(student_id).strip(), str(status).strip().title()
            if student_id not in known_ids:
                raise ValueError(f"Unknown Student ID: {student_id}")
            if status not in VALID_STATUSES:
                raise ValueError(f"Invalid status '{status}'. Use Present, Absent, or On Leave.")
            exists = ((attendance["Date"] == date) & (attendance["Student ID"] == student_id)).any()
            if exists and not correct_existing:
                raise ValueError(f"Attendance already exists for {student_id} on {date}. Use correction mode to change it.")
        # Validate the whole batch first, then change it, so a typo cannot partly save a class.
        for student_id, status in statuses.items():
            student_id, status = str(student_id).strip(), str(status).strip().title()
            mask = (attendance["Date"] == date) & (attendance["Student ID"] == student_id)
            if mask.any():
                attendance.loc[mask, "Status"] = status
            else:
                attendance.loc[len(attendance)] = [date, student_id, status]
        attendance = attendance.drop_duplicates(["Date", "Student ID"], keep="last")
        self.excel.save_attendance(attendance)

    def daily(self, date_text):
        date = self.validate_date(date_text)
        return self.excel.load_attendance().query("Date == @date").sort_values("Student ID")
