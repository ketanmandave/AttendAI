import streamlit as st

def load_fonts():

    st.html(
        """
        <link
            href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
            rel="stylesheet"
        >

        <style>

        /*
        IMPORTANT:
        Do NOT use:

            * {
                font-family: Inter !important;
            }

        because Streamlit uses special icon fonts internally.
        Applying Inter to every element can break those icons.
        */

        html,
        body,
        .stApp,
        .stMarkdown,
        .stButton,
        .stTextInput,
        .stSelectbox,
        .stNumberInput,
        .stTextArea,
        .stRadio,
        .stCheckbox {
            font-family: 'Inter', sans-serif;
        }

        </style>
        """
    )


# =========================================================
# HOME BACKGROUND
# =========================================================

def style_background_home():

    load_fonts()

    st.html(
        """
        <style>

        .stApp {
            background:
                radial-gradient(circle at 10% 0%, rgba(15, 118, 110, .07), transparent 30%),
                radial-gradient(circle at 95% 15%, rgba(180, 83, 9, .045), transparent 28%),
                #f7f7f5;
            min-height: 100vh;
        }

        </style>
        """
    )


# =========================================================
# DASHBOARD BACKGROUND
# =========================================================

def style_background_dashboard():

    load_fonts()

    st.html(
        """
        <style>

        .stApp {
            background: #f7f7f5;
            min-height: 100vh;
        }

        </style>
        """
    )

