"""Persistent teacher login backed by a hashed, revocable session token."""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

import streamlit as st

try:
    import extra_streamlit_components as stx
except ImportError:  # Keeps the normal login usable until dependencies install.
    stx = None

from src.database.db import (
    create_teacher_session,
    get_teacher_for_session,
    revoke_teacher_session,
)

logger = logging.getLogger(__name__)

# SESSION MANAGEMENT: A random opaque token lives for 30 days in the browser;
# Supabase stores only its hash so a database leak does not expose live tokens.
SESSION_COOKIE_NAME = "attendiq_teacher_session"
SESSION_LIFETIME = timedelta(days=30)
_RAW_TOKEN_STATE_KEY = "_teacher_session_token"
_RESTORE_CHECKED_STATE_KEY = "_teacher_session_restore_checked"


def hash_session_token(token):
    """Return the deterministic server-side representation of a raw token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _cookie_token():
    token = st.session_state.get(_RAW_TOKEN_STATE_KEY)
    if token:
        return token
    try:
        return st.context.cookies.get(SESSION_COOKIE_NAME)
    except Exception:
        logger.exception("Could not read the teacher session cookie")
        return None


def _cookie_manager(component_key):
    if stx is None:
        raise RuntimeError(
            "extra-streamlit-components is not installed; install requirements.txt"
        )
    return stx.CookieManager(key=component_key)


def _write_cookie(token, expires_at):
    manager = _cookie_manager("teacher_session_cookie_writer")
    try:
        app_url = st.context.url
    except Exception:
        app_url = ""
    manager.set(
        SESSION_COOKIE_NAME,
        token,
        key="set_teacher_session_cookie",
        path="/",
        expires_at=expires_at,
        secure=app_url.startswith("https://"),
        same_site="strict",
    )


def _delete_cookie():
    if stx is None:
        return
    try:
        manager = _cookie_manager("teacher_session_cookie_remover")
        manager.delete(SESSION_COOKIE_NAME, key="delete_teacher_session_cookie")
    except (KeyError, RuntimeError):
        # CookieManager raises KeyError when the cookie is already absent.
        pass
    except Exception:
        logger.exception("Could not remove the teacher session cookie")


def _apply_teacher_login(teacher, raw_token=None):
    # SESSION MANAGEMENT: Never carry the bcrypt password hash returned by the
    # password-login query into browser-specific Streamlit session state.
    safe_teacher = {
        key: teacher.get(key)
        for key in ("teacher_id", "username", "name")
        if key in teacher
    }
    st.session_state["is_logged_in"] = True
    st.session_state["teacher_data"] = safe_teacher
    st.session_state["user_role"] = "teacher"
    st.session_state["login_type"] = "teacher"
    st.session_state["teacher_login_type"] = "login"
    if raw_token:
        st.session_state[_RAW_TOKEN_STATE_KEY] = raw_token


def start_current_teacher_session(teacher):
    """Keep a valid login usable when persistent storage is unavailable."""
    _apply_teacher_login(teacher)
    st.session_state[_RESTORE_CHECKED_STATE_KEY] = True


def start_teacher_session(teacher):
    """Create a persistent session after a successful password login."""
    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + SESSION_LIFETIME
    session = create_teacher_session(
        teacher["teacher_id"],
        hash_session_token(raw_token),
        expires_at.isoformat(),
    )
    if not session:
        raise RuntimeError("The persistent teacher session could not be created")

    try:
        _write_cookie(raw_token, expires_at)
    except Exception:
        # Do not leave an unusable active row when cookie creation fails.
        try:
            revoke_teacher_session(hash_session_token(raw_token))
        except Exception:
            logger.exception("Could not roll back the failed teacher session")
        raise

    _apply_teacher_login(teacher, raw_token)
    st.session_state[_RESTORE_CHECKED_STATE_KEY] = True
    return session


def restore_teacher_session():
    """Restore teacher state once when a new Streamlit connection starts."""
    if st.session_state.get("teacher_data"):
        return True
    if st.session_state.get(_RESTORE_CHECKED_STATE_KEY):
        return False

    st.session_state[_RESTORE_CHECKED_STATE_KEY] = True
    raw_token = _cookie_token()
    if not raw_token:
        return False

    try:
        session = get_teacher_for_session(hash_session_token(raw_token))
    except Exception:
        # A temporary database failure should not destroy a still-valid cookie.
        logger.exception("Could not validate the persistent teacher session")
        return False

    if not session:
        _delete_cookie()
        return False

    _apply_teacher_login(session["teacher"], raw_token)
    return True


def logout_teacher():
    """Revoke the current token, clear auth state, and remove its cookie."""
    raw_token = _cookie_token()
    if raw_token:
        try:
            revoke_teacher_session(hash_session_token(raw_token))
        except Exception:
            # Local state is still cleared; an expired/revoked cleanup can occur
            # later if Supabase is temporarily unavailable.
            logger.exception("Could not revoke the teacher session")

    _delete_cookie()
    for key in (
        "is_logged_in",
        "teacher_data",
        "user_role",
        "current_teacher_tab",
        "attendance_images",
        "attendance_image_hashes",
        "selected_attendance_subject_id",
        "selected_attendance_subject",
        "voice_attendance_results",
        "photo_tab",
        _RAW_TOKEN_STATE_KEY,
    ):
        st.session_state.pop(key, None)

    # Prevent a stale request cookie from immediately restoring this connection.
    st.session_state[_RESTORE_CHECKED_STATE_KEY] = True
    st.session_state["teacher_login_type"] = "login"
    st.session_state["login_type"] = None
