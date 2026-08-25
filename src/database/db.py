from src.database.config import supabase
import bcrypt

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

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data if response.data else []

def create_student(name, face_embedding=None, voice_embedding=None):
    data = {
        "name": name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
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
        .select("*, subject_student(count), attendance_logs(timestamp)")
        .eq("teacher_id", teacher_id)
        .execute()
    )
    subjects = response.data if response.data else []

    for subject in subjects:
        subject["total_students"] = _relation_count(subject.get("subject_student"))

        attendance_logs = subject.get("attendance_logs") or []
        # The current schema has no attendance-session ID. Treat records from
        # the same calendar date as one class until sessions are modelled.
        class_dates = {
            str(log.get("timestamp"))[:10]
            for log in attendance_logs
            if log.get("timestamp")
        }
        subject["total_classes"] = len(class_dates)

        subject.pop("subject_student", None)
        subject.pop("attendance_logs", None)

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
        .select("student_id, students(student_id, name, voice_embedding)")
        .eq("subject_id", subject_id)
        .execute()
    )
    return response.data if response.data else []


def create_attendance(attendance_logs):
    if not attendance_logs:
        return None
    response = supabase.table("attendance_logs").insert(attendance_logs).execute()
    return response.data if response.data else None


def get_attendance_records_for_teacher(teacher_id):
    # ``!inner`` is important here: without it PostgREST does not filter the
    # attendance rows by the owning teacher. The student relation must also be
    # selected because the records screen displays the student's name.
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
