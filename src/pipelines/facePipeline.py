import dlib
import numpy as np
import streamlit as st
import face_recognition_models

from sklearn.svm import SVC
from src.database.db import get_all_students


# STEP 1: LOAD DLIB MODELS
# We cache these models because loading them is expensive.
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


# STEP 2: CONVERT ALL FACES IN IMAGE INTO 128-D EMBEDDINGS
#
# Input:
# classroom image
#
# Output:
# [
#   embedding_face_1,
#   embedding_face_2,
#   ...
# ]

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


# STEP 3: TRAIN SVM
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
        stored_embedding = student.get("face_embedding")

        if stored_embedding:

            embeddings.append(
                np.array(stored_embedding)
            )

            student_ids.append(
                student.get("student_id")
            )
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

# STEP 4: RETRAIN SVM
# Run this after adding a new student.
def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return model_data is not None

# STEP 5: RECOGNIZE STUDENTS FROM CLASSROOM IMAGE
# Flow:
#
# image
#   ↓
# detect faces
#   ↓
# create embedding for every face
#   ↓
# SVM predicts student
#   ↓
# compare with stored embedding
#   ↓
# distance <= 0.6
#   ↓
# accept student

def predict_attendance(classroom_image):
    # Get embedding for every face detected in classroom image.
    detected_face_embeddings = get_face_embeddings( classroom_image )
    # Dictionary prevents duplicate student IDs.
    detected_students = {}


    # Load classifier + stored embeddings.
    model_data = get_trained_model()

    if not model_data:
        return detected_students, [], len(detected_face_embeddings)


    classifier = model_data["classifier"]

    stored_embeddings = model_data["embeddings"]

    stored_student_ids = model_data["student_ids"]


    # Get unique registered students.
    registered_students = sorted(
        set(stored_student_ids)
    )


    # Process every detected face one by one.
    for face_embedding in detected_face_embeddings:


        # ------------------------------------------
        # STEP A: FIND POSSIBLE STUDENT
        # ------------------------------------------

        if len(registered_students) >= 2:

            predicted_student_id = int(
                classifier.predict(
                    [face_embedding]
                )[0]
            )

        else:

            # If only one student exists,
            # use that student as possible match.
            predicted_student_id = int(
                registered_students[0]
            )

        # STEP B: GET THAT STUDENT'S STORED FACE

        student_position = stored_student_ids.index(
            predicted_student_id
        )

        stored_face_embedding = stored_embeddings[
            student_position
        ]


        # ------------------------------------------
        # STEP C: COMPARE BOTH FACES
        # ------------------------------------------
        #
        # We calculate Euclidean distance between:
        #
        # stored face
        #      VS
        # detected face
        #
        # Smaller distance = more similar faces.

        face_distance = np.linalg.norm(
            stored_face_embedding - face_embedding
        )


        # ------------------------------------------
        # STEP D: VERIFY MATCH
        # ------------------------------------------

        # A classifier cannot discriminate identities when only one student is
        # registered. In that case use a stricter direct-embedding comparison
        # so an unrelated face is not automatically attributed to that one
        # student. Multi-student predictions retain the standard tolerance.
        match_threshold = 0.45 if len(registered_students) == 1 else 0.6


        if face_distance <= match_threshold:

            # Example:
            #
            # First detection:
            # detected_students[5] = True
            #
            # Second detection of same student:
            # detected_students[5] = True
            #
            # Dictionary still contains only:
            #
            # {5: True}

            detected_students[
                predicted_student_id
            ] = True


    return (
        detected_students,
        registered_students,
        len(detected_face_embeddings)
    )
