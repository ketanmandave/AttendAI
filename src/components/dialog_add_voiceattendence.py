import logging
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from src.components.dialog_attendence_result import show_attendance_result
from src.database.db import get_subject_students
from src.pipelines.voicePipeline import process_bulk_audio


logger = logging.getLogger(__name__)


def _voice_audio_input():
    source = st.radio(
        "Audio source",
        ["Record classroom audio", "Upload an audio file"],
        horizontal=True,
        key="voice_attendance_audio_source",
        label_visibility="collapsed",
    )
    if source == "Record classroom audio":
        return st.audio_input(
            "Record students saying they are present",
            sample_rate=16000,
            key="voice_attendance_recording",
        )
    return st.file_uploader(
        "Upload classroom audio",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        key="voice_attendance_upload",
    )


def _student_from_enrollment(enrollment):
    student = enrollment.get("students")
    if isinstance(student, list):
        student = student[0] if student else None
    return student


@st.dialog("Voice Attendance", width="medium")
def voice_attendance_dialog(selected_subject_id):
    st.caption(
        "Ask students to speak one at a time. AttendIQ will compare each voice segment "
        "with enrolled voice profiles."
    )

    saved_result = st.session_state.get("voice_attendance_results")
    if saved_result and saved_result.get("subject_id") != selected_subject_id:
        st.session_state.pop("voice_attendance_results", None)
        saved_result = None

    audio_data = _voice_audio_input()

    if st.button(
        "Analyze voice attendance",
        width="stretch",
        type="primary",
        disabled=audio_data is None,
        key="analyze_voice_attendance",
    ):
        try:
            with st.spinner("Processing classroom audio…"):
                enrollments = get_subject_students(selected_subject_id)
                enrolled_students = [
                    student
                    for student in (_student_from_enrollment(row) for row in enrollments)
                    if student
                ]

                if not enrolled_students:
                    st.warning("No students are enrolled in this subject.")
                    return

                voice_candidates = {
                    int(student["student_id"]): student["voice_embedding"]
                    for student in enrolled_students
                    if student.get("voice_embedding")
                }
                if not voice_candidates:
                    st.error("No enrolled students have registered a voice profile.")
                    return

                detected_scores = process_bulk_audio(
                    audio_data.getvalue(),
                    voice_candidates,
                )

            timestamp = datetime.now(timezone.utc).isoformat()
            results = []
            attendance_logs = []
            for student in enrolled_students:
                student_id = int(student["student_id"])
                score = float(detected_scores.get(student_id, 0.0))
                is_present = student_id in detected_scores

                results.append(
                    {
                        "Name": student["name"],
                        "ID": student_id,
                        "Voice match": f"{score:.0%}" if is_present else "—",
                        "Status": "✅ Present" if is_present else "❌ Absent",
                    }
                )
                attendance_logs.append(
                    {
                        "student_id": student_id,
                        "subject_id": selected_subject_id,
                        "timestamp": timestamp,
                        "is_present": is_present,
                    }
                )

            saved_result = {
                "subject_id": selected_subject_id,
                "dataframe": pd.DataFrame(results),
                "logs": attendance_logs,
            }
            st.session_state["voice_attendance_results"] = saved_result
        except Exception:
            logger.exception("Voice attendance analysis failed")
            st.error("Voice analysis failed. Try a clearer recording or check the database.")
            return

    if saved_result:
        st.divider()
        show_attendance_result(
            saved_result["dataframe"],
            saved_result["logs"],
            source="voice",
            clear_images=False,
        )

