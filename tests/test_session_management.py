import unittest
from unittest.mock import patch

from src.auth import session_manager


class SessionManagementTests(unittest.TestCase):
    def setUp(self):
        session_manager.st.session_state.clear()

    def tearDown(self):
        session_manager.st.session_state.clear()

    def test_token_hash_is_deterministic_and_does_not_store_raw_token(self):
        raw_token = "private-browser-token"

        first_hash = session_manager.hash_session_token(raw_token)

        self.assertEqual(first_hash, session_manager.hash_session_token(raw_token))
        self.assertNotEqual(raw_token, first_hash)
        self.assertEqual(64, len(first_hash))

    def test_current_session_fallback_keeps_valid_teacher_logged_in(self):
        session_manager.start_current_teacher_session(
            {
                "teacher_id": 12,
                "username": "fallback_teacher",
                "name": "Fallback Teacher",
                "password": "must-not-enter-session-state",
            }
        )

        self.assertTrue(session_manager.st.session_state["is_logged_in"])
        self.assertEqual("teacher", session_manager.st.session_state["login_type"])
        self.assertNotIn(
            "password", session_manager.st.session_state["teacher_data"]
        )

    @patch.object(session_manager, "_delete_cookie")
    @patch.object(session_manager, "get_teacher_for_session")
    @patch.object(session_manager, "_cookie_token", return_value="valid-token")
    def test_refresh_restores_teacher_from_valid_cookie(
        self, _cookie_token, get_session, delete_cookie
    ):
        get_session.return_value = {
            "session_id": 8,
            "teacher": {
                "teacher_id": 3,
                "username": "teacher",
                "name": "Teacher One",
            },
        }

        restored = session_manager.restore_teacher_session()

        self.assertTrue(restored)
        self.assertEqual("teacher", session_manager.st.session_state["login_type"])
        self.assertEqual(
            3, session_manager.st.session_state["teacher_data"]["teacher_id"]
        )
        delete_cookie.assert_not_called()

    @patch.object(session_manager, "_delete_cookie")
    @patch.object(session_manager, "get_teacher_for_session", return_value=None)
    @patch.object(session_manager, "_cookie_token", return_value="expired-token")
    def test_expired_or_revoked_cookie_is_rejected(
        self, _cookie_token, _get_session, delete_cookie
    ):
        restored = session_manager.restore_teacher_session()

        self.assertFalse(restored)
        self.assertNotIn("teacher_data", session_manager.st.session_state)
        delete_cookie.assert_called_once()

    @patch.object(session_manager, "_delete_cookie")
    @patch.object(session_manager, "revoke_teacher_session")
    @patch.object(session_manager, "_cookie_token", return_value="logout-token")
    def test_logout_revokes_token_and_clears_auth_state(
        self, _cookie_token, revoke_session, delete_cookie
    ):
        session_manager.st.session_state.update(
            {
                "teacher_data": {"teacher_id": 3},
                "is_logged_in": True,
                "user_role": "teacher",
                "login_type": "teacher",
            }
        )

        session_manager.logout_teacher()

        revoke_session.assert_called_once_with(
            session_manager.hash_session_token("logout-token")
        )
        delete_cookie.assert_called_once()
        self.assertNotIn("teacher_data", session_manager.st.session_state)
        self.assertIsNone(session_manager.st.session_state["login_type"])


if __name__ == "__main__":
    unittest.main()
