import logging
from datetime import datetime, timezone
from html import escape

import numpy as np
import pandas as pd
import streamlit as st

from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_add_voiceattendence import voice_attendance_dialog
from src.components.dialog_attendence_result import show_attendance_result
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_attendance_session import (
    attendance_session_dialog,
    attendance_session_summary,
)
from src.components.footer import footer_dashboard
from src.components.header import header_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    get_subject_students,
    get_teacher_attendance_sessions,
    get_teacher_subjects,
    teacher_login,
)
from src.pipelines.facePipeline import analyze_face_image
from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
    style_teacher_auth,
)
from src.auth.session_manager import (
    logout_teacher,
    start_current_teacher_session,
    start_teacher_session,
)
from src.ui.product_theme import attendance_workflow, page_header, style_product_ui

logger = logging.getLogger(__name__)


def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    # UI REDESIGN: One institutional theme is shared by every teacher screen.
    style_product_ui()
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
    safe_teacher_name = escape(str(teacher_data.get("name") or "Teacher"))
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    valid_tabs = {"take_attendance", "manage_subjects", "attendance_records"}
    if st.session_state.current_teacher_tab not in valid_tabs:
        st.session_state.current_teacher_tab = "take_attendance"

    # UI REDESIGN: A stable faculty navigation replaces the three large top tabs.
    nav_column, workspace_column = st.columns([1.05, 4.35], gap="large")
    with nav_column:
        with st.container(border=True, key="teacher_navigation_shell"):
            st.html(
                """
                <div class="iq-nav-brand">
                    <div class="iq-nav-mark">A</div>
                    <div><strong>AttendIQ</strong><span>Faculty workspace</span></div>
                </div>
                """
            )
            navigation = (
                ("take_attendance", "Take attendance", ":material/how_to_reg:"),
                ("manage_subjects", "Subjects", ":material/menu_book:"),
                ("attendance_records", "Records", ":material/table_view:"),
            )
            for tab_key, label, icon in navigation:
                if st.button(
                    label,
                    icon=icon,
                    width="stretch",
                    type=(
                        "primary"
                        if st.session_state.current_teacher_tab == tab_key
                        else "tertiary"
                    ),
                    key=f"teacher_nav_{tab_key}",
                ):
                    st.session_state.current_teacher_tab = tab_key
                    st.rerun()

            st.html(
                f"""
                <div class="iq-user-card">
                    <span>Signed in as</span>
                    <strong>{safe_teacher_name}</strong>
                </div>
                """
            )
            if st.button(
                "Sign out",
                icon=":material/logout:",
                key="teacherLogoutButton",
                width="stretch",
            ):
                # SESSION MANAGEMENT: Revoke the database token as well as clearing
                # Streamlit state, so the same cookie cannot be reused after logout.
                logout_teacher()
                st.rerun()

    with workspace_column:
        session_warning = st.session_state.pop("teacher_session_warning", None)
        if session_warning:
            st.warning(session_warning, icon=":material/warning:")
        if st.session_state.current_teacher_tab == "take_attendance":
            teacher_tab_take_attendance()
        elif st.session_state.current_teacher_tab == "manage_subjects":
            teacher_tab_manage_subjects()
        elif st.session_state.current_teacher_tab == "attendance_records":
            teacher_tab_attendance_records()
        footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    page_header(
        "Attendance workspace",
        "Take attendance",
        "Select a class, add evidence, review the AI result, and save.",
    )

    st.session_state.setdefault("attendance_images", [])
    st.session_state.setdefault("attendance_image_hashes", set())
    pending_result = st.session_state.get("pending_face_attendance")
    saved_result = st.session_state.get("attendance_save_success")
    active_step = 4 if saved_result else 3 if pending_result else (
        2 if st.session_state.attendance_images else 1
    )
    attendance_workflow(active_step)

    if saved_result:
        safe_saved_title = escape(
            str(saved_result.get("title") or "Lecture attendance")
        )
        st.html(
            f"""
            <div class="iq-success-panel">
                <strong>Attendance saved successfully</strong>
                <span>{safe_saved_title} is now available in Attendance Records.</span>
            </div>
            """
        )
        if st.button(
            "Take another attendance",
            type="primary",
            icon=":material/add_task:",
            key="start_another_attendance",
        ):
            st.session_state.pop("attendance_save_success", None)
            st.rerun()
        return

    if pending_result:
        st.subheader("Review AI results")
        st.caption(
            "Resolve uncertain matches and correct any result before saving the lecture."
        )
        show_attendance_result(
            pending_result["dataframe"],
            pending_result["logs"],
            source="face",
            clear_images=True,
            session_details=pending_result["session_details"],
        )
        return

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

    # FEATURE 2: The title belongs to the lecture session, not to every student log.
    session_title = st.text_input(
        "Lecture title",
        placeholder=f"{selected_subject['name']} lecture",
        key=f"attendance_session_title_{selected_subject_id}",
        help="Optional topic or label shown in Attendance Records.",
    )

    with photo_col:
        if st.button(
            "Add photos",
            type="primary",
            icon=":material/photo_library:",
            width="stretch",
            key="open_attendance_photos",
        ):
            add_photos_dialog()

    st.divider()

    attendance_images = st.session_state.attendance_images
    if attendance_images:
        st.subheader(f"Classroom evidence · {len(attendance_images)} photo(s)")
        gallery_columns = st.columns(4)
        for index, image in enumerate(attendance_images):
            with gallery_columns[index % 4]:
                st.image(image, width="stretch", caption=f"Photo {index + 1}")

    has_photos = bool(attendance_images)
    clear_col, voice_col, face_col = st.columns([1, 1.3, 1.6])

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
            "Analyze face attendance",
            width="stretch",
            type="primary",
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

                    # FEATURE 1: Merge confident and ambiguous detections across
                    # every usable photo. A confident match in any photo wins,
                    # while close candidates are sent to teacher review.
                    detected_sources = {}
                    detected_similarity = {}
                    review_sources = {}
                    review_similarity = {}
                    rejected_photos = []
                    unknown_face_count = 0
                    processable_photo_count = 0
                    detected_face_count = 0
                    for index, image in enumerate(attendance_images):
                        image_array = np.array(image.convert("RGB"))
                        analysis = analyze_face_image(
                            image_array,
                            candidate_students=enrolled_students,
                        )
                        source_label = f"Photo {index + 1}"
                        if not analysis["quality"]["accepted"]:
                            rejected_photos.append(
                                f"{source_label}: "
                                + " ".join(analysis["quality"]["reasons"])
                            )
                            continue

                        processable_photo_count += 1
                        detected_face_count += analysis["face_count"]
                        for match in analysis["matches"]:
                            if match.get("status") == "matched":
                                student_key = str(match["student_id"])
                                detected_sources.setdefault(student_key, []).append(
                                    source_label
                                )
                                detected_similarity[student_key] = max(
                                    detected_similarity.get(student_key, 0.0),
                                    float(match.get("similarity", 0.0)),
                                )
                            elif match.get("status") == "needs_review":
                                for candidate in match.get("candidates", []):
                                    student_key = str(candidate["student_id"])
                                    review_sources.setdefault(student_key, []).append(
                                        source_label
                                    )
                                    review_similarity[student_key] = max(
                                        review_similarity.get(student_key, 0.0),
                                        float(match.get("similarity", 0.0)),
                                    )
                            else:
                                unknown_face_count += 1

                    if processable_photo_count == 0:
                        st.error(
                            "All selected photos failed the quality check. "
                            "Replace blurred, dark, or low-resolution photos and try again."
                        )
                        for message in rejected_photos:
                            st.warning(message)
                        return
                    if detected_face_count == 0:
                        st.error(
                            "No faces were detected in the usable photos. "
                            "Add a clearer classroom photo before creating attendance."
                        )
                        return

                timestamp = datetime.now(timezone.utc).isoformat()
                results = []
                attendance_logs = []
                for student in enrolled_students:
                    student_id = student["student_id"]
                    student_key = str(student_id)
                    sources = detected_sources.get(student_key, [])
                    possible_sources = review_sources.get(student_key, [])
                    if sources:
                        status = "Present"
                        similarity = detected_similarity.get(student_key, 0.0)
                    elif possible_sources:
                        status = "Needs Review"
                        sources = possible_sources
                        similarity = review_similarity.get(student_key, 0.0)
                    else:
                        status = "Absent"
                        similarity = 0.0

                    is_present = status == "Present"
                    results.append(
                        {
                            "Name": student["name"],
                            "ID": student_id,
                            "Detected in": ", ".join(sources) if sources else "—",
                            "Similarity": f"{similarity:.0%}" if similarity else "—",
                            "Status": status,
                        }
                    )
                    attendance_logs.append(
                        {
                            "student_id": student_id,
                            "subject_id": selected_subject_id,
                            "timestamp": timestamp,
                            # FEATURE 2: Preserve AI decision separately from any
                            # teacher change made in the review dialog.
                            "ai_is_present": is_present,
                            "is_present": is_present,
                        }
                    )

                # FEATURE 1: Explain quality and unknown-face outcomes without
                # assigning them to an enrolled student.
                for message in rejected_photos:
                    st.warning(message)
                if unknown_face_count:
                    st.info(
                        f"{unknown_face_count} face(s) were not confidently matched "
                        "to an enrolled student."
                    )

                # UI REDESIGN: Review happens inline as step three instead of in
                # an oversized dialog detached from the attendance workflow.
                st.session_state["pending_face_attendance"] = {
                    "subject_id": selected_subject_id,
                    "dataframe": pd.DataFrame(results),
                    "logs": attendance_logs,
                    "session_details": {
                        "subject_id": selected_subject_id,
                        "teacher_id": teacher_id,
                        "title": session_title.strip()
                        or f"{selected_subject['name']} lecture",
                        "method": "face",
                        "started_at": timestamp,
                    },
                }
                st.rerun()
            except Exception:
                logger.exception("Face attendance analysis failed")
                st.error("Face analysis failed. Check the photos, models, and database.")

    with voice_col:
        if st.button(
            "Use Voice Attendance",
            type="secondary",
            width="stretch",
            icon=":material/mic:",
            key="voice_attendance_button",
        ):
            voice_attendance_dialog(
                selected_subject_id,
                teacher_id=teacher_id,
                session_title=session_title.strip()
                or f"{selected_subject['name']} lecture",
            )


