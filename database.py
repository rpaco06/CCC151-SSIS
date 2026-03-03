import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLLEGES_FILE = os.path.join(BASE_DIR, "data", "colleges.csv")
PROGRAMS_FILE = os.path.join(BASE_DIR, "data", "programs.csv")
STUDENTS_FILE = os.path.join(BASE_DIR, "data", "students.csv")

COLLEGE_FIELDS = ["code", "name"]
PROGRAM_FIELDS = ["code", "name", "college"]
STUDENT_FIELDS = ["id", "firstname", "lastname", "program", "year", "gender"]


def load_csv(filepath, fields):
    if not os.path.exists(filepath):
        return []
    with open(filepath, newline="") as f:
        return list(csv.DictReader(f))

def save_csv(filepath, fields, rows):
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


# colleges
def load_colleges():
    return load_csv(COLLEGES_FILE, COLLEGE_FIELDS)

def save_colleges(rows):
    save_csv(COLLEGES_FILE, COLLEGE_FIELDS, rows)

def get_college_codes():
    return [r["code"] for r in load_colleges()]


# programs
def load_programs():
    return load_csv(PROGRAMS_FILE, PROGRAM_FIELDS)

def save_programs(rows):
    save_csv(PROGRAMS_FILE, PROGRAM_FIELDS, rows)

def get_program_codes():
    return [r["code"] for r in load_programs()]


# students
def load_students():
    return load_csv(STUDENTS_FILE, STUDENT_FIELDS)

def save_students(rows):
    save_csv(STUDENTS_FILE, STUDENT_FIELDS, rows)


# cascade helpers
def nullify_programs_college(old_college_code):
    """when a college is deleted or its code changes, set affected programs' college to empty"""
    programs = load_programs()
    updated = False
    for p in programs:
        if p["college"] == old_college_code:
            p["college"] = ""
            updated = True
    if updated:
        save_programs(programs)

def nullify_students_program(old_program_code):
    """when a program is deleted or its code changes, set affected students' program to empty"""
    students = load_students()
    updated = False
    for s in students:
        if s["program"] == old_program_code:
            s["program"] = ""
            updated = True
    if updated:
        save_students(students)