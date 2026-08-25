import logging

import streamlit as st

from src.database.db import (
    enroll_student_to_subject,
    get_subject_by_code,
    is_student_enrolled,
)


logger = logging.getLogger(__name__)


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.caption("Enter the subject code shared by your teacher.")
    shared_code = st.query_params.get("join-code", "")
    join_code = st.text_input(
        "Subject code",
        value=str(shared_code).strip().upper(),
        placeholder="Example: CS101",
    )

    if not st.button("Enroll now", type="primary", width="stretch"):
        return

    code = join_code.strip().upper()
    if not code:
        st.warning("Please enter a subject code.")
        return

    try:
        subject = get_subject_by_code(code)
        if subject is None:
            st.error("No subject was found with that code.")
            return

        student_id = st.session_state.student_data["student_id"]
        if is_student_enrolled(student_id, subject["subject_id"]):
            st.warning("You are already enrolled in this subject.")
            return

        enrolled = enroll_student_to_subject(student_id, subject["subject_id"])
        if not enrolled:
            st.error("Enrollment could not be saved. Please try again.")
            return

        if "join-code" in st.query_params:
            del st.query_params["join-code"]
        st.toast(f"Enrolled in {subject['name']} successfully!", icon="✅")
        st.rerun()
    except Exception:
        logger.exception("Student enrollment database request failed")
        st.error("Enrollment failed. Check the database connection and try again.")
