import logging
import hashlib
from html import escape

import numpy as np
import streamlit as st
from PIL import Image

from src.components.dialog_enroll import enroll_dialog
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    create_student,
    get_all_students,
    get_student_attendance,
    get_student_subjects,
    unenroll_student_from_subject,
)
from src.pipelines.facePipeline import (
    analyze_face_image,
    assess_image_quality,
    get_face_embeddings,
    train_classifier,
)
from src.pipelines.voicePipeline import get_voice_embedding, identify_speaker
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.ui.product_theme import style_product_ui


logger = logging.getLogger(__name__)


def _style_student_portal():
    st.html(
        """
        <style>
        .block-container { max-width: 1040px; padding-top: 1.25rem; }
        .student-brand { display:flex; align-items:center; gap:12px; padding:6px 0 22px; }
        .student-brand-mark { width:42px; height:42px; display:grid; place-items:center; border-radius:13px; color:white; font-size:20px; background:linear-gradient(135deg,#2563eb,#7c3aed); box-shadow:0 10px 24px rgba(37,99,235,.24); }
        .student-brand strong { display:block; color:#0f172a; font-size:18px; letter-spacing:-.4px; }
        .student-brand span { display:block; color:#64748b; font-size:11px; margin-top:1px; }
        .student-hero { position:relative; overflow:hidden; padding:34px 38px; margin-bottom:24px; border-radius:26px; color:white; background:radial-gradient(circle at 92% 20%,rgba(103,232,249,.25),transparent 30%),linear-gradient(125deg,#172554 0%,#1d4ed8 52%,#6d28d9 100%); box-shadow:0 24px 55px rgba(30,64,175,.22); }
        .student-hero::after { content:''; position:absolute; width:190px; height:190px; right:-45px; bottom:-90px; border:28px solid rgba(255,255,255,.08); border-radius:50%; }
        .student-eyebrow { display:inline-flex; align-items:center; gap:7px; padding:5px 10px; margin-bottom:14px; border:1px solid rgba(255,255,255,.18); border-radius:999px; color:#dbeafe; background:rgba(255,255,255,.09); font-size:10px; font-weight:700; letter-spacing:1.4px; }
        .student-hero h1 { max-width:650px; margin:0 0 9px!important; color:white!important; font-size:32px!important; line-height:1.15!important; letter-spacing:-.8px!important; }
        .student-hero p { max-width:610px; margin:0!important; color:#dbeafe!important; font-size:13px!important; line-height:1.65; }
        .section-kicker { color:#2563eb; font-size:10px; font-weight:800; letter-spacing:1.5px; margin-bottom:5px; }
        .section-title { color:#0f172a; font-size:21px; font-weight:800; letter-spacing:-.4px; margin-bottom:4px; }
        .section-copy { color:#64748b; font-size:12px; line-height:1.55; margin-bottom:18px; }
        .privacy-note { display:flex; gap:10px; align-items:flex-start; margin-top:16px; padding:13px 15px; border:1px solid #dbeafe; border-radius:13px; color:#475569; background:#eff6ff; font-size:11px; line-height:1.5; }
        .profile-banner { padding:30px 34px; margin-bottom:22px; border:1px solid rgba(37,99,235,.12); border-radius:24px; background:linear-gradient(135deg,rgba(255,255,255,.98),rgba(239,246,255,.94)); box-shadow:0 18px 45px rgba(15,23,42,.07); }
        .profile-avatar { width:58px; height:58px; display:grid; place-items:center; margin-bottom:17px; border-radius:18px; color:white; font-size:24px; background:linear-gradient(135deg,#2563eb,#7c3aed); }
        .profile-banner h1 { margin:0 0 6px!important; color:#0f172a!important; font-size:29px!important; }
        .profile-banner p { margin:0!important; color:#64748b!important; font-size:13px!important; }
        .status-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:13px; margin:20px 0 26px; }
        .status-card { padding:17px; border:1px solid #e2e8f0; border-radius:16px; background:rgba(255,255,255,.9); }
        .status-card span { color:#64748b; font-size:10px; font-weight:700; letter-spacing:.7px; text-transform:uppercase; }
        .status-card strong { display:block; margin-top:6px; color:#0f172a; font-size:14px; }
        div[data-testid="stVerticalBlockBorderWrapper"] > div { padding:25px 26px 23px!important; }
        div[data-baseweb="tab-list"] { gap:8px; padding:5px; border-radius:13px; background:#eef2ff; }
        button[data-baseweb="tab"] { flex:1; justify-content:center; height:41px; border-radius:9px; color:#475569; font-weight:700; }
        button[data-baseweb="tab"][aria-selected="true"] { color:#1d4ed8; background:white; box-shadow:0 4px 13px rgba(15,23,42,.08); }
        div[data-testid="stCameraInput"] { border-radius:16px; overflow:hidden; }
        div[data-testid="stFileUploaderDropzone"] { border-color:#cbd5e1; border-radius:14px; background:#f8fafc; }
        .student-brand-mark { background:#17201f; box-shadow:none; }
        .student-hero { padding:28px 30px; border-radius:15px; background:linear-gradient(125deg,#17201f 0%,#263330 68%,#0f766e 125%); box-shadow:0 5px 18px rgba(23,32,31,.10); }
        .student-hero::after { display:none; }
        .student-hero h1 { font-size:27px!important; letter-spacing:-.7px!important; }
        .student-hero p { color:#d6dddb!important; }
        .student-eyebrow { padding:4px 8px; color:#b9d8d3; border-color:rgba(255,255,255,.14); background:rgba(255,255,255,.06); }
        .section-kicker { color:#0f766e; }
        .privacy-note { border-color:#d5e4e1; background:#f0f7f5; }
        .profile-banner { padding:24px 26px; border-color:#dfe3e1; border-radius:14px; background:#fff; box-shadow:0 2px 8px rgba(23,32,31,.04); }
        .profile-avatar { width:48px; height:48px; margin-bottom:13px; border-radius:12px; background:#0f766e; box-shadow:none; }
        .profile-banner h1 { font-size:24px!important; }
        .status-grid { gap:10px; margin:14px 0 22px; }
        .status-card { padding:14px; border-color:#dfe3e1; border-radius:10px; background:#fff; }
        div[data-baseweb="tab-list"] { background:#eef1f0; }
        button[data-baseweb="tab"][aria-selected="true"] { color:#0f766e; box-shadow:0 1px 3px rgba(23,32,31,.08); }
        @media (max-width:700px) { .student-hero{padding:23px 20px}.student-hero h1{font-size:24px!important}.status-grid{grid-template-columns:1fr} }
        </style>
        """
    )

