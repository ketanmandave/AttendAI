"""Local visual-review harness using synthetic data and production screens."""

from unittest.mock import patch

import streamlit as st

from src.screens import student_screen, teacher_screen


st.set_page_config(page_title="AttendIQ UI Review", layout="wide")
view = st.query_params.get("view", "teacher")


if view == "student":
    st.session_state["student_data"] = {
        "student_id": 101,
        "name": "Aarav Sharma",
        "face_embedding": [0.1],
        "voice_embedding": [0.1],
    }
    sample_subjects = [
        {"subject_id": 1, "subjects": {"subject_id": 1, "name": "Automata Theory", "subject_code": "CS100", "section": "A"}},
        {"subject_id": 2, "subjects": {"subject_id": 2, "name": "Database Systems", "subject_code": "CS223", "section": "A"}},
        {"subject_id": 3, "subjects": {"subject_id": 3, "name": "Machine Learning", "subject_code": "CS310", "section": "B"}},
    ]
    sample_logs = [
        *[{"subject_id": 1, "is_present": index < 7} for index in range(10)],
        *[{"subject_id": 2, "is_present": index < 9} for index in range(10)],
        *[{"subject_id": 3, "is_present": index < 4} for index in range(5)],
    ]
    with (
        patch.object(student_screen, "get_student_subjects", return_value=sample_subjects),
        patch.object(student_screen, "get_student_attendance", return_value=sample_logs),
    ):
        student_screen.student_screen()
else:
    st.session_state["teacher_data"] = {
        "teacher_id": 7,
        "name": "Dr. Meera Joshi",
        "username": "meera",
    }
    sample_subjects = [
        {"subject_id": 1, "name": "Automata Theory", "subject_code": "CS100", "section": "A", "total_students": 42, "total_classes": 18},
        {"subject_id": 2, "name": "Database Systems", "subject_code": "CS223", "section": "A", "total_students": 38, "total_classes": 15},
    ]
    with patch.object(teacher_screen, "get_teacher_subjects", return_value=sample_subjects):
        teacher_screen.teacher_screen()
