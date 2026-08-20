import streamlit as st


def header_home():
    st.html(
        """
        <div style="text-align: center; margin-bottom: 36px; padding-top: 10px; position: relative;">

            <!-- Glow ring behind icon -->
            <div style="
                display: inline-block;
                width: 72px;
                height: 72px;
                border-radius: 50%;
                background: linear-gradient(135deg, #2563eb, #7c3aed);
                box-shadow: 0 0 0 12px rgba(37,99,235,0.12), 0 0 0 24px rgba(37,99,235,0.06);
                line-height: 72px;
                font-size: 32px;
                margin-bottom: 18px;
                animation: pulse-glow 3s ease-in-out infinite;
            ">
                🎯
            </div>

            <h1 style="
                color: white;
                font-size: 54px;
                font-weight: 900;
                margin: 0 0 4px 0;
                letter-spacing: -2px;
                line-height: 1.05;
                background: linear-gradient(135deg, #ffffff 0%, #93c5fd 50%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">
                AttendIQ
            </h1>

            <p style="
                color: #94a3b8;
                font-size: 16px;
                font-weight: 400;
                letter-spacing: 0.2px;
                margin: 0;
            ">
                Smart Face &amp; Voice Based Attendance System
            </p>

            <!-- Decorative divider -->
            <div style="
                margin: 22px auto 0;
                width: 80px;
                height: 3px;
                border-radius: 4px;
                background: linear-gradient(90deg, #2563eb, #7c3aed, #06b6d4);
            "></div>

        </div>

        <style>
            @keyframes pulse-glow {
                0%, 100% { box-shadow: 0 0 0 12px rgba(37,99,235,0.12), 0 0 0 24px rgba(37,99,235,0.06); }
                50%       { box-shadow: 0 0 0 16px rgba(37,99,235,0.18), 0 0 0 32px rgba(37,99,235,0.08); }
            }
        </style>
        """
    )

def header_dashboard():
        st.html(
            """
        <div style="text-align: center; margin-bottom: 36px; padding-top: 10px; position: relative;">

            <!-- Glow ring behind icon -->
            <div style="
                display: inline-block;
                width: 72px;
                height: 72px;
                border-radius: 50%;
                background: linear-gradient(135deg, #2563eb, #7c3aed);
                box-shadow: 0 0 0 12px rgba(37,99,235,0.12), 0 0 0 24px rgba(37,99,235,0.06);
                line-height: 72px;
                font-size: 32px;
                margin-bottom: 18px;
                animation: pulse-glow 3s ease-in-out infinite;
            ">
                🎯
            </div>

            <h1 style="
                color: white;
                font-size: 54px;
                font-weight: 900;
                margin: 0 0 4px 0;
                letter-spacing: -2px;
                line-height: 1.05;
                background: linear-gradient(135deg, #ffffff 0%, #93c5fd 50%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">
                AttendIQ
            </h1>

            <p style="
                color: #94a3b8;
                font-size: 16px;
                font-weight: 400;
                letter-spacing: 0.2px;
                margin: 0;
            ">
                Smart Face &amp; Voice Based Attendance System
            </p>

            <!-- Decorative divider -->
            <div style="
                margin: 22px auto 0;
                width: 80px;
                height: 3px;
                border-radius: 4px;
                background: linear-gradient(90deg, #2563eb, #7c3aed, #06b6d4);
            "></div>

        </div>

        <style>
            @keyframes pulse-glow {
                0%, 100% { box-shadow: 0 0 0 12px rgba(37,99,235,0.12), 0 0 0 24px rgba(37,99,235,0.06); }
                50%       { box-shadow: 0 0 0 16px rgba(37,99,235,0.18), 0 0 0 32px rgba(37,99,235,0.08); }
            }
        </style>
        """
)