def style_professional_theme():
    """Final shared theme overrides for a compact, neutral product UI."""
    st.html(
        """
        <style>
        :root {
            --ai-ink: #17201f;
            --ai-muted: #66706e;
            --ai-line: #dfe3e1;
            --ai-surface: #ffffff;
            --ai-subtle: #f1f3f2;
            --ai-accent: #0f766e;
            --ai-accent-dark: #115e59;
            --ai-accent-soft: #e7f3f1;
            --ai-danger: #b42318;
        }

        .block-container {
            max-width: 1120px !important;
            padding-top: 18px !important;
            padding-bottom: 32px !important;
        }

        .stApp::before,
        .stApp::after { display: none !important; }

        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
        div[data-testid="stHeading"] h1,
        div[data-testid="stHeading"] h2,
        div[data-testid="stHeading"] h3,
        div[data-testid="stHeadingWithActionElements"] h3 {
            color: var(--ai-ink) !important;
            letter-spacing: -.025em !important;
        }

        .stMarkdown p, div[data-testid="stCaptionContainer"] p {
            color: var(--ai-muted) !important;
        }

        div.stButton > button {
            min-height: 40px !important;
            border-radius: 9px !important;
            border: 1px solid var(--ai-line) !important;
            background: var(--ai-surface) !important;
            color: #34403e !important;
            font-size: 13px !important;
            font-weight: 650 !important;
            letter-spacing: 0 !important;
            box-shadow: 0 1px 2px rgba(23, 32, 31, .05) !important;
            transform: none !important;
        }

        div.stButton > button::before { display: none !important; }

        div.stButton > button[kind="primary"] {
            border-color: var(--ai-accent) !important;
            background: var(--ai-accent) !important;
            color: #ffffff !important;
            box-shadow: 0 1px 2px rgba(15, 118, 110, .18) !important;
        }

        div.stButton > button[kind="primary"]:hover {
            border-color: var(--ai-accent-dark) !important;
            background: var(--ai-accent-dark) !important;
        }

        div.stButton > button[kind="secondary"]:hover {
            border-color: #aeb7b4 !important;
            background: #f8f9f8 !important;
            color: var(--ai-ink) !important;
        }

        div.stButton > button[kind="tertiary"] {
            border-color: transparent !important;
            background: transparent !important;
            color: #52605d !important;
            box-shadow: none !important;
        }

        div.stButton > button:disabled {
            border-color: #e2e5e4 !important;
            background: #eef0ef !important;
            color: #9ba3a1 !important;
            opacity: 1 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 20px 22px !important;
            border: 1px solid var(--ai-line) !important;
            border-radius: 13px !important;
            background: rgba(255, 255, 255, .96) !important;
            box-shadow: 0 2px 8px rgba(23, 32, 31, .035) !important;
        }

        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] {
            border-color: #cfd5d3 !important;
            border-radius: 9px !important;
            background: #ffffff !important;
            box-shadow: none !important;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="textarea"]:focus-within {
            border-color: var(--ai-accent) !important;
            box-shadow: 0 0 0 3px rgba(15, 118, 110, .10) !important;
        }

        div[data-testid="stFileUploaderDropzone"] {
            min-height: 92px !important;
            padding: 14px !important;
            border: 1px dashed #b9c2bf !important;
            border-radius: 10px !important;
            background: #fafbfa !important;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            border: 1px solid var(--ai-line);
            border-radius: 10px;
            overflow: hidden;
        }

        div[data-testid="stMetric"] {
            padding: 12px 14px;
            border: 1px solid var(--ai-line);
            border-radius: 10px;
            background: var(--ai-surface);
        }

        div[data-testid="stAlert"] {
            border-radius: 10px !important;
            border-width: 1px !important;
            box-shadow: none !important;
        }

        hr {
            margin: 14px 0 !important;
            background: var(--ai-line) !important;
        }

        div[data-testid="stDialog"] [role="dialog"] {
            max-width: 680px !important;
            max-height: min(84vh, 760px) !important;
            overflow-y: auto !important;
            overscroll-behavior: contain;
            border: 1px solid #d7dcda !important;
            border-radius: 14px !important;
            background: #ffffff !important;
            box-shadow: 0 18px 50px rgba(23, 32, 31, .16) !important;
        }

        div[data-testid="stDialog"] [role="dialog"] > div {
            padding: 18px 20px !important;
        }

        div[data-testid="stDialog"] h2 {
            font-size: 19px !important;
            color: var(--ai-ink) !important;
        }

        div[data-baseweb="tab-highlight"] { background-color:var(--ai-accent)!important; }
        div[data-baseweb="tab-border"] { background-color:var(--ai-line)!important; }

        .ai-portal-intro { margin: 4px 0 24px; text-align:center; }
        .ai-portal-intro p { margin:0 0 6px!important; color:var(--ai-accent)!important; font-size:9px!important; font-weight:800; letter-spacing:1.5px; }
        .ai-portal-intro h2 { margin:0 0 5px!important; color:var(--ai-ink)!important; font-size:23px!important; letter-spacing:-.5px!important; }
        .ai-portal-intro span { color:var(--ai-muted); font-size:12px; }

        .portal-card {
            border:1px solid var(--ai-line)!important;
            border-radius:14px!important;
            background:#ffffff!important;
            box-shadow:0 2px 10px rgba(23,32,31,.04)!important;
            margin-bottom:10px!important;
        }
        .portal-card:hover { transform:translateY(-2px)!important; border-color:#b9c5c2!important; box-shadow:0 8px 20px rgba(23,32,31,.07)!important; }
        .portal-image { height:168px!important; filter:saturate(.78) contrast(.96)!important; }
        .portal-card:hover .portal-image { transform:none!important; filter:saturate(.86)!important; }
        .portal-content { padding:18px 20px 20px!important; }
        .portal-label { margin-bottom:6px!important; color:var(--ai-accent)!important; font-size:9px!important; letter-spacing:1.4px!important; }
        .portal-content h3 { margin-bottom:7px!important; color:var(--ai-ink)!important; font-size:19px!important; }
        .portal-description { margin-bottom:14px!important; color:var(--ai-muted)!important; font-size:11px!important; line-height:1.55!important; }
        .portal-tags { gap:6px!important; }
        .portal-tags span { padding:4px 8px!important; border:1px solid #d6dfdc!important; background:#f5f7f6!important; color:#52605d!important; font-size:9px!important; }

        .feature-section { margin-top:30px!important; padding:24px!important; border:1px solid var(--ai-line)!important; border-radius:14px!important; background:#ffffff!important; backdrop-filter:none!important; }
        .feature-section h3 { margin-bottom:18px!important; color:var(--ai-ink)!important; font-size:18px!important; }
        .feature-grid { gap:10px!important; }
        .feature-box { padding:17px 14px!important; border:1px solid #e5e8e7!important; border-radius:10px!important; background:#fafbfa!important; }
        .feature-box:hover { transform:none!important; border-color:#cbd3d1!important; background:#f7f9f8!important; }
        .feature-icon { margin-bottom:8px!important; font-size:22px!important; filter:grayscale(.2); }
        .feature-box h4 { color:var(--ai-ink)!important; font-size:12px!important; }
        .feature-box p { color:var(--ai-muted)!important; font-size:10px!important; }

        .teacher-auth-heading { margin-top:16px!important; margin-bottom:18px!important; padding:18px 20px!important; border:1px solid var(--ai-line)!important; border-radius:13px!important; background:#ffffff!important; box-shadow:0 2px 8px rgba(23,32,31,.035)!important; }
        .teacher-auth-icon { width:46px!important; height:46px!important; border-radius:10px!important; background:#17201f!important; box-shadow:none!important; font-size:21px!important; }
        .teacher-auth-label { color:var(--ai-accent)!important; }
        .teacher-auth-heading h2 { color:var(--ai-ink)!important; font-size:23px!important; }
        .teacher-auth-heading p:last-child { color:var(--ai-muted)!important; }
        .teacher-auth-info { margin-top:14px!important; gap:10px!important; }
        .teacher-auth-info > div { padding:13px!important; border-color:var(--ai-line)!important; border-radius:10px!important; background:#fff!important; box-shadow:none!important; }

        ::-webkit-scrollbar-thumb { background: #b9c1bf !important; }

        @media (max-width: 768px) {
            .block-container { padding: 12px 14px 24px !important; }
            div[data-testid="stVerticalBlockBorderWrapper"] > div {
                padding: 16px !important;
            }
        }
        </style>
        """
    )

