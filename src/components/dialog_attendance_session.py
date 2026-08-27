import logging

import pandas as pd
import streamlit as st

from src.database.db import (
    correct_attendance_record,
    get_attendance_session_details,
)


logger = logging.getLogger(__name__)


def _relation(value):
    """Normalize Supabase to-one relations returned as a dict or one-item list."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


# FEATURE 2: Build a stable lecture summary from real attendance session IDs.
def attendance_session_summary(sessions):
    rows = []
    for session in sessions or []:
        subject = _relation(session.get("subjects")) or {}
        logs = session.get("attendance_logs") or []
        present_count = sum(bool(log.get("is_present")) for log in logs)
        rows.append(
            {
                "Session ID": session.get("session_id"),
                "Time": session.get("started_at"),
                "Lecture": session.get("title") or "Attendance session",
                "Subject": subject.get("name", "N/A"),
                "Subject Code": subject.get("subject_code", "N/A"),
                "Method": str(session.get("attendance_method") or "N/A").title(),
                "Attendance Stats": f"✅ {present_count} / {len(logs)} Students",
                "Status": str(session.get("status") or "N/A").title(),
            }
        )
    return pd.DataFrame(rows)


# FEATURE 2: Separate the model's original decision from the teacher-controlled
# final status and collect the correction audit trail for display/download.
def attendance_session_detail_frames(session):
    record_rows = []
    correction_rows = []
    for log in session.get("attendance_logs") or []:
        student = _relation(log.get("students")) or {}
        student_name = student.get("name", "Unknown student")
        ai_present = bool(log.get("ai_is_present"))
        final_present = bool(log.get("is_present"))
        record_rows.append(
            {
                "Log ID": log.get("id"),
                "Student": student_name,
                "Student ID": log.get("student_id"),
                "AI Status": "Present" if ai_present else "Absent",
                "Final Status": "Present" if final_present else "Absent",
                "Corrected": "Yes" if ai_present != final_present else "No",
            }
        )

        for correction in log.get("attendance_corrections") or []:
            teacher = _relation(correction.get("teachers")) or {}
            correction_rows.append(
                {
                    "Student": student_name,
                    "Previous": (
                        "Present" if correction.get("previous_status") else "Absent"
                    ),
                    "New": "Present" if correction.get("new_status") else "Absent",
                    "Reason": correction.get("reason", ""),
                    "Corrected By": teacher.get("name", "Teacher"),
                    "Corrected At": correction.get("corrected_at", "N/A"),
                }
            )

    return pd.DataFrame(record_rows), pd.DataFrame(correction_rows)


@st.dialog("Lecture Attendance", width="large")
def attendance_session_dialog(session_id, teacher_id):
    try:
        session = get_attendance_session_details(session_id, teacher_id)
    except Exception:
        logger.exception("Could not load attendance session %s", session_id)
        st.error("This lecture session could not be loaded.")
        return

    if not session:
        st.error("This lecture session was not found or does not belong to you.")
        return

    subject = _relation(session.get("subjects")) or {}
    st.subheader(session.get("title") or "Attendance session")
    st.caption(
        f"{subject.get('name', 'Subject')} · {subject.get('subject_code', 'N/A')} · "
        f"{str(session.get('attendance_method') or 'N/A').title()} · "
        f"{session.get('started_at', 'N/A')}"
    )

    records_frame, corrections_frame = attendance_session_detail_frames(session)
    if records_frame.empty:
        st.info("This lecture does not contain attendance records.")
        return

    st.markdown("#### Student records")
    st.dataframe(records_frame, width="stretch", hide_index=True)
    st.download_button(
        "Download this lecture as CSV",
        data=records_frame.drop(columns=["Log ID"]).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"attendance_session_{session_id}.csv",
        mime="text/csv",
        width="stretch",
        key=f"download_attendance_session_{session_id}",
    )

    st.divider()
    st.markdown("#### Correct one student")
    # FEATURE 2: One-record-at-a-time correction avoids partial multi-row saves
    # and requires an explicit reason for every change.
    record_options = {
        f"{row['Student']} — ID {row['Student ID']}": row
        for row in records_frame.to_dict("records")
    }
    selected_label = st.selectbox(
        "Student record",
        options=list(record_options),
        key=f"correction_record_{session_id}",
    )
    selected_record = record_options[selected_label]
    current_status = selected_record["Final Status"]
    new_status = st.radio(
        "Final attendance status",
        options=["Present", "Absent"],
        index=0 if current_status == "Present" else 1,
        horizontal=True,
        key=f"correction_status_{session_id}_{selected_record['Log ID']}",
    )
    reason = st.text_input(
        "Correction reason",
        placeholder="Example: Student was present but recognition failed",
        key=f"correction_reason_{session_id}_{selected_record['Log ID']}",
    )
    has_change = new_status != current_status
    if st.button(
        "Save correction",
        type="primary",
        width="stretch",
        disabled=not has_change or not reason.strip(),
        key=f"save_correction_{session_id}_{selected_record['Log ID']}",
    ):
        try:
            result = correct_attendance_record(
                selected_record["Log ID"],
                teacher_id,
                new_status == "Present",
                reason,
            )
            if result.get("changed"):
                st.toast("Attendance correction saved with audit history.", icon="✅")
                st.rerun()
        except Exception:
            logger.exception(
                "Could not correct attendance log %s", selected_record["Log ID"]
            )
            st.error("The correction could not be saved. Check the database migration.")

    st.divider()
    st.markdown("#### Correction history")
    if corrections_frame.empty:
        st.caption("No manual corrections have been made for this lecture.")
    else:
        st.dataframe(corrections_frame, width="stretch", hide_index=True)
