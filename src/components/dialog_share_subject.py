import streamlit as st
import segno
import io


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):

    app_url = getattr(st.context, "url", "") or "http://localhost:8501"
    app_domain = app_url.split("?", 1)[0].rstrip("/")
    join_url = f"{app_domain}/?join-code={subject_code}"

    st.header("Scan to Join")

    # Generate QR code
    qr = segno.make(join_url)

    # Store QR image in memory
    out = io.BytesIO()

    qr.save(
        out,
        kind="png",
        scale=10,
        border=1
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Copy Link")

        st.code(
            join_url,
            language="text"
        )

        st.code(
            subject_code,
            language="text"
        )

        st.info(
            "Copy this link to share on WhatsApp or Email."
        )

    with col2:
        st.markdown("### Scan to Join")

        st.image(
            out.getvalue(),
            width="stretch",
            caption=f"QR Code for joining {subject_name}"
        )
