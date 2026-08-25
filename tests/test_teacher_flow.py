import io
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from streamlit.testing.v1 import AppTest
from PIL import Image

from src.database import db
from src.components.dialog_add_photo import _add_image
from src.components.dialog_attendence_result import _attendance_csv
from src.pipelines import facePipeline

TEST_ROOT = Path(__file__).resolve().parent


class _SessionState(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class _Query:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.inserted = None
        self.selected = None
        self.teacher_id = None

    def select(self, columns):
        self.selected = columns
        return self

    def insert(self, data):
        self.inserted = data
        self.rows = [data]
        return self

    def eq(self, column, value):
        if column == "teacher_id":
            self.teacher_id = value
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)


class _Supabase:
    def __init__(self, rows=None):
        self.query = _Query(rows)
        self.table_name = None

    def table(self, name):
        self.table_name = name
        return self.query


class TeacherFlowTests(unittest.TestCase):
    def test_single_registered_student_requires_a_strict_face_match(self):
        model = {
            "classifier": None,
            "embeddings": [np.zeros(128)],
            "student_ids": [9],
        }

        with (
            patch.object(facePipeline, "get_trained_model", return_value=model),
            patch.object(
                facePipeline,
                "get_face_embeddings",
                return_value=[np.full(128, 0.045)],
            ),
        ):
            rejected, _, _ = facePipeline.predict_attendance(np.zeros((2, 2, 3)))

        with (
            patch.object(facePipeline, "get_trained_model", return_value=model),
            patch.object(
                facePipeline,
                "get_face_embeddings",
                return_value=[np.full(128, 0.02)],
            ),
        ):
            accepted, _, _ = facePipeline.predict_attendance(np.zeros((2, 2, 3)))

        self.assertEqual(rejected, {})
        self.assertEqual(accepted, {9: True})

    def test_attendance_result_csv_contains_visible_rows(self):
        import pandas as pd

        result = _attendance_csv(
            pd.DataFrame([{"Name": "Test Student", "Status": "Present"}])
        ).decode("utf-8-sig")

        self.assertIn("Name,Status", result)
        self.assertIn("Test Student,Present", result)

    def test_photo_dialog_copies_images_and_rejects_duplicates(self):
        image_buffer = io.BytesIO()
        Image.new("RGB", (2, 2), color=(37, 99, 235)).save(
            image_buffer, format="PNG"
        )
        uploaded = SimpleNamespace(getvalue=image_buffer.getvalue)
        state = _SessionState(attendance_images=[], attendance_image_hashes=set())

        with patch("src.components.dialog_add_photo.st.session_state", state):
            first_result = _add_image(uploaded)
            duplicate_result = _add_image(uploaded)

        self.assertEqual(first_result, "added")
        self.assertEqual(duplicate_result, "duplicate")
        self.assertEqual(len(state.attendance_images), 1)
        self.assertEqual(state.attendance_images[0].mode, "RGB")

    def test_successful_login_redirects_to_dashboard_in_one_click(self):
        teacher = {
            "teacher_id": 7,
            "username": "teacher1",
            "name": "Test Teacher",
        }
        subjects = [
            {
                "subject_id": 3,
                "subject_code": "CS101",
                "name": "Computer Science",
                "section": "A",
                "total_students": 12,
                "total_classes": 2,
            },
            {
                "subject_id": 4,
                "subject_code": "MA101",
                "name": "Mathematics",
                "section": "B",
                "total_students": 10,
                "total_classes": 3,
            },
        ]

        with (
            patch("src.screens.teacher_screen.teacher_login", return_value=teacher),
            patch("src.screens.teacher_screen.get_teacher_subjects", return_value=subjects),
            patch(
                "src.screens.teacher_screen.get_subject_students",
                return_value=[
                    {
                        "student_id": 9,
                        "students": {
                            "student_id": 9,
                            "name": "Test Student",
                            "voice_embedding": [0.1],
                        },
                    }
                ],
            ),
            patch(
                "src.screens.teacher_screen.predict_attendance",
                return_value=({9: True}, [9], 1),
            ),
            patch(
                "src.screens.teacher_screen.get_attendance_records_for_teacher",
                return_value=[
                    {
                        "id": 1,
                        "timestamp": "2026-08-25T10:00:00+00:00",
                        "student_id": 9,
                        "subject_id": 3,
                        "is_present": True,
                        "students": {"student_id": 9, "name": "Test Student"},
                        "subjects": {
                            "subject_id": 3,
                            "name": "Computer Science",
                            "subject_code": "CS101",
                            "section": "A",
                        },
                    },
                    {
                        "id": 2,
                        "timestamp": "2026-08-25T10:00:00+00:00",
                        "student_id": 10,
                        "subject_id": 3,
                        "is_present": False,
                        "students": {"student_id": 10, "name": "Second Student"},
                        "subjects": {
                            "subject_id": 3,
                            "name": "Computer Science",
                            "subject_code": "CS101",
                            "section": "A",
                        },
                    },
                    {
                        "id": 3,
                        "timestamp": "2026-08-25T09:00:00+00:00",
                        "student_id": 9,
                        "subject_id": 3,
                        "is_present": True,
                        "students": {"student_id": 9, "name": "Test Student"},
                        "subjects": {
                            "subject_id": 3,
                            "name": "Computer Science",
                            "subject_code": "CS101",
                            "section": "A",
                        },
                    },
                ],
            ),
        ):
            app = AppTest.from_file(TEST_ROOT.parent / "app.py")
            app.run(timeout=30)
            app.button(key="teacher_portal").click().run(timeout=30)
            app.text_input(key="teacherUsername").set_value("teacher1")
            app.text_input(key="teacherPassword").set_value("password")
            app.button(key="loginButton").click().run(timeout=30)
            self.assertEqual(app.session_state["teacher_data"]["teacher_id"], 7)
            self.assertTrue(
                any("Welcome, Test Teacher!" in item.value for item in app.subheader)
            )
            self.assertEqual(
                app.button(key="open_attendance_photos").label,
                "Add Photos",
            )

            app.button(key="open_attendance_photos").click().run(timeout=30)
            self.assertEqual(app.session_state["attendance_images"], [])
            self.assertTrue(app.button(key="add_camera_snapshot").disabled)
            app.button(key="finish_adding_photos").click().run(timeout=30)

            app.session_state["attendance_images"] = [
                Image.new("RGB", (4, 4), color=(255, 255, 255))
            ]
            app.run(timeout=30)
            self.assertFalse(app.button(key="run_face_attendance").disabled)
            app.button(key="run_face_attendance").click().run(timeout=30)
            self.assertEqual(
                app.button(key="confirm_face_attendance").label,
                "Confirm & Save",
            )
            app.button(key="discard_face_attendance").click().run(timeout=30)

            app.button(key="teacher_manage_subjects_tab").click().run(timeout=30)
            self.assertEqual(
                app.session_state["current_teacher_tab"], "manage_subjects"
            )
            self.assertEqual(app.button(key="share_subject_3").label, "Share class: CS101")
            self.assertEqual(app.button(key="share_subject_4").label, "Share class: MA101")

            app.button(key="teacher_attendance_records_tab").click().run(timeout=30)
            self.assertEqual(
                app.session_state["current_teacher_tab"], "attendance_records"
            )
            self.assertEqual(len(app.dataframe), 1)
            records_table = app.dataframe[0].value
            self.assertEqual(len(records_table), 2)
            self.assertEqual(
                records_table.iloc[0]["Attendance Stats"], "✅ 1 / 2 Students"
            )
            self.assertEqual(
                records_table.iloc[1]["Attendance Stats"], "✅ 1 / 1 Students"
            )
            self.assertEqual(
                app.get("download_button")[0].label,
                "Download attendance sessions as CSV",
            )

    def test_subject_queries_match_sql_schema_and_normalize_counts(self):
        fake = _Supabase(
            [
                {
                    "subject_id": 3,
                    "subject_code": "CS101",
                    "name": "Computer Science",
                    "section": "A",
                    "teacher_id": 7,
                    "subject_student": [{"count": 12}],
                    "attendance_logs": [
                        {"timestamp": "2026-08-24T09:00:00+00:00"},
                        {"timestamp": "2026-08-24T09:00:03+00:00"},
                        {"timestamp": "2026-08-25T09:00:00+00:00"},
                    ],
                }
            ]
        )

        with patch.object(db, "supabase", fake):
            subjects = db.get_teacher_subjects(7)

        self.assertEqual(fake.table_name, "subjects")
        self.assertEqual(
            fake.query.selected,
            "*, subject_student(count), attendance_logs(timestamp)",
        )
        self.assertEqual(fake.query.teacher_id, 7)
        self.assertEqual(subjects[0]["total_students"], 12)
        self.assertEqual(subjects[0]["total_classes"], 2)

    def test_subject_creation_uses_canonical_column_names(self):
        fake = _Supabase()

        with patch.object(db, "supabase", fake):
            db.create_subject("CS101", "Computer Science", "A", 7)

        self.assertEqual(
            fake.query.inserted,
            {
                "subject_code": "CS101",
                "name": "Computer Science",
                "section": "A",
                "teacher_id": 7,
            },
        )

    def test_bulk_attendance_uses_attendance_logs_table(self):
        fake = _Supabase()
        logs = [
            {
                "student_id": 9,
                "subject_id": 3,
                "timestamp": "2026-08-25T10:00:00+00:00",
                "is_present": True,
            }
        ]

        with patch.object(db, "supabase", fake):
            result = db.create_attendance(logs)

        self.assertEqual(fake.table_name, "attendance_logs")
        self.assertEqual(fake.query.inserted, logs)
        self.assertTrue(result)

    def test_teacher_attendance_query_includes_student_and_filters_subject_owner(self):
        rows = [
            {
                "id": 1,
                "student_id": 9,
                "subject_id": 3,
                "is_present": True,
                "students": {"student_id": 9, "name": "Test Student"},
                "subjects": {
                    "subject_id": 3,
                    "name": "Computer Science",
                    "subject_code": "CS101",
                    "section": "A",
                    "teacher_id": 7,
                },
            }
        ]
        fake = _Supabase(rows)

        with patch.object(db, "supabase", fake):
            result = db.get_attendance_records_for_teacher(7)

        self.assertEqual(fake.table_name, "attendance_logs")
        self.assertIn("students(student_id, name)", fake.query.selected)
        self.assertIn("subjects!inner", fake.query.selected)
        self.assertEqual(result, rows)

    def test_student_dashboard_renders_enrollments_and_attendance(self):
        enrollments = [
            {
                "subject_id": 3,
                "subjects": {
                    "subject_id": 3,
                    "subject_code": "CS101",
                    "name": "Computer Science",
                    "section": "A",
                },
            },
            {
                "subject_id": 4,
                "subjects": {
                    "subject_id": 4,
                    "subject_code": "MA101",
                    "name": "Mathematics",
                    "section": "B",
                },
            },
        ]
        attendance = [
            {"subject_id": 3, "is_present": True},
            {"subject_id": 3, "is_present": False},
            {"subject_id": 4, "is_present": True},
        ]

        with (
            patch(
                "src.screens.student_screen.get_student_subjects",
                return_value=enrollments,
            ),
            patch(
                "src.screens.student_screen.get_student_attendance",
                return_value=attendance,
            ),
            patch(
                "src.screens.student_screen.subject_card",
                side_effect=lambda **kwargs: kwargs["footer_callback"](),
            ) as card_mock,
        ):
            app = AppTest.from_file(TEST_ROOT.parent / "app.py")
            app.session_state["login_type"] = "student"
            app.session_state["student_data"] = {
                "student_id": 9,
                "name": "Test Student",
                "face_embedding": [0.1],
                "voice_embedding": None,
            }
            app.run(timeout=30)

        self.assertEqual(
            app.button(key="unenroll_subject_3_CS101").label,
            "Unenroll from this subject",
        )
        self.assertEqual(
            app.button(key="unenroll_subject_4_MA101").label,
            "Unenroll from this subject",
        )
        self.assertEqual(card_mock.call_count, 2)
        first_card = card_mock.call_args_list[0].kwargs
        second_card = card_mock.call_args_list[1].kwargs
        self.assertEqual(first_card["name"], "Computer Science")
        self.assertEqual(
            first_card["stats"],
            [("📅", "Total", 2), ("✅", "Attended", 1)],
        )
        self.assertEqual(second_card["name"], "Mathematics")
        self.assertEqual(
            second_card["stats"],
            [("📅", "Total", 1), ("✅", "Attended", 1)],
        )

    def test_shared_code_opens_auto_enrollment_and_confirms_once(self):
        subject = {
            "subject_id": 3,
            "subject_code": "CS101",
            "name": "Computer Science",
            "section": "A",
        }

        with (
            patch("src.screens.student_screen.get_student_subjects", return_value=[]),
            patch("src.screens.student_screen.get_student_attendance", return_value=[]),
            patch(
                "src.components.dialog_auto_enroll.get_subject_by_code",
                return_value=subject,
            ) as subject_lookup,
            patch(
                "src.components.dialog_auto_enroll.is_student_enrolled",
                return_value=False,
            ),
            patch(
                "src.components.dialog_auto_enroll.enroll_student_to_subject",
                return_value=[{"student_id": 9, "subject_id": 3}],
            ) as enroll_mock,
        ):
            app = AppTest.from_file(TEST_ROOT.parent / "app.py")
            app.session_state["login_type"] = "student"
            app.session_state["is_logged_in"] = True
            app.session_state["user_role"] = "student"
            app.session_state["student_data"] = {
                "student_id": 9,
                "name": "Test Student",
                "face_embedding": [0.1],
                "voice_embedding": None,
            }
            app.query_params["join-code"] = "cs101"
            app.run(timeout=30)
            app.button(key="confirm_auto_enroll_3").click().run(timeout=30)

        self.assertEqual(subject_lookup.call_count, 2)
        self.assertTrue(
            all(call.args == ("CS101",) for call in subject_lookup.call_args_list)
        )
        enroll_mock.assert_called_once_with(9, 3)
        self.assertNotIn("join-code", app.query_params)


if __name__ == "__main__":
    unittest.main()
