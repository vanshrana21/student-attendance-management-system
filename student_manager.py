"""Student registration, search, listing, and editing."""
from excel_handler import STUDENT_COLUMNS


class StudentManager:
    def __init__(self, excel):
        self.excel = excel

    def add_student(self, student_id, name, department, semester, section):
        values = [str(x).strip() for x in (student_id, name, department, semester, section)]
        if any(not value for value in values):
            raise ValueError("Every student field is required.")
        frame = self.excel.load_students()
        if frame["Student ID"].str.casefold().eq(values[0].casefold()).any():
            raise ValueError(f"Student ID {values[0]} already exists.")
        frame.loc[len(frame)] = values
        self.excel.save_students(frame)

    def list_students(self):
        return self.excel.load_students().sort_values("Student ID", kind="stable")

    def search(self, search_text):
        students = self.excel.load_students()
        query = str(search_text).strip()
        mask = students["Student ID"].str.contains(query, case=False, na=False, regex=False) | students["Student Name"].str.contains(query, case=False, na=False, regex=False)
        return students[mask]

    def edit_student(self, student_id, name, department, semester, section):
        values = [str(x).strip() for x in (name, department, semester, section)]
        if not all(values):
            raise ValueError("Every student field is required.")
        frame = self.excel.load_students()
        mask = frame["Student ID"].str.casefold().eq(str(student_id).strip().casefold())
        if not mask.any():
            raise ValueError(f"No student with ID {student_id} was found.")
        frame.loc[mask, STUDENT_COLUMNS[1:]] = values
        self.excel.save_students(frame)
