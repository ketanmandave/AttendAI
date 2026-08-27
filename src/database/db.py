from src.database.config import supabase
import bcrypt
from datetime import datetime, timezone

def check_teacher_exists(username):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    return len(response.data) > 0 # Returns True if teacher exists, False otherwise

def create_teacher(username, password, name):
    data ={
        "username": username,
        "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "name": name
    }
    response = supabase.table("teachers").insert(data).execute()
    return response.data[0] if response.data else None

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if len(response.data) == 0:
        return None  # Teacher not found
    teacher = response.data[0]
    if bcrypt.checkpw(password.encode('utf-8'), teacher['password'].encode('utf-8')):
        return teacher  # Successful login
    else:
        return None  # Incorrect password


# SESSION MANAGEMENT: Only a SHA-256 hash is stored in Supabase. The raw token
# remains in the teacher's browser cookie and is never written to the database.
def create_teacher_session(teacher_id, token_hash, expires_at):
    response = (
        supabase.table("user_sessions")
        .insert(
            {
                "teacher_id": teacher_id,
                "token_hash": token_hash,
                "expires_at": expires_at,
            }
        )
        .execute()
    )
    return response.data[0] if response.data else None


# SESSION MANAGEMENT: Validate the session first, then load a safe teacher
# projection so the password hash is never placed in Streamlit session state.
def get_teacher_for_session(token_hash):
    response = (
        supabase.table("user_sessions")
        .select("session_id, teacher_id, expires_at, revoked_at")
        .eq("token_hash", token_hash)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None

    session = response.data[0]
    if session.get("revoked_at"):
        return None

    expires_at = session.get("expires_at")
    if not expires_at:
        return None

    try:
        parsed_expiry = datetime.fromisoformat(
            str(expires_at).replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return None
    if parsed_expiry.tzinfo is None:
        parsed_expiry = parsed_expiry.replace(tzinfo=timezone.utc)
    if parsed_expiry <= datetime.now(timezone.utc):
        return None

    teacher_response = (
        supabase.table("teachers")
        .select("teacher_id, username, name")
        .eq("teacher_id", session["teacher_id"])
        .limit(1)
        .execute()
    )
    if not teacher_response.data:
        return None

    return {
        "session_id": session["session_id"],
        "expires_at": expires_at,
        "teacher": teacher_response.data[0],
    }


# SESSION MANAGEMENT: Logout invalidates the server-side record even if the
# browser cannot immediately remove its cookie.
def revoke_teacher_session(token_hash):
    response = (
        supabase.table("user_sessions")
        .update({"revoked_at": datetime.now(timezone.utc).isoformat()})
        .eq("token_hash", token_hash)
        .execute()
    )
    return response.data[0] if response.data else None

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data if response.data else []

def create_student(
    name,
    face_embedding=None,
    voice_embedding=None,
    face_embeddings=None,
):
    # FEATURE 1: `face_embedding` is retained for existing deployments while
    # `face_embeddings` stores multiple registration samples for better matching.
    data = {
        "name": name,
        "face_embedding": face_embedding,
        "face_embeddings": face_embeddings or ([face_embedding] if face_embedding else []),
        "voice_embedding": voice_embedding,
    }
    response = supabase.table("students").insert(data).execute()
    return response.data if response.data else None

def create_subject(subject_code, name, section, teacher_id):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }
    response = supabase.table("subjects").insert(data).execute()
    return response.data if response.data else None

def _relation_count(value):
    """Read a Supabase embedded aggregate returned as a dict or one-item list."""
    if isinstance(value, dict):
        return int(value.get("count") or 0)
    if isinstance(value, list) and value:
        return int(value[0].get("count") or 0)
    return 0

def get_teacher_subjects(teacher_id):
    response = (
        supabase.table("subjects")
        # FEATURE 2: Count real lecture sessions instead of unique calendar dates.
        .select("*, subject_student(count), attendance_sessions(session_id, status)")
        .eq("teacher_id", teacher_id)
        .execute()
    )
    subjects = response.data if response.data else []

    for subject in subjects:
        subject["total_students"] = _relation_count(subject.get("subject_student"))

        attendance_sessions = subject.get("attendance_sessions") or []
        subject["total_classes"] = sum(
            session.get("status") == "completed"
            for session in attendance_sessions
        )

        subject.pop("subject_student", None)
        subject.pop("attendance_sessions", None)

    return subjects

def enroll_student_to_subject(student_id, subject_id):
    data = {
        "student_id": student_id,
        "subject_id": subject_id
    }
    response = supabase.table("subject_student").insert(data).execute()
    return response.data if response.data else None


def unenroll_student_from_subject(student_id, subject_id):
    response = (
        supabase.table("subject_student")
        .delete()
        .eq("student_id", student_id)
        .eq("subject_id", subject_id)
        .execute()
    )
    return response.data if response.data else None


def get_student_subjects(student_id):
    response = (
        supabase.table("subject_student")
        .select("subject_id, subjects(subject_id, name, subject_code, section)")
        .eq("student_id", student_id)
        .execute()
    )
    return response.data if response.data else []


def get_student_attendance(student_id):
    response = (
        supabase.table("attendance_logs")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )
    return response.data if response.data else []


def get_subject_by_code(subject_code):
    response = (
        supabase.table("subjects")
        .select("subject_id, name, subject_code, section")
        .eq("subject_code", subject_code)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def is_student_enrolled(student_id, subject_id):
    response = (
        supabase.table("subject_student")
        .select("student_id")
        .eq("student_id", student_id)
        .eq("subject_id", subject_id)
        .limit(1)
        .execute()
    )
    return bool(response.data)


def get_subject_students(subject_id):
    response = (
        supabase.table("subject_student")
        # FEATURE 1: Attendance recognition must compare only enrolled students
        # and needs every registered face sample for each of them.
        .select(
            "student_id, students(student_id, name, face_embedding, "
            "face_embeddings, voice_embedding)"
        )
        .eq("subject_id", subject_id)
        .execute()
    )
    return response.data if response.data else []


def create_attendance(attendance_logs):
    if not attendance_logs:
        return None
    response = supabase.table("attendance_logs").insert(attendance_logs).execute()
    return response.data if response.data else None


# FEATURE 2: Create one lecture and attach every student record to its session ID.
# If record insertion fails, the empty draft session is removed as compensation.
def create_attendance_session_with_logs(
    subject_id,
    teacher_id,
    title,
    attendance_method,
    attendance_logs,
    started_at=None,
):
    if not attendance_logs:
        return None

    started_at = started_at or datetime.now(timezone.utc).isoformat()
    session_payload = {
        "subject_id": subject_id,
        "teacher_id": teacher_id,
        "title": (title or "Attendance session").strip(),
        "attendance_method": attendance_method,
        "started_at": started_at,
        "status": "draft",
    }
    session_response = (
        supabase.table("attendance_sessions").insert(session_payload).execute()
    )
    if not session_response.data:
        return None

    session = session_response.data[0]
    session_id = session["session_id"]
    unique_logs = {}
    for log in attendance_logs:
        student_id = log.get("student_id")
        if student_id is None:
            continue
        is_present = bool(log.get("is_present"))
        ai_is_present = bool(log.get("ai_is_present", is_present))
        unique_logs[str(student_id)] = {
            "session_id": session_id,
            "student_id": student_id,
            "subject_id": subject_id,
            "timestamp": started_at,
            "ai_is_present": ai_is_present,
            "is_present": is_present,
        }

    try:
        log_response = (
            supabase.table("attendance_logs")
            .insert(list(unique_logs.values()))
            .execute()
        )
        if not log_response.data:
            raise RuntimeError("Attendance records were not created")

        completed_at = datetime.now(timezone.utc).isoformat()
        completed_response = (
            supabase.table("attendance_sessions")
            .update({"status": "completed", "completed_at": completed_at})
            .eq("session_id", session_id)
            .eq("teacher_id", teacher_id)
            .execute()
        )
        if not completed_response.data:
            raise RuntimeError("Attendance session could not be completed")

        session.update(completed_response.data[0])
        session["attendance_logs"] = log_response.data
        return session
    except Exception:
        supabase.table("attendance_sessions").delete().eq(
            "session_id", session_id
        ).eq("teacher_id", teacher_id).execute()
        raise


# FEATURE 2: Return one row per actual lecture with its records for summary counts.
def get_teacher_attendance_sessions(teacher_id):
    response = (
        supabase.table("attendance_sessions")
        .select(
            "session_id, subject_id, teacher_id, title, attendance_method, "
            "started_at, completed_at, status, "
            "subjects(subject_id, name, subject_code, section), "
            "attendance_logs(id, student_id, is_present, ai_is_present)"
        )
        .eq("teacher_id", teacher_id)
        .order("started_at", desc=True)
        .execute()
    )
    return response.data if response.data else []


# FEATURE 2: Ownership is checked in the query before session details are shown.
def get_attendance_session_details(session_id, teacher_id):
    response = (
        supabase.table("attendance_sessions")
        .select(
            "session_id, subject_id, teacher_id, title, attendance_method, "
            "started_at, completed_at, status, "
            "subjects(subject_id, name, subject_code, section), "
            "attendance_logs(id, student_id, is_present, ai_is_present, "
            "students(student_id, name), "
            "attendance_corrections(correction_id, corrected_by, previous_status, "
            "new_status, reason, corrected_at, teachers(name)))"
        )
        .eq("session_id", session_id)
        .eq("teacher_id", teacher_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


# FEATURE 2: Change final attendance only after verifying that the record belongs
# to the logged-in teacher, then preserve the original and new values in history.
def correct_attendance_record(attendance_log_id, teacher_id, new_status, reason):
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("A correction reason is required")

    record_response = (
        supabase.table("attendance_logs")
        .select(
            "id, is_present, session_id, "
            "attendance_sessions!inner(teacher_id)"
        )
        .eq("id", attendance_log_id)
        .eq("attendance_sessions.teacher_id", teacher_id)
        .limit(1)
        .execute()
    )
    if not record_response.data:
        raise PermissionError("Attendance record not found for this teacher")

    previous_status = bool(record_response.data[0].get("is_present"))
    new_status = bool(new_status)
    if previous_status == new_status:
        return {"changed": False, "record": record_response.data[0]}

    update_response = (
        supabase.table("attendance_logs")
        .update({"is_present": new_status})
        .eq("id", attendance_log_id)
        .execute()
    )
    if not update_response.data:
        raise RuntimeError("Attendance record could not be updated")

    correction_payload = {
        "attendance_log_id": attendance_log_id,
        "corrected_by": teacher_id,
        "previous_status": previous_status,
        "new_status": new_status,
        "reason": reason,
    }
    try:
        correction_response = (
            supabase.table("attendance_corrections")
            .insert(correction_payload)
            .execute()
        )
        if not correction_response.data:
            raise RuntimeError("Correction history could not be saved")
    except Exception:
        supabase.table("attendance_logs").update(
            {"is_present": previous_status}
        ).eq("id", attendance_log_id).execute()
        raise

    return {
        "changed": True,
        "record": update_response.data[0],
        "correction": correction_response.data[0],
    }


def get_attendance_records_for_teacher(teacher_id):

    response = (
        supabase.table("attendance_logs")
        .select(
            "id, timestamp, subject_id, student_id, is_present, "
            "students(student_id, name), "
            "subjects!inner(subject_id, name, subject_code, section, teacher_id)"
        )
        .eq("subjects.teacher_id", teacher_id)
        .execute()
    )
    return response.data if response.data else []
