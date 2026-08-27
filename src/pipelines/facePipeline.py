import dlib
import numpy as np
import streamlit as st
import face_recognition_models

from sklearn.svm import SVC
from src.database.db import get_all_students


# FEATURE 1: Central thresholds make image-quality and ambiguity decisions easy
# to tune later with real classroom validation data.
MIN_IMAGE_SIDE = 160
MIN_BRIGHTNESS = 45.0
MAX_BRIGHTNESS = 215.0
MIN_CONTRAST = 18.0
MIN_BLUR_SCORE = 45.0
NORMAL_MATCH_THRESHOLD = 0.58
SINGLE_STUDENT_MATCH_THRESHOLD = 0.45
AMBIGUITY_MARGIN = 0.08
MIN_FACE_SIZE_RATIO = 0.06

@st.cache_resource
def load_dlib_models():

    face_detector = dlib.get_frontal_face_detector()

    landmark_predictor = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    face_encoder = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return face_detector, landmark_predictor, face_encoder

def get_face_embeddings(image):

    face_detector, landmark_predictor, face_encoder = load_dlib_models()
    # Detect every face present in the image.
    faces = face_detector(image, 1)

    face_embeddings = []

    for face in faces:

        # Find facial landmarks like eyes, nose and mouth.
        landmarks = landmark_predictor(image, face)

        # Convert face into 128 numerical values.
        embedding = face_encoder.compute_face_descriptor(
            image,
            landmarks,
            1
        )

        face_embeddings.append(
            np.array(embedding)
        )

    return face_embeddings


# FEATURE 1: Reject unusable images before recognition. The blur score uses a
# small NumPy Laplacian so the project does not require an additional OpenCV
# dependency.
def assess_image_quality(image):
    image_array = np.asarray(image)
    if image_array.ndim != 3 or image_array.shape[2] < 3:
        return {
            "accepted": False,
            "reasons": ["The image must be a colour photograph."],
            "brightness": 0.0,
            "contrast": 0.0,
            "blur_score": 0.0,
        }

    height, width = image_array.shape[:2]
    gray = (
        0.299 * image_array[:, :, 0]
        + 0.587 * image_array[:, :, 1]
        + 0.114 * image_array[:, :, 2]
    ).astype(np.float32)
    brightness = float(gray.mean())
    contrast = float(gray.std())

    if height >= 3 and width >= 3:
        laplacian = (
            gray[:-2, 1:-1]
            + gray[2:, 1:-1]
            + gray[1:-1, :-2]
            + gray[1:-1, 2:]
            - 4 * gray[1:-1, 1:-1]
        )
        blur_score = float(laplacian.var())
    else:
        blur_score = 0.0

    reasons = []
    if min(height, width) < MIN_IMAGE_SIDE:
        reasons.append("Image resolution is too small.")
    if brightness < MIN_BRIGHTNESS:
        reasons.append("Image is too dark.")
    elif brightness > MAX_BRIGHTNESS:
        reasons.append("Image is too bright.")
    if contrast < MIN_CONTRAST:
        reasons.append("Image has very low contrast.")
    if blur_score < MIN_BLUR_SCORE:
        reasons.append("Image is too blurred.")

    return {
        "accepted": not reasons,
        "reasons": reasons,
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "blur_score": round(blur_score, 2),
    }


# FEATURE 1: Read all registered samples while remaining compatible with old
# students that only have the original `face_embedding` column.
def _student_face_samples(student):
    samples = student.get("face_embeddings") or []
    if samples and isinstance(samples[0], (int, float)):
        samples = [samples]

    legacy_sample = student.get("face_embedding")
    if legacy_sample:
        samples = list(samples) + [legacy_sample]

    valid_samples = []
    for sample in samples:
        sample_array = np.asarray(sample, dtype=np.float64)
        if sample_array.shape == (128,):
            valid_samples.append(sample_array)
    return valid_samples