def _brand_bar(show_home=True):
    brand_col, action_col = st.columns([4, 1])
    with brand_col:
        st.html(
            """
            <div class="student-brand">
                <div class="student-brand-mark">🎯</div>
                <div><strong>AttendIQ</strong><span>Student identity portal</span></div>
            </div>
            """
        )
    if show_home:
        with action_col:
            st.write("")
            if st.button("← Home", width="stretch", key="student_home"):
                st.session_state["login_type"] = None
                st.rerun()
    else:
        with action_col:
            st.write("")
            if st.button("Sign out", width="stretch", key="student_sign_out"):
                for key in (
                    "student_data",
                    "is_logged_in",
                    "user_role",
                    "student_auth_mode",
                ):
                    st.session_state.pop(key, None)
                st.session_state["login_type"] = None
                st.rerun()


def _set_student_session(student):
    st.session_state["is_logged_in"] = True
    st.session_state["user_role"] = "student"
    st.session_state["student_data"] = student


def _audio_input(key_prefix):
    source = st.radio(
        "Audio source",
        ["Record with microphone", "Upload an audio file"],
        horizontal=True,
        key=f"{key_prefix}_source",
        label_visibility="collapsed",
    )
    if source == "Record with microphone":
        st.caption("Allow microphone access when asked, then record 5–10 seconds.")
        return st.audio_input(
            "Record your voice",
            sample_rate=16000,
            key=f"{key_prefix}_recording",
        )
    st.caption("Use a clear recording with one speaker and little background noise.")
    return st.file_uploader(
        "Upload WAV, MP3, M4A, OGG or FLAC",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        key=f"{key_prefix}_upload",
    )


def _find_student(student_id):
    return next(
        (
            student
            for student in get_all_students()
            if str(student.get("student_id")) == str(student_id)
        ),
        None,
    )


