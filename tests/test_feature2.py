import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.components.dialog_attendance_session import (
    attendance_session_detail_frames,
    attendance_session_summary,
)
from src.database import db


class _FeatureTwoQuery:
    def __init__(self, database, table_name):
        self.database = database
        self.table_name = table_name
        self.operation = "select"
        self.payload = None
        self.filters = []

    def select(self, _columns):
        self.operation = "select"
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        return self

    def delete(self):
        self.operation = "delete"
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def limit(self, _count):
        return self

    def order(self, _column, desc=False):
        return self

    def execute(self):
        self.database.operations.append(
            (self.table_name, self.operation, self.payload, self.filters)
        )

        if self.operation == "select":
            return SimpleNamespace(
                data=self.database.select_rows.get(self.table_name, [])
            )
        if self.operation == "insert" and self.table_name == "attendance_sessions":
            return SimpleNamespace(data=[{"session_id": 51, **self.payload}])
        if self.operation == "insert" and self.table_name == "attendance_logs":
            return SimpleNamespace(
                data=[
                    {"id": index + 1, **row}
                    for index, row in enumerate(self.payload)
                ]
            )
        if self.operation == "insert" and self.table_name == "attendance_corrections":
            return SimpleNamespace(data=[{"correction_id": 8, **self.payload}])
        if self.operation == "update" and self.table_name == "attendance_sessions":
            return SimpleNamespace(data=[{"session_id": 51, **self.payload}])
        if self.operation == "update" and self.table_name == "attendance_logs":
            return SimpleNamespace(data=[{"id": 4, **self.payload}])
        return SimpleNamespace(data=[{"deleted": True}])


class _FeatureTwoSupabase:
    def __init__(self, select_rows=None):
        self.select_rows = select_rows or {}
        self.operations = []

    def table(self, table_name):
        return _FeatureTwoQuery(self, table_name)


class FeatureTwoTests(unittest.TestCase):
    # FEATURE 2: One confirmation creates one session and links every unique
    # student log to the generated session ID.
    def test_session_save_links_logs_and_preserves_ai_status(self):
        fake = _FeatureTwoSupabase()
        logs = [
            {
                "student_id": 7,
                "ai_is_present": False,
                "is_present": True,
            },
            {
                "student_id": 9,
                "ai_is_present": True,
                "is_present": True,
            },
        ]

        with patch.object(db, "supabase", fake):
            session = db.create_attendance_session_with_logs(
                subject_id=3,
                teacher_id=2,
                title="Finite Automata",
                attendance_method="face",
                attendance_logs=logs,
                started_at="2026-08-27T10:00:00+00:00",
            )

        self.assertEqual(session["session_id"], 51)
        inserted_logs = next(
            operation[2]
            for operation in fake.operations
            if operation[0] == "attendance_logs" and operation[1] == "insert"
        )
        self.assertEqual({row["session_id"] for row in inserted_logs}, {51})
        self.assertFalse(inserted_logs[0]["ai_is_present"])
        self.assertTrue(inserted_logs[0]["is_present"])

    # FEATURE 2: A correction changes the final value and writes its reason and
    # previous value to the audit table.
    def test_correction_creates_audit_history(self):
        fake = _FeatureTwoSupabase(
            select_rows={
                "attendance_logs": [
                    {"id": 4, "session_id": 51, "is_present": False}
                ]
            }
        )

        with patch.object(db, "supabase", fake):
            result = db.correct_attendance_record(
                attendance_log_id=4,
                teacher_id=2,
                new_status=True,
                reason="Student was visible in another photo",
            )

        self.assertTrue(result["changed"])
        correction = next(
            operation[2]
            for operation in fake.operations
            if operation[0] == "attendance_corrections"
            and operation[1] == "insert"
        )
        self.assertFalse(correction["previous_status"])
        self.assertTrue(correction["new_status"])
        self.assertEqual(correction["corrected_by"], 2)

    # FEATURE 2: Summaries are based on session IDs, so two lectures never merge.
    def test_each_lecture_remains_a_separate_summary_row(self):
        sessions = [
            {
                "session_id": 1,
                "title": "Lecture 1",
                "started_at": "2026-08-27T10:00:00+00:00",
                "attendance_method": "face",
                "status": "completed",
                "subjects": {"name": "Automata", "subject_code": "CS100"},
                "attendance_logs": [{"is_present": True}, {"is_present": False}],
            },
            {
                "session_id": 2,
                "title": "Lecture 2",
                "started_at": "2026-08-27T10:00:00+00:00",
                "attendance_method": "voice",
                "status": "completed",
                "subjects": {"name": "Automata", "subject_code": "CS100"},
                "attendance_logs": [{"is_present": True}],
            },
        ]

        summary = attendance_session_summary(sessions)

        self.assertEqual(len(summary), 2)
        self.assertEqual(list(summary["Session ID"]), [1, 2])

    # FEATURE 2: Detail view keeps AI and final decisions visibly separate.
    def test_detail_frame_distinguishes_corrected_result(self):
        session = {
            "attendance_logs": [
                {
                    "id": 4,
                    "student_id": 7,
                    "ai_is_present": False,
                    "is_present": True,
                    "students": {"name": "Test Student"},
                    "attendance_corrections": [],
                }
            ]
        }

        records, _ = attendance_session_detail_frames(session)

        self.assertEqual(records.iloc[0]["AI Status"], "Absent")
        self.assertEqual(records.iloc[0]["Final Status"], "Present")
        self.assertEqual(records.iloc[0]["Corrected"], "Yes")


if __name__ == "__main__":
    unittest.main()