# =========================================================
# BASE LAYOUT
# =========================================================

def style_base_layout():

    st.html(
        """
        <style>

        /* =================================================
           STREAMLIT DEFAULT ELEMENTS
        ================================================= */

        #MainMenu {
            visibility: hidden;
        }

        header {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }


        .block-container {

            max-width: 1100px;

            padding-top: 22px;
            padding-bottom: 45px;

            position: relative;

            z-index: 1;
        }


        /* =================================================
           DECORATIVE BACKGROUND
        ================================================= */

        .stApp::before {

            content: '';

            position: fixed;

            width: 550px;
            height: 550px;

            top: -220px;
            right: -180px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(59, 130, 246, 0.12),
                    transparent 70%
                );

            pointer-events: none;

            z-index: 0;

            animation:
                attendIQFloat 9s
                ease-in-out
                infinite;
        }


        .stApp::after {

            content: '';

            position: fixed;

            width: 420px;
            height: 420px;

            left: -150px;
            bottom: -130px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(139, 92, 246, 0.12),
                    transparent 70%
                );

            pointer-events: none;

            z-index: 0;

            animation:
                attendIQFloat 11s
                ease-in-out
                infinite reverse;
        }


        @keyframes attendIQFloat {

            0%,
            100% {
                transform:
                    translateY(0)
                    scale(1);
            }

            50% {
                transform:
                    translateY(-25px)
                    scale(1.04);
            }
        }


        /* =================================================
           HOME PORTAL CARDS
        ================================================= */

        .portal-card {

            position: relative;

            overflow: hidden;

            border-radius: 24px;

            border:
                1px solid
                rgba(255, 255, 255, 0.12);

            background:
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.07),
                    rgba(255, 255, 255, 0.025)
                );

            backdrop-filter:
                blur(20px);

            -webkit-backdrop-filter:
                blur(20px);

            box-shadow:
                0 10px 35px
                rgba(0, 0, 0, 0.25);

            transition:
                transform .3s ease,
                border-color .3s ease,
                box-shadow .3s ease;

            margin-bottom: 14px;
        }


        .portal-card:hover {

            transform:
                translateY(-6px);

            border-color:
                rgba(96, 165, 250, 0.35);

            box-shadow:
                0 22px 55px
                rgba(0, 0, 0, 0.35);
        }


        .portal-image {

            width: 100%;
            height: 220px;

            display: block;

            object-fit: cover;

            border-radius: 0 !important;

            filter:
                brightness(.88)
                saturate(1.08);

            transition:
                transform .4s ease,
                filter .4s ease;
        }


        .portal-card:hover .portal-image {

            transform:
                scale(1.035);

            filter:
                brightness(.95)
                saturate(1.12);
        }


        .portal-content {

            padding:
                24px 26px 27px;
        }


        .portal-label {

            margin:
                0 0 8px 0 !important;

            color:
                #67e8f9 !important;

            font-size:
                10px !important;

            font-weight:
                700 !important;

            letter-spacing:
                2.5px;
        }


        .portal-content h3 {

            margin:
                0 0 10px 0 !important;

            color:
                #ffffff !important;

            font-size:
                23px !important;

            font-weight:
                700 !important;
        }


        .portal-description {

            margin:
                0 0 18px 0 !important;

            color:
                #94a3b8 !important;

            font-size:
                13px !important;

            line-height:
                1.65;
        }


        .portal-tags {

            display: flex;

            flex-wrap: wrap;

            gap: 8px;
        }


        .portal-tags span {

            padding:
                5px 11px;

            border-radius:
                100px;

            border:
                1px solid
                rgba(59, 130, 246, .28);

            background:
                rgba(59, 130, 246, .13);

            color:
                #bfdbfe;

            font-size:
                10px;

            font-weight:
                600;
        }


        /* =================================================
           HOME FEATURES
        ================================================= */

        .feature-section {

            margin-top:
                50px;

            padding:
                36px 40px;

            border-radius:
                26px;

            border:
                1px solid
                rgba(255, 255, 255, .09);

            background:
                rgba(255, 255, 255, .035);

            backdrop-filter:
                blur(20px);
        }


        .feature-section h3 {

            margin:
                0 0 28px 0 !important;

            text-align:
                center;

            color:
                white !important;

            font-size:
                22px !important;
        }


        .feature-grid {

            display: grid;

            grid-template-columns:
                repeat(3, 1fr);

            gap:
                18px;
        }


        .feature-box {

            padding:
                24px 20px;

            text-align:
                center;

            border-radius:
                18px;

            border:
                1px solid
                rgba(255, 255, 255, .08);

            background:
                rgba(255, 255, 255, .035);

            transition:
                .25s ease;
        }


        .feature-box:hover {

            transform:
                translateY(-3px);

            border-color:
                rgba(59, 130, 246, .25);

            background:
                rgba(59, 130, 246, .07);
        }


        .feature-icon {

            margin-bottom:
                12px;

            font-size:
                30px;
        }


        .feature-box h4 {

            margin:
                0 0 7px 0 !important;

            color:
                white !important;

            font-size:
                14px !important;
        }


        .feature-box p {

            margin:
                0 !important;

            color:
                #94a3b8 !important;

            font-size:
                12px !important;

            line-height:
                1.55;
        }


        /* =================================================
           STREAMLIT BUTTONS — PREMIUM GRADIENT
        ================================================= */

        div.stButton > button {

            position: relative;
            overflow: hidden;

            min-height: 46px;
            border-radius: 12px;
            border: none !important;

            background: linear-gradient(
                135deg,
                #2563eb 0%,
                #3b82f6 50%,
                #1d4ed8 100%
            ) !important;

            color: white !important;

            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: 0.2px;

            box-shadow:
                0 4px 18px rgba(37, 99, 235, 0.38),
                inset 0 1px 0 rgba(255, 255, 255, 0.18);

            transition:
                transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
                box-shadow 0.25s ease,
                background 0.25s ease;
        }

        /* Shimmer sweep on hover */
        div.stButton > button::before {

            content: '';
            position: absolute;
            top: 0; left: -75%;
            width: 50%; height: 100%;

            background: linear-gradient(
                120deg,
                transparent 0%,
                rgba(255,255,255,0.22) 50%,
                transparent 100%
            );

            transform: skewX(-20deg);
            transition: left 0.55s ease;
            pointer-events: none;
        }

        div.stButton > button:hover::before {
            left: 130%;
        }

        div.stButton > button:hover {

            transform: translateY(-2px) scale(1.01);

            box-shadow:
                0 8px 28px rgba(37, 99, 235, 0.55),
                inset 0 1px 0 rgba(255, 255, 255, 0.22);

            background: linear-gradient(
                135deg,
                #1d4ed8 0%,
                #2563eb 50%,
                #1e40af 100%
            ) !important;
        }

        div.stButton > button:active {
            transform: translateY(0px) scale(0.98) !important;
            box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3) !important;
        }


        /* =================================================
           STREAMLIT MARKDOWN — HEADERS & DIVIDERS
        ================================================= */

        /* h1 inside markdown */
        .stMarkdown h1 {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.6px;
            color: #0f172a;
        }

        /* h2 */
        .stMarkdown h2,
        div[data-testid="stHeading"] h2 {
            font-size: 22px;
            font-weight: 700;
            letter-spacing: -0.4px;
            color: #1e293b;
        }

        /* h3 / subheader */
        .stMarkdown h3,
        div[data-testid="stHeading"] h3 {
            font-size: 18px;
            font-weight: 700;
            color: #1e293b;
        }

        /* h4 used for form section titles */
        .stMarkdown h4 {
            font-size: 15px;
            font-weight: 700;
            color: #334155;
            margin: 0 0 14px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }

        /* Caption text */
        div[data-testid="stCaptionContainer"] p {
            color: #64748b !important;
            font-size: 13px !important;
        }

        /* Divider */
        hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(
                90deg,
                transparent,
                #cbd5e1 20%,
                #cbd5e1 80%,
                transparent
            ) !important;
            margin: 18px 0 !important;
        }


        /* =================================================
           STREAMLIT CONTAINER (border=True)
        ================================================= */

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            border-radius: 18px !important;
            border: 1.5px solid #e2e8f0 !important;
            background: rgba(255,255,255,0.96) !important;
            box-shadow:
                0 4px 24px rgba(15, 23, 42, 0.06),
                0 1px 4px rgba(15, 23, 42, 0.04) !important;
            padding: 28px 28px 24px !important;
        }


        /* =================================================
           STREAMLIT st.subheader
        ================================================= */

        div[data-testid="stHeadingWithActionElements"] h3 {
            font-size: 20px !important;
            font-weight: 800 !important;
            color: #0f172a !important;
            letter-spacing: -0.4px !important;
        }


        /* =================================================
           SCROLLBAR
        ================================================= */

        ::-webkit-scrollbar {
            width: 5px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(100, 116, 139, 0.3);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(37, 99, 235, 0.45);
        }


        /* =================================================
           RESPONSIVE
        ================================================= */

        @media (max-width: 768px) {

            .block-container {
                padding-left: 16px;
                padding-right: 16px;
            }

            .feature-grid {
                grid-template-columns: 1fr;
            }

            .feature-section {
                padding: 28px 20px;
            }

            div.stButton > button {
                font-size: 13px;
                min-height: 42px;
            }
        }

        </style>
        """
    )

    style_professional_theme()