def _face_login():
    st.html(
        """
        <div class="section-kicker">FACE ID</div>
        <div class="section-title">Look into the camera</div>
        <div class="section-copy">Use a clear, front-facing photo with only your face in the frame.</div>
        """
    )
    photo = st.camera_input(
        "Student face", key="student_login_photo", label_visibility="collapsed"
    )
    if st.button(
        "Verify my face →",
        type="primary",
        width="stretch",
        disabled=photo is None,
        key="verify_student_face",
    ):
        try:
            image = np.array(Image.open(photo).convert("RGB"))
            with st.spinner("Comparing your face securely…"):
                # FEATURE 1: Validate the login image and preserve ambiguous
                # matches instead of automatically choosing a similar student.
                analysis = analyze_face_image(image)
                face_count = analysis["face_count"]
                matched_faces = [
                    match
                    for match in analysis["matches"]
                    if match.get("status") == "matched"
                ]
                review_faces = [
                    match
                    for match in analysis["matches"]
                    if match.get("status") == "needs_review"
                ]
            if not analysis["quality"]["accepted"]:
                st.warning(
                    "Photo rejected: " + " ".join(analysis["quality"]["reasons"])
                )
                return
            if face_count == 0:
                st.warning("No face was detected. Improve the lighting and try again.")
            elif face_count > 1:
                st.warning("More than one face was detected. Keep only your face in the frame.")
            elif review_faces:
                st.warning(
                    "This face is too similar to more than one profile. Use Voice ID "
                    "or ask a teacher to review your registration."
                )
            elif not matched_faces:
                st.error("We could not match this face to a registered student.")
            else:
                student = _find_student(matched_faces[0]["student_id"])
                if student is None:
                    st.error("The face matched, but the student profile could not be loaded.")
                else:
                    _set_student_session(student)
                    st.toast("Identity verified", icon="✅")
                    st.rerun()
        except Exception:
            st.error("Face verification could not be completed. Please retake the photo.")


def _voice_login():
    st.html(
        """
        <div class="section-kicker">VOICE ID</div>
        <div class="section-title">Verify with your voice</div>
        <div class="section-copy">Say a natural sentence for 5–10 seconds, or upload a clear recording.</div>
        """
    )
    audio = _audio_input("student_login_voice")
    if st.button(
        "Verify my voice →",
        type="primary",
        width="stretch",
        disabled=audio is None,
        key="verify_student_voice",
    ):
        try:
            with st.spinner("Creating and comparing your voice signature…"):
                new_embedding = get_voice_embedding(audio.getvalue())
                students = get_all_students()
                stored_voices = {
                    str(student["student_id"]): student.get("voice_embedding")
                    for student in students
                    if student.get("voice_embedding")
                }
                if not stored_voices:
                    st.warning("No students have enrolled a voice yet. Use Face ID instead.")
                    return
                student_id, similarity = identify_speaker(new_embedding, stored_voices)
            if student_id is None:
                st.error(
                    f"Voice not recognized. Best match confidence: {max(similarity, 0):.0%}."
                )
            else:
                student = _find_student(student_id)
                if student is None:
                    st.error("The voice matched, but the student profile could not be loaded.")
                else:
                    _set_student_session(student)
                    st.toast("Voice verified", icon="✅")
                    st.rerun()
        except Exception:
            st.error("Voice verification failed. Try a quieter recording or upload an audio file.")


def _login_panel():
    left, right = st.columns([1.22, 0.78], gap="large")
    with left:
        with st.container(border=True):
            face_tab, voice_tab = st.tabs(["👤  Face ID", "🎙️  Voice ID"])
            with face_tab:
                _face_login()
            with voice_tab:
                _voice_login()
    with right:
        st.html(
            """
            <div class="section-kicker">NEW HERE?</div>
            <div class="section-title">Create your profile</div>
            <div class="section-copy">Enroll your face once. Voice enrollment is optional and gives you another way to sign in.</div>
            <div class="privacy-note"><span>🔐</span><span>Your biometric features are converted into numerical embeddings used for recognition.</span></div>
            """
        )
        st.write("")
        if st.button("Create student profile", width="stretch", key="open_student_register"):
            st.session_state["student_auth_mode"] = "register"
            st.rerun()