def teacher_tab_manage_subjects():
    page_header(
        "Course administration",
        "Subjects",
        "Create classes, review enrollment, and share student join codes.",
    )

    teacher_id = st.session_state.teacher_data['teacher_id']

    _, action_col = st.columns([3, 1])
    with action_col:
        if st.button(
            "Create subject",
            type="primary",
            icon=":material/add:",
            width="stretch",
            key="create_subject_button",
        ):
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

    subject_columns = st.columns(2)
    for index, subject in enumerate(subjects):
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

        with subject_columns[index % 2]:
            subject_card(
                name=subject_name,
                code=subject_code,
                section=subject_section,
                stats=stats,
                footer_callback=share_btn,
            )


def teacher_tab_attendance_records():
    page_header(
        "Lecture history",
        "Attendance records",
        "Review saved lectures, download reports, and correct individual records.",
    )
    teacher_id = st.session_state.teacher_data["teacher_id"]

    try:
        # FEATURE 2: Load real lecture sessions instead of reconstructing them
        # from timestamp-equal student rows.
        sessions = get_teacher_attendance_sessions(teacher_id)
    except Exception:
        logger.exception("Could not load attendance sessions for teacher %s", teacher_id)
        st.error(
            "Attendance sessions could not be loaded. Run the Feature 2 database "
            "migration and check the connection."
        )
        return

    summary_frame = attendance_session_summary(sessions)
    if summary_frame.empty:
        st.info("No lecture sessions have been saved for your subjects yet.")
        return

    summary_frame["Time"] = pd.to_datetime(
        summary_frame["Time"], errors="coerce", utc=True
    ).dt.strftime("%Y-%m-%d %I:%M %p")
    display_frame = summary_frame[
        [
            "Time",
            "Lecture",
            "Subject",
            "Subject Code",
            "Method",
            "Attendance Stats",
            "Status",
        ]
    ]

    total_records = sum(len(session.get("attendance_logs") or []) for session in sessions)
    total_present = sum(
        bool(log.get("is_present"))
        for session in sessions
        for log in (session.get("attendance_logs") or [])
    )
    attendance_rate = total_present / total_records * 100 if total_records else 0.0
    metric_one, metric_two, metric_three = st.columns(3)
    metric_one.metric("Lecture sessions", len(display_frame))
    metric_two.metric("Student records", total_records)
    metric_three.metric("Average attendance", f"{attendance_rate:.0f}%")

    st.subheader("Saved lectures")
    st.dataframe(display_frame, width="stretch", hide_index=True)

    # FEATURE 2: Session IDs drive drill-down, so lectures with identical names
    # or timestamps still remain separate and individually correctable.
    session_options = {
        (
            f"#{row['Session ID']} · {row['Lecture']} · {row['Subject Code']} · "
            f"{row['Time'] or 'Unknown time'}"
        ): int(row["Session ID"])
        for row in summary_frame.to_dict("records")
    }
    selection_col, action_col = st.columns([4, 1], vertical_alignment="bottom")
    with selection_col:
        selected_session_label = st.selectbox(
            "Select a lecture",
            options=list(session_options),
            key="selected_teacher_attendance_session",
        )
    with action_col:
        if st.button(
            "Open session",
            type="primary",
            width="stretch",
            key="open_teacher_attendance_session",
        ):
            attendance_session_dialog(
                session_options[selected_session_label],
                teacher_id,
            )

    st.download_button(
        "Download attendance sessions as CSV",
        data=display_frame.to_csv(index=False).encode("utf-8-sig"),
        file_name="attendance_sessions.csv",
        mime="text/csv",
        width="content",
        key="download_teacher_attendance_sessions",
    )



# LOGIN


def teacher_login_db(username, password):
    if not username or not password:
        return False, "Please enter both username and password."

    try:
        teacher = teacher_login(username.strip(), password)
    except Exception:
        logger.exception("Teacher login database request failed")
        return False, "Unable to reach the teacher database. Please try again."
    if teacher:
        try:
            # SESSION MANAGEMENT: Password login now creates the persistent,
            # hashed session and writes its raw token to a browser cookie.
            start_teacher_session(teacher)
        except Exception:
            logger.exception("Teacher persistent session creation failed")
            # SESSION MANAGEMENT: A cookie/dependency problem must never reject
            # credentials that the teacher database already validated.
            start_current_teacher_session(teacher)
            st.session_state["teacher_session_warning"] = (
                "You are signed in for this browser tab, but persistent login is "
                "temporarily unavailable. Install the dependencies and restart "
                "the app to stay signed in after a refresh."
            )
            return True, f"Welcome back, {teacher['name']}!"
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
