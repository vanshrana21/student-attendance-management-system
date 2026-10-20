"""Pandas-based attendance summaries. On Leave is excluded from the denominator."""
import pandas as pd


class ReportManager:
    def __init__(self, excel):
        self.excel = excel

    def student_summary(self, student_id=None, start_date=None, end_date=None, department=None, semester=None):
        students = self.excel.load_students()
        attendance = self.excel.load_attendance()
        if student_id:
            students = students[students["Student ID"].str.casefold() == str(student_id).strip().casefold()]
        if department:
            students = students[students["Department"].str.casefold() == str(department).strip().casefold()]
        if semester:
            students = students[students["Semester"].str.casefold() == str(semester).strip().casefold()]
        if start_date:
            start_date = pd.Timestamp(start_date).strftime("%Y-%m-%d")
            attendance = attendance[attendance["Date"] >= start_date]
        if end_date:
            end_date = pd.Timestamp(end_date).strftime("%Y-%m-%d")
            attendance = attendance[attendance["Date"] <= end_date]
        attendance = attendance[attendance["Student ID"].isin(students["Student ID"])]
        # A missing row is unknown, not an absence. Leave is listed separately and not counted.
        counted = attendance[attendance["Status"].isin(["Present", "Absent"])]
        grouped = counted.groupby("Student ID")["Status"].value_counts().unstack(fill_value=0)
        leave_counts = attendance[attendance["Status"] == "On Leave"].groupby("Student ID").size()
        result = students.copy()
        result["Present Days"] = result["Student ID"].map(grouped.get("Present", pd.Series(dtype=int))).fillna(0).astype(int)
        result["Absent Days"] = result["Student ID"].map(grouped.get("Absent", pd.Series(dtype=int))).fillna(0).astype(int)
        result["Leave Days"] = result["Student ID"].map(leave_counts).fillna(0).astype(int)
        result["Counted Classes"] = result["Present Days"] + result["Absent Days"]
        result["Attendance %"] = result.apply(lambda row: round(row["Present Days"] / row["Counted Classes"] * 100, 2) if row["Counted Classes"] else 0.0, axis=1)
        result["Below 75%"] = result["Attendance %"] < 75
        return result

    def daily_report(self, date_text):
        date = pd.Timestamp(date_text).strftime("%Y-%m-%d")
        students = self.excel.load_students()
        day = self.excel.load_attendance().query("Date == @date")
        # Left join only recorded rows; unrecorded students stay blank rather than becoming Absent.
        report = students.merge(day, on="Student ID", how="left")
        report.insert(0, "Selected Date", date)
        return report

    def dashboard(self, date_text):
        date = pd.Timestamp(date_text).strftime("%Y-%m-%d")
        students = self.excel.load_students()
        day = self.excel.load_attendance().query("Date == @date")
        present = int((day["Status"] == "Present").sum())
        absent = int((day["Status"] == "Absent").sum())
        counted = present + absent
        overall = round(present / counted * 100, 2) if counted else 0.0
        low = self.student_summary()
        low = low[(low["Counted Classes"] > 0) & low["Below 75%"]]
        return {"total": len(students), "present": present, "absent": absent, "overall": overall, "low": low}
