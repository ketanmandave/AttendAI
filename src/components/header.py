import streamlit as st


def header_home():
    st.html(
        """
        <div class="ai-home-header">
            <div class="ai-brand-lockup">
                <div class="ai-brand-mark">A</div>
                <div>
                    <strong>AttendIQ</strong>
                    <span>Smart attendance management</span>
                </div>
            </div>
            <div class="ai-home-copy">
                <div class="ai-eyebrow">FACE + VOICE RECOGNITION</div>
                <h1>Attendance, without the admin overhead.</h1>
                <p>Secure identity verification and clear attendance records for modern classrooms.</p>
            </div>
        </div>
        <style>
        .ai-home-header { padding: 12px 0 30px; }
        .ai-brand-lockup { display:flex; align-items:center; gap:11px; }
        .ai-brand-mark { width:38px; height:38px; display:grid; place-items:center; border-radius:10px; background:#17201f; color:white; font-size:16px; font-weight:800; }
        .ai-brand-lockup strong { display:block; color:#17201f; font-size:17px; letter-spacing:-.4px; }
        .ai-brand-lockup span { display:block; margin-top:1px; color:#76807e; font-size:10px; }
        .ai-home-copy { max-width:700px; margin:52px auto 0; text-align:center; }
        .ai-eyebrow { margin-bottom:12px; color:#0f766e; font-size:10px; font-weight:800; letter-spacing:1.6px; }
        .ai-home-copy h1 { margin:0 0 12px!important; color:#17201f!important; font-size:42px!important; line-height:1.08!important; letter-spacing:-1.5px!important; }
        .ai-home-copy p { margin:0 auto!important; max-width:560px; color:#66706e!important; font-size:14px!important; line-height:1.6; }
        @media(max-width:700px) { .ai-home-copy{margin-top:34px}.ai-home-copy h1{font-size:31px!important} }
        </style>
        """
    )


def header_dashboard():
    st.html(
        """
        <div class="ai-dashboard-brand">
            <div class="ai-dashboard-mark">A</div>
            <div>
                <strong>AttendIQ</strong>
                <span>Attendance workspace</span>
            </div>
        </div>
        <style>
        .ai-dashboard-brand { display:flex; align-items:center; gap:10px; min-height:48px; }
        .ai-dashboard-mark { width:36px; height:36px; display:grid; place-items:center; border-radius:9px; background:#17201f; color:white; font-size:15px; font-weight:800; }
        .ai-dashboard-brand strong { display:block; color:#17201f; font-size:16px; letter-spacing:-.35px; }
        .ai-dashboard-brand span { display:block; margin-top:1px; color:#78817f; font-size:10px; }
        </style>
        """
    )