# FEATURE 1: Directly compare every student's samples and detect close first
# and second choices. SVM alone always chooses somebody, which is unsafe for an
# unknown or very similar face.
def match_face_embedding(face_embedding, candidate_students):
    candidates = []
    for student in candidate_students:
        samples = _student_face_samples(student)
        if not samples:
            continue
        best_distance = min(
            float(np.linalg.norm(sample - face_embedding)) for sample in samples
        )
        candidates.append(
            {
                "student_id": int(student["student_id"]),
                "name": student.get("name", "Unknown student"),
                "distance": best_distance,
            }
        )

    candidates.sort(key=lambda item: item["distance"])
    if not candidates:
        return {"status": "unknown", "candidates": []}

    best = candidates[0]
    second = candidates[1] if len(candidates) > 1 else None
    threshold = (
        SINGLE_STUDENT_MATCH_THRESHOLD
        if len(candidates) == 1
        else NORMAL_MATCH_THRESHOLD
    )
    similarity = max(0.0, min(1.0, 1.0 - best["distance"]))

    if best["distance"] > threshold:
        return {
            "status": "unknown",
            "student_id": None,
            "similarity": similarity,
            "candidates": candidates[:2],
        }

    margin = None if second is None else second["distance"] - best["distance"]
    if margin is not None and margin < AMBIGUITY_MARGIN:
        return {
            "status": "needs_review",
            "student_id": None,
            "similarity": similarity,
            "margin": margin,
            "candidates": candidates[:2],
        }

    return {
        "status": "matched",
        "student_id": best["student_id"],
        "name": best["name"],
        "distance": best["distance"],
        "similarity": similarity,
        "margin": margin,
        "candidates": candidates[:2],
    }


# FEATURE 1: Rich analysis result used by teacher attendance and student login.
# It reports rejected images, unknown faces and ambiguous candidates instead of
# silently forcing every face into a registered identity.
def analyze_face_image(image, candidate_students=None, check_quality=True):
    quality = assess_image_quality(image)
    result = {
        "quality": quality,
        "face_count": 0,
        "matches": [],
        "registered_student_ids": [],
    }
    if check_quality and not quality["accepted"]:
        return result

    students = candidate_students if candidate_students is not None else get_all_students()
    students = list(students or [])
    result["registered_student_ids"] = sorted(
        {
            int(student["student_id"])
            for student in students
            if student.get("student_id") is not None
        }
    )

    face_detector, landmark_predictor, face_encoder = load_dlib_models()
    faces = face_detector(image, 1)
    result["face_count"] = len(faces)
    minimum_side = max(1, min(image.shape[:2]))

    for face_index, face in enumerate(faces, start=1):
        face_ratio = min(face.width(), face.height()) / minimum_side
        if face_ratio < MIN_FACE_SIZE_RATIO:
            result["matches"].append(
                {
                    "face_index": face_index,
                    "status": "low_quality",
                    "reason": "Detected face is too small for reliable recognition.",
                    "candidates": [],
                }
            )
            continue

        landmarks = landmark_predictor(image, face)
        embedding = np.asarray(
            face_encoder.compute_face_descriptor(image, landmarks, 1)
        )
        match = match_face_embedding(embedding, students)
        match["face_index"] = face_index
        result["matches"].append(match)

    return result


# TRAIN SVM
# X = face embeddings
# y = student IDs

@st.cache_resource
def get_trained_model():

    embeddings = []
    student_ids = []

    students = get_all_students()

    if not students:
        return None

    # Prepare training data from database.
    for student in students:
        # FEATURE 1: Include all face samples when rebuilding the legacy SVM.
        for stored_embedding in _student_face_samples(student):
            embeddings.append(stored_embedding)
            student_ids.append(student.get("student_id"))
    if not embeddings:
        return None

    classifier = SVC(
        kernel="linear",
        probability=True,
        class_weight="balanced"
    )

    # SVM needs at least two different classes.
    if len(set(student_ids)) >= 2:
        classifier.fit(
            embeddings,
            student_ids
        )

    return {
        "classifier": classifier,
        "embeddings": embeddings,
        "student_ids": student_ids
    }

# RETRAIN SVM
# Run this after adding a new student.
def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return model_data is not None


def predict_attendance(classroom_image):
    # FEATURE 1: Compatibility wrapper for existing callers. New attendance UI
    # uses `analyze_face_image` to access quality and review information.
    analysis = analyze_face_image(classroom_image)
    detected_students = {
        match["student_id"]: True
        for match in analysis["matches"]
        if match.get("status") == "matched"
    }
    return (
        detected_students,
        analysis["registered_student_ids"],
        analysis["face_count"],
    )