def _register_panel():
    title_col, back_col = st.columns([4, 1])
    with title_col:
        st.html(
            """
            <div class="section-kicker">NEW PROFILE</div>
            <div class="section-title">Set up your student identity</div>
            <div class="section-copy">Add at least two clear face samples. Voice enrollment is optional.</div>
            """
        )
    with back_col:
        if st.button("← Sign in", width="stretch", key="back_to_student_login"):
            st.session_state["student_auth_mode"] = "login"
            st.rerun()
    with st.container(border=True):
        details_col, biometric_col = st.columns([0.85, 1.15], gap="large")
        with details_col:
            st.markdown("#### 1. Your details")
            name = st.text_input(
                "Full name", placeholder="Enter your full name", key="new_student_name"
            )
            st.markdown("#### 2. Optional voice")
            st.caption("You can skip this and register with Face ID only.")
            audio = _audio_input("student_enroll_voice")
        with biometric_col:
            st.markdown("#### 3. Face enrollment")
            # FEATURE 1: One camera sample plus uploaded alternatives creates a
            # more representative profile than a single enrollment photograph.
            st.caption(
                "Capture one photo and add at least one more sample. Use different "
                "angles with good lighting and only one face in every image."
            )
            photo = st.camera_input(
                "Enrollment photo",
                key="student_enrollment_photo",
                label_visibility="collapsed",
            )
            additional_photos = st.file_uploader(
                "Additional face samples",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                key="student_additional_face_samples",
                help="Upload up to four additional clear photos of the same student.",
            )
        st.divider()
        if st.button(
            "Create my profile →",
            type="primary",
            width="stretch",
            key="create_student_profile",
        ):
            if not name.strip():
                st.warning("Enter your full name before continuing.")
                return
            face_files = ([photo] if photo is not None else []) + list(
                (additional_photos or [])[:4]
            )
            if len(face_files) < 2:
                st.warning("Provide at least two face samples before continuing.")
                return
            try:
                with st.spinner("Creating your secure biometric profile…"):
                    # FEATURE 1: Validate every sample independently and reject
                    # duplicates, blur, bad lighting, and multiple-face images.
                    face_embeddings = []
                    rejected_samples = []
                    sample_hashes = set()
                    for sample_number, face_file in enumerate(face_files, start=1):
                        file_bytes = face_file.getvalue()
                        file_hash = hashlib.sha256(file_bytes).hexdigest()
                        if file_hash in sample_hashes:
                            rejected_samples.append(
                                f"Sample {sample_number}: duplicate image."
                            )
                            continue
                        sample_hashes.add(file_hash)

                        sample_image = np.array(Image.open(face_file).convert("RGB"))
                        quality = assess_image_quality(sample_image)
                        if not quality["accepted"]:
                            rejected_samples.append(
                                f"Sample {sample_number}: {' '.join(quality['reasons'])}"
                            )
                            continue

                        sample_embeddings = get_face_embeddings(sample_image)
                        if len(sample_embeddings) != 1:
                            reason = (
                                "no face detected"
                                if not sample_embeddings
                                else "multiple faces detected"
                            )
                            rejected_samples.append(
                                f"Sample {sample_number}: {reason}."
                            )
                            continue
                        face_embeddings.append(sample_embeddings[0])

                    if rejected_samples:
                        st.warning(" ".join(rejected_samples))
                    if len(face_embeddings) < 2:
                        st.error(
                            "At least two valid, different face samples are required. "
                            "Replace the rejected images and try again."
                        )
                        return

                    voice_embedding = None
                    if audio is not None:
                        voice_embedding = get_voice_embedding(audio.getvalue())
                        if voice_embedding is None:
                            st.error(
                                "The voice recording could not be processed. Retake it or register without voice."
                            )
                            return
                    created = create_student(
                        name.strip(),
                        face_embeddings[0].tolist(),
                        voice_embedding,
                        face_embeddings=[sample.tolist() for sample in face_embeddings],
                    )
                if not created:
                    st.error("Your profile could not be saved. Please try again.")
                    return
                train_classifier()
                _set_student_session(created[0])
                st.toast("Profile created successfully", icon="✅")
                st.rerun()
            except Exception:
                st.error("Profile creation failed. Check the photo and try again.")


