import logging

import streamlit as st

from src.database.db import create_subject


logger = logging.getLogger(__name__)


@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.caption("Add a subject to your teaching dashboard.")

    subject_code = st.text_input("Subject code", placeholder="CS101")
    name = st.text_input("Subject name", placeholder="Introduction to Computer Science")
    section = st.text_input("Section", placeholder="A")

    if st.button("Create subject", type="primary", width="stretch"):
        if not subject_code.strip() or not name.strip() or not section.strip():
            st.warning("Subject code, name, and section are required.")
            return

        try:
            created = create_subject(
                subject_code.strip().upper(),
                name.strip(),
                section.strip(),
                teacher_id,
            )
        except Exception:
            logger.exception("Subject creation database request failed")
            st.error("The subject could not be created. Check the database connection.")
            return
        if not created:
            st.error("The subject could not be created. Please try again.")
            return

        st.session_state.current_teacher_tab = "manage_subjects"
        st.toast(f"Subject '{name.strip()}' created successfully!", icon="✅")
        st.rerun()
