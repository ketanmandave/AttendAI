import logging
import re

import pandas as pd
import streamlit as st

from src.database.db import create_attendance


logger = logging.getLogger(__name__)


def _attendance_csv(dataframe):
    """Create an Excel-friendly CSV download from the visible result table."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def _attendance_filename(source, attendance_logs):
    timestamp = attendance_logs[0].get("timestamp", "") if attendance_logs else ""
    safe_timestamp = re.sub(r"[^0-9A-Za-z_-]+", "-", str(timestamp)).strip("-")
    suffix = safe_timestamp or "session"
    return f"{source}_attendance_{suffix}.csv"


def _clear_attendance_state(clear_images=False):
    st.session_state.pop("voice_attendance_results", None)
    if clear_images:
        st.session_state.setdefault("attendance_images", []).clear()
        st.session_state.setdefault("attendance_image_hashes", set()).clear()


def show_attendance_result(
    dataframe,
    attendance_logs,
    *,
    source="attendance",
    clear_images=False,
):
    st.caption("Review every student before saving this attendance session.")

    if dataframe is None or dataframe.empty:
        st.warning("No attendance results were generated.")
        return

    st.dataframe(dataframe, hide_index=True, width="stretch")

    present_count = sum(bool(log.get("is_present")) for log in attendance_logs)
    total_count = len(attendance_logs)
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Students", total_count)
    metric_col2.metric("Present", present_count)
    metric_col3.metric("Absent", total_count - present_count)

    st.download_button(
        "Download result as CSV",
        data=_attendance_csv(dataframe),
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
            key=f"confirm_{source}_attendance",
        ):
            try:
                created = create_attendance(attendance_logs)
                if not created:
                    st.error("Attendance could not be saved. Please try again.")
                    return

                _clear_attendance_state(clear_images=clear_images)
                st.toast("Attendance saved successfully!", icon="✅")
                st.rerun()
            except Exception:
                logger.exception("Could not save %s attendance", source)
                st.error("Attendance sync failed. Check the database connection.")


@st.dialog("Attendance Results", width="medium")
def attendance_result_dialog(dataframe, attendance_logs):
    if not isinstance(dataframe, pd.DataFrame):
        dataframe = pd.DataFrame(dataframe)
    show_attendance_result(
        dataframe,
        attendance_logs,
        source="face",
        clear_images=True,
    )
