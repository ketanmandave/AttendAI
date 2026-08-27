import pandas as pd

from src.components.dialog_attendence_result import show_attendance_result


# FEATURE 1: Small AppTest harness for the teacher-review result state.
show_attendance_result(
    pd.DataFrame(
        [
            {
                "Name": "Possible Student",
                "ID": 2,
                "Detected in": "Photo 1",
                "Similarity": "72%",
                "Status": "Needs Review",
            }
        ]
    ),
    [
        {
            "student_id": 2,
            "subject_id": 4,
            "timestamp": "2026-08-27T10:00:00+00:00",
            "is_present": False,
        }
    ],
    source="face",
)
