import logging

import streamlit as st

from src.database.db import (
    enroll_student_to_subject,
    get_subject_by_code,
    is_student_enrolled,
)


logger = logging.getLogger(__name__)


def _dismiss_join_request():
    if "join-code" in st.query_params:
        del st.query_params["join-code"]
    st.rerun()


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):
    student = st.session_state.get("student_data")
    if not student or not student.get("student_id"):
        st.warning("Sign in as a student before joining this subject.")
        if st.button("Close", width="stretch", key="close_auto_enroll_no_student"):
            _dismiss_join_request()
        return

    code = str(subject_code or "").strip().upper()
    if not code:
        st.error("The shared subject code is empty or invalid.")
        if st.button("Close", width="stretch", key="close_auto_enroll_bad_code"):
            _dismiss_join_request()
        return

    try:
        subject = get_subject_by_code(code)
        if subject is None:
            st.error(f"No subject was found with code {code}.")
            if st.button("Close", width="stretch", key="close_auto_enroll_not_found"):
                _dismiss_join_request()
            return

        student_id = student["student_id"]
        subject_id = subject["subject_id"]
        if is_student_enrolled(student_id, subject_id):
            st.info(f"You are already enrolled in {subject['name']}.")
            if st.button("Got it", width="stretch", key="close_auto_enroll_existing"):
                _dismiss_join_request()
            return
    except Exception:
        logger.exception("Could not validate automatic enrollment for code %s", code)
        st.error("The enrollment request could not be loaded. Check the database connection.")
        if st.button("Close", width="stretch", key="close_auto_enroll_error"):
            _dismiss_join_request()
        return

    st.caption("SUBJECT INVITATION")
    st.subheader(subject["name"])
    st.write(f"Code: **{subject['subject_code']}**")
    st.write(f"Section: **{subject.get('section') or 'N/A'}**")
    st.write("Would you like to enroll in this subject?")

    decline_col, confirm_col = st.columns(2)
    with decline_col:
        if st.button(
            "No thanks",
            width="stretch",
            key=f"decline_auto_enroll_{subject_id}",
        ):
            _dismiss_join_request()

    with confirm_col:
        if st.button(
            "Enroll now",
            type="primary",
            width="stretch",
            key=f"confirm_auto_enroll_{subject_id}",
        ):
            try:
                enrolled = enroll_student_to_subject(student_id, subject_id)
                if not enrolled:
                    st.error("Enrollment could not be saved. Please try again.")
                    return

                if "join-code" in st.query_params:
                    del st.query_params["join-code"]
                st.toast(f"Enrolled in {subject['name']} successfully!", icon="✅")
                st.rerun()
            except Exception:
                logger.exception(
                    "Automatic enrollment failed for student %s and subject %s",
                    student_id,
                    subject_id,
                )
                st.error("Enrollment failed. Check the database connection and try again.")
