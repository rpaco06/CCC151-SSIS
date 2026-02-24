import re


def is_empty(data: dict) -> bool:
    return not all(data.values())


def valid_student_id(sid: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{4}$", sid))


def is_duplicate(rows: list, key: str, value: str) -> bool:
    return any(r[key] == value for r in rows)


def validate_college(data: dict) -> str | None:
    if is_empty(data):
        return "Please fill in all fields."
    return None


def validate_program(data: dict) -> str | None:
    if is_empty(data):
        return "Please fill in all fields."
    return None


def validate_student(data: dict) -> str | None:
    if is_empty(data):
        return "Please fill in all fields."
    if not valid_student_id(data["id"]):
        return "Student ID must follow the format YYYY-NNNN (e.g. 2024-0001)."
    return None