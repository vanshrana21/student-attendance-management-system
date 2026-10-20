"""Small helpers for creating and safely reading/writing the Excel workbooks."""
from pathlib import Path
import pandas as pd

STUDENT_COLUMNS = ["Student ID", "Student Name", "Department", "Semester", "Section"]
ATTENDANCE_COLUMNS = ["Date", "Student ID", "Status"]


class ExcelHandler:
    def __init__(self, folder=None):
        self.folder = Path(folder) if folder else Path(__file__).resolve().parent
        self.students_file = self.folder / "Students.xlsx"
        self.attendance_file = self.folder / "Attendance.xlsx"
        self.reports_file = self.folder / "Reports.xlsx"
        self.folder.mkdir(parents=True, exist_ok=True)
        self._create_empty_files()

    def _create_empty_files(self):
        """Create workbooks with headings if they are not already present."""
        for path, columns in ((self.students_file, STUDENT_COLUMNS),
                              (self.attendance_file, ATTENDANCE_COLUMNS)):
            if not path.exists():
                pd.DataFrame(columns=columns).to_excel(path, index=False)

    def _read(self, path, columns):
        try:
            frame = pd.read_excel(path, engine="openpyxl", dtype={"Student ID": str})
        except (OSError, ValueError, ImportError) as error:
            raise ValueError(f"Could not read {path.name}. Check that it is a valid .xlsx file. ({error})") from error
        missing = [column for column in columns if column not in frame.columns]
        if missing:
            raise ValueError(f"{path.name} is missing these columns: {', '.join(missing)}")
        return frame[columns].copy()

    def load_students(self):
        frame = self._read(self.students_file, STUDENT_COLUMNS)
        for col in ("Student ID", "Student Name", "Department", "Section"):
            frame[col] = frame[col].fillna("").astype(str).str.strip()
        frame["Semester"] = frame["Semester"].fillna("").astype(str).str.strip()
        return frame

    def load_attendance(self):
        frame = self._read(self.attendance_file, ATTENDANCE_COLUMNS)
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
        frame["Student ID"] = frame["Student ID"].fillna("").astype(str).str.strip()
        frame["Status"] = frame["Status"].fillna("").astype(str).str.strip().str.title()
        return frame.dropna(subset=["Date"])

    def save_students(self, frame):
        frame[STUDENT_COLUMNS].to_excel(self.students_file, index=False, engine="openpyxl")

    def save_attendance(self, frame):
        frame[ATTENDANCE_COLUMNS].to_excel(self.attendance_file, index=False, engine="openpyxl")

    def save_report(self, report, sheet_name="Attendance Report"):
        """Write a report sheet; other report sheets in Reports.xlsx are retained."""
        if self.reports_file.exists():
            try:
                with pd.ExcelWriter(self.reports_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                    report.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            except (OSError, ValueError) as error:
                raise ValueError(f"Could not update Reports.xlsx: {error}") from error
        else:
            with pd.ExcelWriter(self.reports_file, engine="openpyxl") as writer:
                report.to_excel(writer, sheet_name=sheet_name[:31], index=False)
