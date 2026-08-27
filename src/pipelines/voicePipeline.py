# 1. Convert one audio sample -> voice embedding
# 2. Compare one embedding with stored students = best student
# 3. Split a long classroom audio --> identify speakers from each segment

from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import librosa
import streamlit as st
import io

@st.cache_resource
def load_voice_encoder():

    encoder = VoiceEncoder()

    return encoder

def get_voice_embedding(audio_bytes):

    try:
        encoder = load_voice_encoder()
        # Load audio and convert it to 16 kHz.
        audio, sample_rate = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )

        # Clean and prepare audio for Resemblyzer.
        clean_audio = preprocess_wav(audio)

        # Convert voice into numerical embedding.
        voice_embedding = encoder.embed_utterance(
            clean_audio
        )

        # Convert NumPy array to list
        # so we can store it in database/JSON.
        return voice_embedding.tolist()

    except Exception as error:

        st.error("Voice recognition error")

        return None


def identify_speaker( new_voice_embedding, stored_student_voices, match_threshold=0.65):

    if new_voice_embedding is None or not stored_student_voices:
        return None, 0.0

    best_student_id = None

    best_similarity = -1.0

    # Compare new voice with every registered student's voice.
    for student_id, stored_voice_embedding in stored_student_voices.items():

        if not stored_voice_embedding:
            continue

        # Cosine-style similarity.
        # Higher score = more similar voices.
        similarity = np.dot(
            new_voice_embedding,
            stored_voice_embedding
        )

        # Keep only the best matching student.
        if similarity > best_similarity:
            best_similarity = similarity
            best_student_id = student_id

    # Accept only if similarity is high enough.
    if best_similarity >= match_threshold:
        return best_student_id, best_similarity

    # Otherwise speaker is unknown.
    return None, best_similarity

def process_bulk_audio( audio_bytes, stored_student_voices, match_threshold=0.65 ):
    try:
        encoder = load_voice_encoder()
        # Load classroom audio.
        audio, sample_rate = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )

        # Split audio wherever silence occurs.
        voice_segments = librosa.effects.split(
            audio,
            top_db=30
        )

        # Stores unique recognized students.
        recognized_students = {}
        # Process every speaking segment.
        for segment_start, segment_end in voice_segments:
            # Ignore very short sounds below 0.5 seconds.
            segment_length = segment_end - segment_start

            if segment_length < sample_rate * 0.5:
                continue

            # Extract only this speaking part.
            voice_segment = audio[
                segment_start:segment_end
            ]

            # Prepare audio.
            clean_segment = preprocess_wav(
                voice_segment
            )

            # Convert this voice segment into embedding.
            segment_embedding = encoder.embed_utterance(
                clean_segment
            )

            # Find which student matches this voice.
            student_id, similarity = identify_speaker(
                segment_embedding,
                stored_student_voices,
                match_threshold
            )

            # If student was recognized.
            if student_id is not None:
                # If same student speaks multiple times,
                # keep only the highest similarity score.
                if (
                    student_id not in recognized_students
                    or similarity > recognized_students[student_id]
                ):

                    recognized_students[student_id] = similarity


        return recognized_students
    except Exception as error:

        st.error("Bulk voice processing error")

        return {}

    