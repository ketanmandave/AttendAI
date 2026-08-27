import unittest

import numpy as np
import pandas as pd

from src.components.dialog_attendence_result import _apply_reviewed_statuses
from src.pipelines.facePipeline import assess_image_quality, match_face_embedding


class FeatureOneTests(unittest.TestCase):
    # FEATURE 1: A flat image represents a blurred/low-detail capture and must
    # be rejected before the recognition model runs.
    def test_image_quality_rejects_blurred_image(self):
        blurred = np.full((200, 200, 3), 128, dtype=np.uint8)

        result = assess_image_quality(blurred)

        self.assertFalse(result["accepted"])
        self.assertIn("Image is too blurred.", result["reasons"])

    # FEATURE 1: A high-detail, correctly exposed image should pass the basic
    # quality gate. Face presence is checked separately by dlib.
    def test_image_quality_accepts_detailed_image(self):
        checkerboard = np.indices((200, 200)).sum(axis=0) % 2
        image = np.repeat((checkerboard * 255)[:, :, None], 3, axis=2).astype(
            np.uint8
        )

        result = assess_image_quality(image)

        self.assertTrue(result["accepted"])

    # FEATURE 1: Similar first and second candidates must be reviewed instead
    # of forcing the closest identity.
    def test_similar_students_are_marked_for_review(self):
        students = [
            {
                "student_id": 1,
                "name": "Student One",
                "face_embeddings": [np.zeros(128).tolist()],
            },
            {
                "student_id": 2,
                "name": "Student Two",
                "face_embeddings": [np.full(128, 0.004).tolist()],
            },
        ]

        result = match_face_embedding(np.full(128, 0.002), students)

        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(len(result["candidates"]), 2)

    # FEATURE 1: Multiple samples allow a student to match a later sample even
    # when the first registration image differs substantially.
    def test_best_of_multiple_face_samples_is_used(self):
        students = [
            {
                "student_id": 7,
                "name": "Test Student",
                "face_embeddings": [
                    np.full(128, 0.1).tolist(),
                    np.zeros(128).tolist(),
                ],
            }
        ]

        result = match_face_embedding(np.full(128, 0.01), students)

        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["student_id"], 7)

    # FEATURE 1: Teacher choices must update the exact payload later inserted
    # into attendance_logs, and unresolved rows must block saving.
    def test_teacher_review_updates_attendance_payload(self):
        reviewed = pd.DataFrame(
            [
                {"ID": 1, "Status": "Present"},
                {"ID": 2, "Status": "Needs Review"},
            ]
        )
        logs = [
            {"student_id": 1, "is_present": False},
            {"student_id": 2, "is_present": False},
        ]

        unresolved = _apply_reviewed_statuses(reviewed, logs)

        self.assertTrue(logs[0]["is_present"])
        self.assertFalse(logs[1]["is_present"])
        self.assertEqual(unresolved, 1)


if __name__ == "__main__":
    unittest.main()
