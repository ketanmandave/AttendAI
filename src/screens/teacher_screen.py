import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import streamlit as st

from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_add_voiceattendence import voice_attendance_dialog
from src.components.dialog_attendence_result import attendance_result_dialog
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.footer import footer_dashboard
from src.components.header import header_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    get_subject_students,
    get_teacher_subjects,
    teacher_login,
    get_attendance_records_for_teacher,
)
from src.pipelines.facePipeline import predict_attendance
from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
    style_teacher_auth,
)

logger = logging.getLogger(__name__)


def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    if st.session_state.get("teacher_data"):
        teacher_dashboard()
    elif(
        "teacher_login_type" not in st.session_state
        or st.session_state.teacher_login_type == "login"
    ):
        style_teacher_auth()
        teacher_screen_login()

    elif st.session_state.teacher_login_type == "register":
        style_teacher_auth()
        teacher_screen_register()

    else:
        st.session_state["teacher_login_type"] = "login"
        st.rerun()



def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")

    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {teacher_data['name']}!")
        if st.button("Logout", key="teacherLogoutButton", width="stretch"):
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
            ):
                st.session_state.pop(key, None)
            st.session_state.teacher_login_type = "login"
            st.rerun()

    st.space(2)


    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    valid_tabs = {"take_attendance", "manage_subjects", "attendance_records"}
    if st.session_state.current_teacher_tab not in valid_tabs:
        st.session_state.current_teacher_tab = "take_attendance"

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        if st.button(
            'Take Attendance',
            width='stretch',
            type="primary" if st.session_state.current_teacher_tab == "take_attendance" else "secondary",
            key="teacher_take_attendance_tab",
        ):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        if st.button(
            'Manage Subjects',
            width='stretch',
            type="primary" if st.session_state.current_teacher_tab == "manage_subjects" else "secondary",
            key="teacher_manage_subjects_tab",
        ):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        if st.button(
            'Attendance Records',
            width='stretch',
            type="primary" if st.session_state.current_teacher_tab == "attendance_records" else "secondary",
            key="teacher_attendance_records_tab",
        ):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take AI Attendance")

    st.session_state.setdefault("attendance_images", [])
    st.session_state.setdefault("attendance_image_hashes", set())

    try:
        subjects = get_teacher_subjects(teacher_id)
    except Exception:
        logger.exception("Could not load subjects for teacher %s", teacher_id)
        st.error("Subjects could not be loaded. Check the database connection and schema.")
        return

    if not subjects:
        st.warning("You have not created any subjects yet. Create one before taking attendance.")
        return

    subject_options = {
        f"{subject['name']} — {subject['subject_code']}": subject
        for subject in subjects
    }
    subject_col, photo_col = st.columns([3, 1], vertical_alignment="bottom")
    with subject_col:
        selected_label = st.selectbox(
            "Select subject",
            options=list(subject_options),
            key="selected_attendance_subject",
        )

    selected_subject = subject_options[selected_label]
    selected_subject_id = selected_subject["subject_id"]
    previous_subject_id = st.session_state.get("selected_attendance_subject_id")
    if previous_subject_id is not None and previous_subject_id != selected_subject_id:
        st.session_state["attendance_images"] = []
        st.session_state["attendance_image_hashes"] = set()
        st.session_state.pop("voice_attendance_results", None)
    st.session_state["selected_attendance_subject_id"] = selected_subject_id

    with photo_col:
        if st.button(
            "Add Photos",
            type="primary",
            icon=":material/photo_library:",
            width="stretch",
            key="open_attendance_photos",
        ):
            add_photos_dialog()

    st.divider()

    attendance_images = st.session_state.attendance_images
    if attendance_images:
        st.subheader("Added Photos")
        gallery_columns = st.columns(4)
        for index, image in enumerate(attendance_images):
            with gallery_columns[index % 4]:
                st.image(image, width="stretch", caption=f"Photo {index + 1}")

    has_photos = bool(attendance_images)
    clear_col, face_col, voice_col = st.columns(3)

    with clear_col:
        if st.button(
            "Clear all photos",
            width="stretch",
            type="tertiary",
            icon=":material/delete:",
            disabled=not has_photos,
            key="clear_teacher_attendance_photos",
        ):
            st.session_state["attendance_images"] = []
            st.session_state["attendance_image_hashes"] = set()
            st.rerun()

    with face_col:
        if st.button(
            "Run Face Analysis",
            width="stretch",
            type="secondary",
            icon=":material/analytics:",
            disabled=not has_photos,
            key="run_face_attendance",
        ):
            try:
                with st.spinner("Deep scanning classroom photos…"):
                    enrollment_rows = get_subject_students(selected_subject_id)
                    enrolled_students = []
                    for enrollment in enrollment_rows:
                        student = enrollment.get("students")
                        if isinstance(student, list):
                            student = student[0] if student else None
                        if student:
                            enrolled_students.append(student)

                    if not enrolled_students:
                        st.warning("No students are enrolled in this subject.")
                        return

                    detected_sources = {}
                    for index, image in enumerate(attendance_images):
                        image_array = np.array(image.convert("RGB"))
                        detected, _, _ = predict_attendance(image_array)
                        for detected_id in detected:
                            student_key = str(detected_id)
                            detected_sources.setdefault(student_key, []).append(
                                f"Photo {index + 1}"
                            )

                timestamp = datetime.now(timezone.utc).isoformat()
                results = []
                attendance_logs = []
                for student in enrolled_students:
                    student_id = student["student_id"]
                    sources = detected_sources.get(str(student_id), [])
                    is_present = bool(sources)
                    results.append(
                        {
                            "Name": student["name"],
                            "ID": student_id,
                            "Detected in": ", ".join(sources) if sources else "—",
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

                attendance_result_dialog(pd.DataFrame(results), attendance_logs)
            except Exception:
                logger.exception("Face attendance analysis failed")
                st.error("Face analysis failed. Check the photos, models, and database.")

    with voice_col:
        if st.button(
            "Use Voice Attendance",
            type="primary",
            width="stretch",
            icon=":material/mic:",
            key="voice_attendance_button",
        ):
            voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subjects():
    st.subheader("Manage Subjects")
    st.write("This is where you can manage your subjects.")

    teacher_id = st.session_state.teacher_data['teacher_id']

    col1, col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects")

    with col2:
        if st.button('Create New Subject', width='content', key='create_subject_button'):
            create_subject_dialog(teacher_id)

    # List all subjects belonging to the logged-in teacher.
    try:
        subjects = get_teacher_subjects(teacher_id)
    except Exception:
        logger.exception("Could not load subjects for teacher %s", teacher_id)
        st.error("Subjects could not be loaded. Check the database connection and schema.")
        return
    if not subjects:
        st.info("No subjects yet. Create your first subject to get started.")
        return

    for subject in subjects:
        subject_name = subject.get("name", "Unnamed subject")
        subject_code = subject.get("subject_code", "N/A")
        subject_section = subject.get("section", "N/A")
        stats = [
            ("👥", "Students", subject.get("total_students", 0)),
            ("📅", "Classes", subject.get("total_classes", 0)),
        ]

        def share_btn(
            name=subject_name,
            code=subject_code,
            subject_key=subject.get("subject_id", subject_code),
        ):
            if st.button(
                f"Share class: {code}",
                key=f"share_subject_{subject_key}",
            ):
                share_subject_dialog(name, code)

        subject_card(
            name=subject_name,
            code=subject_code,
            section=subject_section,
            stats=stats,
            footer_callback=share_btn,
        )


def teacher_tab_attendance_records():
    st.header("Attendance Records")
    teacher_id = st.session_state.teacher_data["teacher_id"]

    try:
        records = get_attendance_records_for_teacher(teacher_id)
    except Exception:
        logger.exception("Could not load attendance records for teacher %s", teacher_id)
        st.error("Attendance records could not be loaded. Check the database connection and schema.")
        return

    data = []

    for record in records:
        subject = record.get("subjects")
        if isinstance(subject, list):
            subject = subject[0] if subject else None
        timestamp = record.get("timestamp")
        if not subject or not timestamp:
            continue

        data.append({
            "Session Timestamp": timestamp,
            "Subject": subject.get("name", "N/A"),
            "Subject Code": subject.get("subject_code", "N/A"),
            "Is Present": bool(record.get("is_present", False)),
        })

    if not data:
        st.info("No attendance records have been saved for your subjects yet.")
        return

    records_frame = pd.DataFrame(data)
    records_frame["Session Timestamp"] = pd.to_datetime(
        records_frame["Session Timestamp"], errors="coerce", utc=True
    )
    records_frame = records_frame.dropna(subset=["Session Timestamp"])

    if records_frame.empty:
        st.info("No attendance records with a valid session time were found.")
        return

    # Every face/voice attendance run writes one shared timestamp for all
    # students. Grouping by the exact timestamp keeps separate lectures of the
    # same subject separate while combining their individual student records.
    summary = (
        records_frame.groupby(
            ["Session Timestamp", "Subject", "Subject Code"],
            as_index=False,
        )
        .agg(
            Present_Count=("Is Present", "sum"),
            Total_Count=("Is Present", "count"),
        )
        .sort_values("Session Timestamp", ascending=False)
    )
    summary["Time"] = summary["Session Timestamp"].dt.strftime(
        "%Y-%m-%d %I:%M %p"
    )
    summary["Attendance Stats"] = (
        "✅ "
        + summary["Present_Count"].astype(str)
        + " / "
        + summary["Total_Count"].astype(str)
        + " Students"
    )
    display_frame = summary[
        ["Time", "Subject", "Subject Code", "Attendance Stats"]
    ]

    st.caption(f"{len(display_frame)} attendance session(s)")
    st.dataframe(display_frame, width="stretch", hide_index=True)
    st.download_button(
        "Download attendance sessions as CSV",
        data=display_frame.to_csv(index=False).encode("utf-8-sig"),
        file_name="attendance_sessions.csv",
        mime="text/csv",
        width="content",
        key="download_teacher_attendance_sessions",
    )


# =========================================================
# LOGIN
# =========================================================


def teacher_login_db(username, password):
    if not username or not password:
        return False, "Please enter both username and password."

    try:
        teacher = teacher_login(username.strip(), password)
    except Exception:
        logger.exception("Teacher login database request failed")
        return False, "Unable to reach the teacher database. Please try again."
    if teacher:
        st.session_state.is_logged_in = True
        st.session_state.teacher_data= teacher
        st.session_state.user_role = 'teacher'
        return True, f"Welcome back, {teacher['name']}!"
    else:
        return False, "Invalid username or password."


def teacher_screen_login():

    # Header row
    col1, col2 = st.columns([5, 1])

    with col1:
        header_dashboard()

    with col2:
        st.write("")

        if st.button("← Home", key="loginBackButton", width="stretch"):
            st.session_state.teacher_login_type = "login"
            st.session_state["login_type"] = None
            st.rerun()

    # Page intro
    st.html("""
        <div class="teacher-auth-heading">

            <div class="teacher-auth-icon">
                👨‍🏫
            </div>

            <div>
                <p class="teacher-auth-label">
                    TEACHER ACCESS
                </p>

                <h2>
                    Welcome back
                </h2>

                <p>
                    Sign in to manage attendance and student records.
                </p>
            </div>

        </div>
        """)

    # Form container
    with st.container(border=True):

        st.markdown("#### Login Details")

        username = st.text_input(
            "Username", placeholder="Enter your username", key="teacherUsername"
        )

        password = st.text_input(
            "Password",
            placeholder="Enter your password",
            type="password",
            key="teacherPassword",
        )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:

            if st.button("Login", type="primary", key="loginButton", width="stretch"):
                success, message = teacher_login_db(username, password)
                if success:
                    st.toast(message, icon="✅")
                    st.rerun()
                else:
                    st.error(message)

        with col2:

            if st.button("Create Account", key="registerButton", width="stretch"):
                st.session_state.teacher_login_type = "register"
                st.rerun()

    # Small info section
    st.html("""
        <div class="teacher-auth-info">

            <div>
                <span>🔐</span>

                <div>
                    <strong>Secure Access</strong>
                    <p>
                        Teacher credentials protect attendance controls.
                    </p>
                </div>
            </div>

            <div>
                <span>📊</span>

                <div>
                    <strong>Attendance Management</strong>
                    <p>
                        View and manage student attendance records.
                    </p>
                </div>
            </div>

        </div>
        """)

    footer_dashboard()


# =========================================================
# REGISTER
# =========================================================


def register_teacher(name, username, password, confirm):
    if not name or not username or not password or not confirm:
        return False, "All fields are required."

    if password != confirm:
        return False, "Passwords do not match."

    name = name.strip()
    username = username.strip()

    try:
        if check_teacher_exists(username):
            return False, "Username already exists."
        teacher = create_teacher(username, password, name)
    except Exception:
        logger.exception("Teacher registration database request failed")
        return False, "Unable to reach the teacher database. Please try again."
    if teacher:
        return True, "Teacher account created successfully."
    else:
        return False, "Failed to create teacher account."


def teacher_screen_register():

    # Header row
    col1, col2 = st.columns([5, 1])

    with col1:
        header_dashboard()

    with col2:
        st.write("")

        if st.button("← Home", key="registerHomeButton", width="stretch"):
            st.session_state.teacher_login_type = "login"
            st.session_state["login_type"] = None
            st.rerun()

    # Page heading
    st.html("""
        <div class="teacher-auth-heading">

            <div class="teacher-auth-icon">
                ✨
            </div>

            <div>
                <p class="teacher-auth-label">
                    NEW TEACHER
                </p>

                <h2>
                    Create your account
                </h2>

                <p>
                    Register as a teacher to access AttendIQ.
                </p>
            </div>

        </div>
        """)

    # Form container
    with st.container(border=True):

        st.markdown("#### Teacher Information")

        name = st.text_input(
            "Full Name", placeholder="Enter your full name", key="teacherName"
        )

        username = st.text_input(
            "Username", placeholder="Choose a username", key="teacherRegisterUsername"
        )

        col1, col2 = st.columns(2)

        with col1:

            password = st.text_input(
                "Password",
                placeholder="Create a password",
                type="password",
                key="teacherRegisterPassword",
            )

        with col2:

            confirm = st.text_input(
                "Confirm Password",
                placeholder="Re-enter password",
                type="password",
                key="teacherConfirmPassword",
            )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Create Teacher Account",
                type="primary",
                key="teacherCreateButton",
                width="stretch",
            ):
                success, message = register_teacher(name, username, password, confirm)
                if success:
                    st.session_state.teacher_login_type = "login"
                    st.toast(message, icon="✅")
                    st.rerun()
                else:
                    st.error(message)

        with col2:

            if st.button("Back to Login", key="backLoginButton", width="stretch"):
                st.session_state.teacher_login_type = "login"
                st.rerun()

    footer_dashboard()
