import streamlit as st

from src.components.header import header_home
from src.components.footer import footer_home

from src.ui.base_layout import (
    style_background_home,
    style_base_layout,
)
from src.ui.product_theme import style_product_ui


def home_screen():

    style_background_home()
    style_base_layout()
    # UI REDESIGN: Final shared styling removes the legacy mixed visual themes.
    style_product_ui()

    # Header
    header_home()

    # Page title
    st.html("""
        <div class="ai-portal-intro">
            <p>CHOOSE YOUR WORKSPACE</p>
            <h2>Continue as teacher or student</h2>
            <span>Select the workspace that matches what you need to do.</span>
        </div>
        """)

    col1, gap, col2 = st.columns([1, 0.08, 1])

    # Teacher Portal
    with col1:

        st.html("""
            <div class="portal-card">

                <div style="overflow: hidden; border-radius: 24px 24px 0 0;">
                    <img
                        src="https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=1000&q=85"
                        class="portal-image"
                    >
                </div>

                <div class="portal-content">

                    <p class="portal-label">
                        FACULTY ACCESS
                    </p>

                    <h3>
                        Teacher Portal
                    </h3>

                    <p class="portal-description">
                        Manage attendance sessions, monitor students
                        and review attendance records.
                    </p>

                    <div class="portal-tags">

                        <span>
                            👥 Students
                        </span>

                        <span>
                            📊 Analytics
                        </span>

                        <span>
                            ✅ Records
                        </span>

                    </div>

                </div>

            </div>
            """)

        if st.button(
            "Open Teacher Portal →",
            type="primary",
            key="teacher_portal",
            width="stretch",
        ):
            st.session_state["login_type"] = "teacher"
            st.rerun()


    # Student Portal
    with col2:

        st.html("""
            <div class="portal-card">

                <div style="overflow: hidden; border-radius: 24px 24px 0 0;">
                    <img
                        src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1000&q=85"
                        class="portal-image"
                    >
                </div>

                <div class="portal-content">

                    <p class="portal-label">
                        STUDENT ACCESS
                    </p>

                    <h3>
                        Student Portal
                    </h3>

                    <p class="portal-description">
                        Verify your identity using face and voice
                        recognition and securely mark attendance.
                    </p>

                    <div class="portal-tags">

                        <span>
                            👤 Face ID
                        </span>

                        <span>
                            🎙️ Voice ID
                        </span>

                        <span>
                            🔐 Secure
                        </span>

                    </div>

                </div>

            </div>
            """)

        if st.button(
            "Open Student Portal →",
            type="primary",
            key="student_portal",
            width="stretch",
        ):
            st.session_state["login_type"] = "student"
            st.rerun()


    # Feature Section
    st.html("""
        <div class="feature-section">

            <h3>
                Why AttendIQ?
            </h3>

            <div class="feature-grid">

                <div class="feature-box">
                    <div class="feature-icon">👤</div>

                    <h4>
                        Face Recognition
                    </h4>

                    <p>
                        Identifies students accurately using advanced facial feature analysis.
                    </p>
                </div>


                <div class="feature-box">
                    <div class="feature-icon">🎙️</div>

                    <h4>
                        Voice Verification
                    </h4>

                    <p>
                        Adds an extra layer of biometric identity verification.
                    </p>
                </div>


                <div class="feature-box">
                    <div class="feature-icon">⚡</div>

                    <h4>
                        Fast Attendance
                    </h4>

                    <p>
                        Automatically records attendance for verified students instantly.
                    </p>
                </div>

            </div>

        </div>
        """)

    # Footer
    footer_home()