# =========================================================
# TEACHER LOGIN / REGISTER
# =========================================================

def style_teacher_auth():

    st.html(
        """
        <style>

        /* Keep authentication focused and readable on wide screens. This
           style is loaded only for login/register, never for the dashboard. */
        .block-container {
            max-width: 780px !important;
            margin-inline: auto !important;
        }

        /* =================================================
           AUTH PAGE HEADER
        ================================================= */

        .teacher-auth-heading {

            display:
                flex;

            align-items:
                center;

            gap:
                16px;

            margin-top:
                28px;

            margin-bottom:
                26px;

            padding:
                22px 24px;

            border-radius:
                18px;

            border:
                1px solid
                rgba(37, 99, 235, .12);

            background:
                linear-gradient(
                    135deg,
                    rgba(37, 99, 235, .09),
                    rgba(99, 102, 241, .05)
                );

            box-shadow:
                0 10px 30px
                rgba(15, 23, 42, .035);
        }


        .teacher-auth-icon {

            flex-shrink:
                0;

            width:
                56px;

            height:
                56px;

            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            border-radius:
                15px;

            font-size:
                26px;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #4f46e5
                );

            box-shadow:
                0 10px 25px
                rgba(37, 99, 235, .20);
        }


        .teacher-auth-label {

            margin:
                0 0 4px 0 !important;

            color:
                #2563eb !important;

            font-size:
                10px !important;

            font-weight:
                700 !important;

            letter-spacing:
                1.7px;
        }


        .teacher-auth-heading h2 {

            margin:
                0 !important;

            color:
                #0f172a !important;

            font-size:
                27px !important;

            font-weight:
                750 !important;

            line-height:
                1.2;
        }


        .teacher-auth-heading p:last-child {

            margin:
                6px 0 0 0 !important;

            color:
                #64748b !important;

            font-size:
                13px !important;
        }


        /* =================================================
           FORM CONTAINER
        ================================================= */

        div[data-testid="stVerticalBlockBorderWrapper"] {

            border-radius:
                18px !important;

            border:
                1px solid
                #dce5f2 !important;

            background:
                rgba(
                    255,
                    255,
                    255,
                    .92
                ) !important;

            box-shadow:
                0 18px 50px
                rgba(
                    15,
                    23,
                    42,
                    .06
                );

            overflow:
                hidden;
        }


        /* =================================================
           INPUT LABEL
        ================================================= */

        div[data-testid="stTextInput"] label {

            color:
                #334155 !important;

            font-family:
                'Inter',
                sans-serif !important;

            font-size:
                13px !important;

            font-weight:
                600 !important;
        }


        /* =================================================
           INPUT FIELD
        ================================================= */

        div[data-testid="stTextInput"] input {

            height:
                44px;

            border-radius:
                10px;

            color:
                #0f172a !important;

            background:
                #ffffff !important;

            font-family:
                'Inter',
                sans-serif !important;

            font-size:
                13px !important;
        }


        div[data-testid="stTextInput"] input::placeholder {

            color:
                #94a3b8 !important;

            opacity:
                1;
        }


        /*
        Style the actual input wrapper instead of forcing
        borders directly onto every nested element.
        */

        div[data-testid="stTextInput"] div[data-baseweb="input"] {

            border-radius:
                10px !important;

            background:
                #ffffff !important;

            border:
                1px solid
                #cbd5e1 !important;

            box-shadow:
                none !important;

            transition:
                border-color .2s ease,
                box-shadow .2s ease;
        }


        div[data-testid="stTextInput"]
        div[data-baseweb="input"]:focus-within {

            border-color:
                #2563eb !important;

            box-shadow:
                0 0 0 3px
                rgba(
                    37,
                    99,
                    235,
                    .10
                ) !important;
        }


        /* =================================================
           PASSWORD VISIBILITY BUTTON

           You asked to remove it completely.
        ================================================= */

        div[data-testid="stTextInput"] button {

            display:
                none !important;
        }


        /*
        Prevent the password input from keeping unnecessary
        space after the eye button is removed.
        */

        div[data-testid="stTextInput"] input[type="password"] {

            padding-right:
                12px !important;
        }


        /* =================================================
           AUTH BUTTONS
        ================================================= */

        div.stButton > button {

            min-height:
                46px;

            border-radius:
                10px;

            font-family:
                'Inter',
                sans-serif !important;

            font-size:
                13px;

            font-weight:
                600;

            transition:
                transform .2s ease,
                box-shadow .2s ease;
        }


        div.stButton > button:hover {

            transform:
                translateY(-1px);
        }


        /* =================================================
           AUTH INFORMATION CARDS
        ================================================= */

        .teacher-auth-info {

            display:
                grid;

            grid-template-columns:
                repeat(2, 1fr);

            gap:
                14px;

            margin-top:
                22px;
        }


        .teacher-auth-info > div {

            display:
                flex;

            align-items:
                flex-start;

            gap:
                12px;

            padding:
                16px;

            border-radius:
                14px;

            border:
                1px solid
                #e2e8f0;

            background:
                rgba(
                    255,
                    255,
                    255,
                    .82
                );

            box-shadow:
                0 8px 25px
                rgba(
                    15,
                    23,
                    42,
                    .035
                );
        }


        .teacher-auth-info span {

            font-size:
                20px;
        }


        .teacher-auth-info strong {

            color:
                #0f172a;

            font-size:
                12px;

            font-weight:
                700;
        }


        .teacher-auth-info p {

            margin:
                4px 0 0 0;

            color:
                #64748b;

            font-size:
                10px;

            line-height:
                1.55;
        }


        /* =================================================
           MOBILE
        ================================================= */

        @media (max-width: 768px) {

            .block-container {
                max-width: 100% !important;
            }

            .teacher-auth-heading {

                padding:
                    18px;
            }


            .teacher-auth-icon {

                width:
                    48px;

                height:
                    48px;

                font-size:
                    22px;
            }


            .teacher-auth-heading h2 {

                font-size:
                    22px !important;
            }


            .teacher-auth-info {

                grid-template-columns:
                    1fr;
            }
        }

        /* Professional neutral/teal finish for the teacher portal. */
        .teacher-auth-heading {
            margin-top: 14px;
            margin-bottom: 18px;
            padding: 18px 20px;
            border: 1px solid #d7dcda;
            border-radius: 14px;
            background: #ffffff;
            box-shadow: 0 2px 12px rgba(23, 32, 31, .04);
        }

        .teacher-auth-icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            background: #17201f;
            box-shadow: none;
        }

        .teacher-auth-label {
            color: #0f766e !important;
        }

        .teacher-auth-heading h2,
        .teacher-auth-info strong {
            color: #17201f !important;
        }

        .teacher-auth-heading p:last-child,
        .teacher-auth-info p {
            color: #64706d !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #d7dcda !important;
            border-radius: 14px !important;
            background: #ffffff !important;
            box-shadow: 0 4px 18px rgba(23, 32, 31, .05) !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
            border-color: #0f766e !important;
            box-shadow: 0 0 0 3px rgba(15, 118, 110, .10) !important;
        }

        .teacher-auth-info {
            margin-top: 16px;
            gap: 10px;
        }

        .teacher-auth-info > div {
            padding: 13px 14px;
            border: 1px solid #dfe4e2;
            border-radius: 12px;
            box-shadow: none;
        }

        </style>
        """
    )
