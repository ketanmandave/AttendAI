import logging
import re

import pandas as pd
import streamlit as st

from src.database.db import create_attendance, create_attendance_session_with_logs


logger = logging.getLogger(__name__)


def _attendance_csv(dataframe):
    """Create an Excel-friendly CSV download from the visible result table."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def _attendance_filename(source, attendance_logs):
    timestamp = attendance_logs[0].get("timestamp", "") if attendance_logs else ""
    safe_timestamp = re.sub(r"[^0-9A-Za-z_-]+", "-", str(timestamp)).strip("-")
    suffix = safe_timestamp or "session"
    return f"{source}_attendance_{suffix}.csv"


# FEATURE 1: Keep teacher decisions and database payloads synchronized in one
# testable helper before saving the attendance session.
def _apply_reviewed_statuses(reviewed_dataframe, attendance_logs):
    logs_by_student = {
        str(log.get("student_id")): log for log in attendance_logs
    }
    for _, row in reviewed_dataframe.iterrows():
        log = logs_by_student.get(str(row.get("ID")))
        if log is not None:
            log["is_present"] = row.get("Status") == "Present"
    return int((reviewed_dataframe["Status"] == "Needs Review").sum())


def _clear_attendance_state(clear_images=False):
    st.session_state.pop("voice_attendance_results", None)
    # UI REDESIGN: Face review is now rendered inline in the teacher workflow.
    st.session_state.pop("pending_face_attendance", None)
    if clear_images:
        st.session_state.setdefault("attendance_images", []).clear()
        st.session_state.setdefault("attendance_image_hashes", set()).clear()


def show_attendance_result(
    dataframe,
    attendance_logs,
    *,
    source="attendance",
    clear_images=False,
    session_details=None,
):
    st.caption("Review every student before saving this attendance session.")

    if dataframe is None or dataframe.empty:
        st.warning("No attendance results were generated.")
        return

    reviewed_dataframe = dataframe.copy()
    unresolved_count = 0

    if source == "face" and "Status" in reviewed_dataframe.columns:
        # FEATURE 1: Teachers can resolve ambiguous matches and correct any AI
        # decision before it becomes a permanent attendance record.
        st.info(
            "Review the Status column. Every 'Needs Review' row must be changed "
            "to Present or Absent before saving."
        )
        timestamp = attendance_logs[0].get("timestamp", "session") if attendance_logs else "session"
        editor_suffix = re.sub(r"[^0-9A-Za-z_-]+", "-", str(timestamp)).strip("-")
        reviewed_dataframe = st.data_editor(
            reviewed_dataframe,
            hide_index=True,
            width="stretch",
            disabled=[column for column in reviewed_dataframe.columns if column != "Status"],
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Present", "Absent", "Needs Review"],
                    required=True,
                    help="Confirm or correct the final attendance decision.",
                )
            },
            key=f"review_{source}_attendance_{editor_suffix}",
        )

        unresolved_count = _apply_reviewed_statuses(
            reviewed_dataframe,
            attendance_logs,
        )
    else:
        st.dataframe(reviewed_dataframe, hide_index=True, width="stretch")

    present_count = sum(bool(log.get("is_present")) for log in attendance_logs)
    total_count = len(attendance_logs)
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Students", total_count)
    metric_col2.metric("Present", present_count)
    metric_col3.metric("Absent", total_count - present_count)

    st.download_button(
        "Download result as CSV",
        # FEATURE 1: Download the teacher-reviewed result, not the original AI output.
        data=_attendance_csv(reviewed_dataframe),
        file_name=_attendance_filename(source, attendance_logs),
        mime="text/csv",
        width="stretch",
        key=f"download_{source}_attendance_result",
    )

    discard_col, confirm_col = st.columns(2)
    with discard_col:
        if st.button(
            "Discard",
            width="stretch",
            key=f"discard_{source}_attendance",
        ):
            _clear_attendance_state(clear_images=clear_images)
            st.rerun()

    with confirm_col:
        if st.button(
            "Confirm & Save",
            width="stretch",
            type="primary",
            disabled=unresolved_count > 0,
            key=f"confirm_{source}_attendance",
        ):
            try:
                # FEATURE 2: Save one real lecture session first, then attach all
                # reviewed student records to its generated session ID.
                if session_details:
                    created = create_attendance_session_with_logs(
                        subject_id=session_details["subject_id"],
                        teacher_id=session_details["teacher_id"],
                        title=session_details.get("title"),
                        attendance_method=session_details.get("method", source),
                        attendance_logs=attendance_logs,
                        started_at=session_details.get("started_at"),
                    )
                else:
                    created = create_attendance(attendance_logs)
                if not created:
                    st.error("Attendance could not be saved. Please try again.")
                    return

                # UI REDESIGN: Keep a compact completion state so the teacher
                # receives an unambiguous final confirmation after the rerun.
                st.session_state["attendance_save_success"] = {
                    "title": (
                        session_details.get("title", "Attendance session")
                        if session_details
                        else "Attendance session"
                    ),
                    "present": present_count,
                    "total": total_count,
                }
                _clear_attendance_state(clear_images=clear_images)
                st.toast("Attendance saved successfully!", icon="✅")
                st.rerun()
            except Exception:
                logger.exception("Could not save %s attendance", source)
                st.error("Attendance sync failed. Check the database connection.")

    if unresolved_count:
        st.warning(
            f"Resolve {unresolved_count} uncertain student result(s) before saving."
        )


@st.dialog("Attendance Results", width="medium")
def attendance_result_dialog(dataframe, attendance_logs, session_details=None):
    if not isinstance(dataframe, pd.DataFrame):
        dataframe = pd.DataFrame(dataframe)
    show_attendance_result(
        dataframe,
        attendance_logs,
        source="face",
        clear_images=True,
        session_details=session_details,
    )
