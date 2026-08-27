import hashlib
import io

import streamlit as st
from PIL import Image, UnidentifiedImageError


MAX_ATTENDANCE_IMAGES = 20


def _initialize_photo_state():
    st.session_state.setdefault("photo_tab", "camera")
    st.session_state.setdefault("attendance_images", [])
    st.session_state.setdefault("attendance_image_hashes", set())


def _add_image(uploaded_file):
    """Copy a valid uploaded image into session state and reject duplicates."""
    image_bytes = uploaded_file.getvalue()
    image_hash = hashlib.sha256(image_bytes).hexdigest()

    if image_hash in st.session_state.attendance_image_hashes:
        return "duplicate"
    if len(st.session_state.attendance_images) >= MAX_ATTENDANCE_IMAGES:
        return "limit"

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB").copy()
    except (UnidentifiedImageError, OSError):
        return "invalid"

    st.session_state.attendance_images.append(image)
    st.session_state.attendance_image_hashes.add(image_hash)
    return "added"


def _show_add_result(results):
    added = results.count("added")
    duplicates = results.count("duplicate")
    invalid = results.count("invalid")

    if added:
        st.toast(f"Added {added} photo{'s' if added != 1 else ''}.", icon="✅")
    if duplicates:
        st.info(f"Skipped {duplicates} duplicate photo{'s' if duplicates != 1 else ''}.")
    if invalid:
        st.warning(f"Skipped {invalid} invalid image file{'s' if invalid != 1 else ''}.")
    if "limit" in results:
        st.warning(f"A maximum of {MAX_ATTENDANCE_IMAGES} photos can be processed at once.")


@st.dialog("Add Classroom Photos", width="medium")
def add_photos_dialog():
    _initialize_photo_state()

    st.caption("Capture or upload classroom photos to scan for student attendance.")
    st.write(f"**{len(st.session_state.attendance_images)} photo(s) selected**")

    camera_col, upload_col = st.columns(2)
    with camera_col:
        camera_type = "primary" if st.session_state.photo_tab == "camera" else "tertiary"
        if st.button(
            "📷 Camera",
            type=camera_type,
            width="stretch",
            key="attendance_photo_camera_tab",
        ):
            st.session_state.photo_tab = "camera"

    with upload_col:
        upload_type = "primary" if st.session_state.photo_tab == "upload" else "tertiary"
        if st.button(
            "⬆️ Upload photos",
            type=upload_type,
            width="stretch",
            key="attendance_photo_upload_tab",
        ):
            st.session_state.photo_tab = "upload"

    if st.session_state.photo_tab == "camera":
        camera_action = st.empty()
        camera_photo = st.camera_input(
            "Take a classroom snapshot",
            key="attendance_dialog_camera",
        )

        with camera_action:
            if st.button(
                "Add captured photo",
                type="primary",
                width="stretch",
                disabled=camera_photo is None,
                key="add_camera_snapshot",
            ):
                _show_add_result([_add_image(camera_photo)])

    else:
        uploaded_files = st.file_uploader(
            "Choose classroom images",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="attendance_dialog_upload",
        )
        if st.button(
            "Add selected photos",
            type="primary",
            width="stretch",
            disabled=not uploaded_files,
            key="add_uploaded_attendance_photos",
        ):
            _show_add_result([_add_image(file) for file in uploaded_files])

    if st.session_state.attendance_images:
        st.divider()
        preview_images = st.session_state.attendance_images[-4:]
        st.image(
            preview_images,
            caption=[f"Selected photo {index + 1}" for index in range(len(preview_images))],
            width=150,
        )

    st.divider()
    clear_col, done_col = st.columns(2)
    with clear_col:
        if st.button(
            "Clear all",
            type="tertiary",
            width="stretch",
            disabled=not st.session_state.attendance_images,
            key="clear_attendance_photos",
        ):
            st.session_state.attendance_images = []
            st.session_state.attendance_image_hashes = set()
            st.toast("Selected photos cleared.")
            st.rerun()

    with done_col:
        if st.button("Done", type="primary", width="stretch", key="finish_adding_photos"):
            st.session_state.pop("photo_tab", None)
            st.rerun()
