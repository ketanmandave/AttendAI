import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


TEST_ROOT = Path(__file__).resolve().parent


class FeatureOneUiTests(unittest.TestCase):
    # FEATURE 1: An unresolved face must render in the review editor and keep
    # the save action disabled until the teacher chooses a final status.
    def test_uncertain_result_requires_teacher_decision(self):
        app = AppTest.from_file(TEST_ROOT / "feature1_review_app.py")
        app.run(timeout=30)

        self.assertFalse(app.exception)
        # Streamlit AppTest exposes both dataframe and data_editor as Dataframe.
        self.assertEqual(len(app.dataframe), 1)
        self.assertIn("Status", app.dataframe[0].value.columns)
        self.assertTrue(app.button(key="confirm_face_attendance").disabled)
        self.assertTrue(
            any("Resolve 1 uncertain" in warning.value for warning in app.warning)
        )


if __name__ == "__main__":
    unittest.main()
