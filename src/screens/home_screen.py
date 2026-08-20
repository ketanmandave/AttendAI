import streamlit as st

from src.components.header import header_home
from src.components.footer import footer_home

from src.ui.base_layout import (
    style_background_home,
    style_base_layout,
)


def home_screen():

    style_background_home()
    style_base_layout()

    # Header
    header_home()

    # Page title
    st.html("""
        <div style="
            text-align: center;
            margin-bottom: 38px;
        ">
            <p style="
                display: inline-block;
                color: #67e8f9;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 3px;
                margin-bottom: 12px;
                background: rgba(6,182,212,0.12);
                border: 1px solid rgba(6,182,212,0.25);
                padding: 5px 16px;
                border-radius: 100px;
            ">
                ✦ &nbsp;GET STARTED &nbsp;✦
            </p>

            <h2 style="
                color: white;
                font-size: 34px;
                font-weight: 800;
                margin: 0 0 8px 0;
                letter-spacing: -0.8px;
                line-height: 1.1;
            ">
                Choose Your Portal
            </h2>

            <p style="
                color: #64748b;
                margin: 0;
                font-size: 15px;
                font-weight: 400;
            ">
                Select your role to continue with AttendIQ
            </p>
        </div>
        """)

    col1, gap, col2 = st.columns([1, 0.08, 1])

    # =====================================
    # Teacher Portal
    # =====================================

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
            key="teacher_portal",
            width="stretch",
        ):
            st.session_state["login_type"] = "teacher"
            st.rerun()

    # =====================================
    # Student Portal
    # =====================================

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
            key="student_portal",
            width="stretch",
        ):
            st.session_state["login_type"] = "student"
            st.rerun()

    # =====================================
    # Feature Section
    # =====================================

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
