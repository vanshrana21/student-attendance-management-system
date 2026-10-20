"""Local Flask browser interface for the Excel-based attendance project."""
from datetime import date
import json
from flask import Flask, jsonify, render_template, request
from excel_handler import ExcelHandler
from student_manager import StudentManager
from attendance_manager import AttendanceManager
from report_manager import ReportManager

app = Flask(__name__)
excel = ExcelHandler()
students = StudentManager(excel)
attendance = AttendanceManager(excel)
reports = ReportManager(excel)


def records(frame):
    """Convert Pandas values to regular JSON-safe Python values."""
    return json.loads(frame.to_json(orient="records"))


def error_response(error, status=400):
    return jsonify({"error": str(error)}), status


@app.get("/")
def home():
    recorded_dates = excel.load_attendance()["Date"]
    dashboard_date = recorded_dates.max() if not recorded_dates.empty else date.today().isoformat()
    return render_template("index.html", today=date.today().isoformat(), dashboard_date=dashboard_date)


@app.get("/api/dashboard")
def dashboard():
    try:
        data = reports.dashboard(request.args.get("date", date.today().isoformat()))
        return jsonify({
            "total": data["total"], "present": data["present"],
            "absent": data["absent"], "overall": data["overall"],
            "low": records(data["low"][["Student ID", "Student Name", "Department", "Attendance %"]]),
        })
    except (ValueError, OSError) as error:
        return error_response(error)


@app.get("/api/students")
def list_students():
    query = request.args.get("q", "").strip()
    frame = students.search(query) if query else students.list_students()
    return jsonify(records(frame))


@app.post("/api/students")
def add_student():
    data = request.get_json(silent=True) or {}
    try:
        students.add_student(*(data.get(key, "") for key in ("student_id", "name", "department", "semester", "section")))
        return jsonify({"message": "Student registered."}), 201
    except (ValueError, OSError) as error:
        return error_response(error)


@app.put("/api/students/<student_id>")
def edit_student(student_id):
    data = request.get_json(silent=True) or {}
    try:
        students.edit_student(student_id, *(data.get(key, "") for key in ("name", "department", "semester", "section")))
        return jsonify({"message": "Student details updated."})
    except (ValueError, OSError) as error:
        return error_response(error)


@app.get("/api/attendance")
def daily_attendance():
    try:
        day = request.args.get("date", date.today().isoformat())
        return jsonify(records(reports.daily_report(day)))
    except (ValueError, OSError) as error:
        return error_response(error)


@app.post("/api/attendance")
def save_attendance():
    data = request.get_json(silent=True) or {}
    try:
        statuses = data.get("statuses", {})
        if not statuses:
            raise ValueError("Choose a status for at least one student before saving.")
        attendance.mark_attendance(data.get("date", ""), statuses, correct_existing=bool(data.get("correct_existing")))
        return jsonify({"message": f"Saved {len(statuses)} attendance record(s)."})
    except (ValueError, OSError) as error:
        return error_response(error)


@app.get("/api/reports/students")
def student_report():
    try:
        frame = reports.student_summary(
            student_id=request.args.get("student_id") or None,
            start_date=request.args.get("start_date") or None,
            end_date=request.args.get("end_date") or None,
            department=request.args.get("department") or None,
            semester=request.args.get("semester") or None,
        )
        return jsonify(records(frame))
    except (ValueError, OSError) as error:
        return error_response(error)


@app.post("/api/reports/export")
def export_report():
    data = request.get_json(silent=True) or {}
    try:
        day = data.get("date", "")
        if day:
            frame = reports.daily_report(day)
            sheet = "Daily " + day
        else:
            frame = reports.student_summary()
            sheet = "Student Summary"
        excel.save_report(frame, sheet)
        return jsonify({"message": f"Exported {sheet} to Reports.xlsx."})
    except (ValueError, OSError) as error:
        return error_response(error)


if __name__ == "__main__":
    # Local-only server: the app is available on this computer, not the network.
    app.run(host="127.0.0.1", port=5000, debug=False)