def student_dashboard():
    student = st.session_state["student_data"]
    student_id = student["student_id"]
    _brand_bar(show_home=False)
    try:
        with st.spinner("Loading your enrolled subjects…"):
            subjects = get_student_subjects(student_id)
            attendance_logs = get_student_attendance(student_id)
    except Exception:
        logger.exception("Could not load enrollment data for student %s", student_id)
        st.error("Your subjects could not be loaded. Check the database connection.")
        footer_dashboard()
        return

    stats_map = {}
    for attendance_log in attendance_logs:
        subject_key = str(attendance_log.get("subject_id"))
        if subject_key not in stats_map:
            stats_map[subject_key] = {"total": 0, "attended": 0}
        stats_map[subject_key]["total"] += 1
        if attendance_log.get("is_present"):
            stats_map[subject_key]["attended"] += 1

    # UI REDESIGN: The first screen answers the student's main question—current
    # attendance standing—before showing identity or enrollment details.
    total_classes = sum(item["total"] for item in stats_map.values())
    total_attended = sum(item["attended"] for item in stats_map.values())
    overall_percentage = (
        total_attended / total_classes * 100 if total_classes else 0.0
    )
    safe_name = escape(str(student.get("name") or "Student"))
    display_student_id = escape(str(student_id))
    standing = (
        "Good standing"
        if overall_percentage >= 75
        else "Attendance needs attention"
        if total_classes
        else "No attendance recorded yet"
    )
    st.html(
        f"""
        <div class="iq-student-overview">
            <div class="iq-eyebrow">STUDENT #{display_student_id}</div>
            <h1>Hello, {safe_name}</h1>
            <p>{standing}. Your overall attendance across enrolled subjects is shown below.</p>
            <div class="iq-overall-score"><strong>{overall_percentage:.0f}%</strong><span>overall attendance</span></div>
            <div class="iq-progress"><span style="width:{overall_percentage:.1f}%"></span></div>
        </div>
        """
    )

    metric_one, metric_two, metric_three = st.columns(3)
    metric_one.metric("Classes recorded", total_classes)
    metric_two.metric("Classes attended", total_attended)
    metric_three.metric("Enrolled subjects", len(subjects))

    title_col, enroll_col = st.columns([3, 1], vertical_alignment="bottom")
    with title_col:
        st.html(
            """
            <div class="iq-eyebrow" style="margin-top:24px">MY SUBJECTS</div>
            <h2 style="margin:0;font-size:21px">Attendance by subject</h2>
            <p style="margin:4px 0 0;font-size:12px">The recommended minimum is 75%.</p>
            """
        )
    with enroll_col:
        if st.button(
            "Enroll in subject",
            type="primary",
            icon=":material/add:",
            width="stretch",
            key="open_enroll_subject_dialog",
        ):
            enroll_dialog()

    st.divider()

    if not subjects:
        st.info("You have not enrolled in any subjects yet. Use the button above to join one.")
        footer_dashboard()
        return

    columns = st.columns(2)
    for index, enrollment in enumerate(subjects):
        subject = enrollment.get("subjects")
        if isinstance(subject, list):
            subject = subject[0] if subject else None
        if not subject:
            continue

        subject_id = subject.get("subject_id") or enrollment.get("subject_id")
        subject_name = subject.get("name", "Unnamed subject")
        subject_code = subject.get("subject_code", "N/A")
        subject_section = subject.get("section", "N/A")
        stats = stats_map.get(str(subject_id), {"total": 0, "attended": 0})
        attendance_percentage = (
            stats["attended"] / stats["total"] * 100 if stats["total"] else 0.0
        )
        attendance_status = (
            "Good standing"
            if stats["total"] and attendance_percentage >= 75
            else "Below 75%"
            if stats["total"]
            else "No records"
        )

        def unenroll_button(
            course_id=subject_id,
            course_name=subject_name,
            course_code=subject_code,
        ):
            if st.button(
                "Unenroll from this subject",
                type="tertiary",
                width="stretch",
                key=f"unenroll_subject_{course_id}_{course_code}",
            ):
                try:
                    unenrolled = unenroll_student_from_subject(student_id, course_id)
                    if not unenrolled:
                        st.error("The subject could not be removed. Please try again.")
                        return
                    st.toast(f"Unenrolled from {course_name} successfully!", icon="✅")
                    st.rerun()
                except Exception:
                    logger.exception(
                        "Could not unenroll student %s from subject %s",
                        student_id,
                        course_id,
                    )
                    st.error("Unenrollment failed. Check the database connection.")

        with columns[index % 2]:
            subject_card(
                name=subject_name,
                code=subject_code,
                section=subject_section,
                stats=[
                    ("", "Classes", stats["total"]),
                    ("", "Present", stats["attended"]),
                ],
                footer_callback=unenroll_button,
                progress=attendance_percentage,
                status=attendance_status,
            )

    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()
    _style_student_portal()
    # UI REDESIGN: Load the shared final layer after older student-specific CSS.
    style_product_ui()
    if st.session_state.get("student_data"):
        student_dashboard()
        return
    _brand_bar()
    st.html(
        """
        <div class="student-hero">
            <div class="student-eyebrow">● SECURE STUDENT ACCESS</div>
            <h1>One identity. Two simple ways to sign in.</h1>
            <p>Verify with Face ID or Voice ID. New students can create a biometric profile in under a minute.</p>
        </div>
        """
    )
    if st.session_state.get("student_auth_mode", "login") == "register":
        _register_panel()
    else:
        _login_panel()
