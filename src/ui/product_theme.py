"""Final AttendIQ visual system shared by every user-facing screen."""

import streamlit as st


def style_product_ui():
    """Apply the final institutional theme after legacy component styles."""
    st.html(
        """
        <style>
        :root {
            --iq-bg: #f8fafc;
            --iq-surface: #ffffff;
            --iq-surface-muted: #f1f5f4;
            --iq-text: #0f172a;
            --iq-muted: #64748b;
            --iq-border: #e2e8f0;
            --iq-primary: #0f766e;
            --iq-primary-dark: #115e59;
            --iq-primary-soft: #ecf7f5;
            --iq-success: #15803d;
            --iq-success-soft: #f0fdf4;
            --iq-warning: #b45309;
            --iq-warning-soft: #fffbeb;
            --iq-danger: #b91c1c;
            --iq-danger-soft: #fef2f2;
        }

        .stApp {
            background: var(--iq-bg) !important;
            color: var(--iq-text) !important;
        }
        .stApp::before, .stApp::after { display: none !important; }
        .block-container {
            max-width: 1200px !important;
            padding: 20px 24px 38px !important;
        }

        h1, h2, h3, h4, h5, h6 { color: var(--iq-text) !important; }
        label, div[data-testid="stCaptionContainer"] { color: var(--iq-muted); }

        div.stButton > button,
        div[data-testid="stDownloadButton"] > button {
            min-height: 44px !important;
            border-radius: 9px !important;
            border: 1px solid var(--iq-border) !important;
            background: var(--iq-surface) !important;
            color: #334155 !important;
            font-size: 13px !important;
            font-weight: 650 !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, .04) !important;
            transform: none !important;
        }
        div.stButton > button[kind="primary"] {
            border-color: var(--iq-primary) !important;
            background: var(--iq-primary) !important;
            color: white !important;
        }
        div.stButton > button[kind="primary"] p,
        div.stButton > button[kind="primary"] span,
        div.stButton > button[kind="primary"] svg,
        button[data-testid="stBaseButton-primary"] p,
        button[data-testid="stBaseButton-primary"] span,
        button[data-testid="stBaseButton-primary"] span[data-testid="stIconMaterial"],
        button[kind="primary"] div[data-testid="stMarkdownContainer"] p,
        div.stButton > button[kind="primary"] * {
            color: white !important;
            fill: currentColor !important;
        }
        div.stButton > button[kind="primary"]:hover {
            border-color: var(--iq-primary-dark) !important;
            background: var(--iq-primary-dark) !important;
        }
        div.stButton > button[kind="tertiary"] {
            border-color: transparent !important;
            background: transparent !important;
            box-shadow: none !important;
        }
        div.stButton > button:disabled,
        div.stButton > button[kind="primary"]:disabled {
            border-color: #e2e8f0 !important;
            background: #eef2f1 !important;
            color: #94a3b8 !important;
            box-shadow: none !important;
        }
        div.stButton > button:disabled p,
        div.stButton > button:disabled span,
        div.stButton > button:disabled svg,
        div.stButton > button:disabled * {
            color: #94a3b8 !important;
            fill: currentColor !important;
        }
        div.stButton > button:focus-visible,
        div[data-testid="stDownloadButton"] > button:focus-visible {
            outline: 3px solid rgba(15, 118, 110, .22) !important;
            outline-offset: 2px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 20px !important;
            border: 1px solid var(--iq-border) !important;
            border-radius: 12px !important;
            background: var(--iq-surface) !important;
            box-shadow: 0 1px 3px rgba(15, 23, 42, .035) !important;
        }
        div[data-testid="stMetric"] {
            min-height: 96px;
            padding: 15px 16px !important;
            border: 1px solid var(--iq-border) !important;
            border-radius: 11px !important;
            background: var(--iq-surface) !important;
        }
        div[data-testid="stMetricLabel"] { color: var(--iq-muted) !important; }
        div[data-testid="stMetricValue"] { color: var(--iq-text) !important; }

        div[data-baseweb="input"], div[data-baseweb="textarea"],
        div[data-baseweb="select"] > div {
            min-height: 44px !important;
            border-radius: 9px !important;
            border-color: #cbd5e1 !important;
            background: white !important;
            box-shadow: none !important;
        }
        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="textarea"]:focus-within,
        div[data-baseweb="select"] > div:focus-within {
            border-color: var(--iq-primary) !important;
            box-shadow: 0 0 0 3px rgba(15, 118, 110, .10) !important;
        }
        div[data-testid="stFileUploaderDropzone"] {
            border: 1px dashed #94a3b8 !important;
            border-radius: 10px !important;
            background: #f8fafc !important;
        }
        div[data-testid="stDataFrame"], div[data-testid="stTable"] {
            border: 1px solid var(--iq-border) !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }
        div[data-testid="stAlert"] {
            border-radius: 10px !important;
            box-shadow: none !important;
        }
        hr { margin: 18px 0 !important; background: var(--iq-border) !important; }

        div[data-testid="stDialog"] [role="dialog"] {
            width: min(720px, calc(100vw - 32px)) !important;
            max-width: 720px !important;
            max-height: 86vh !important;
            overflow-y: auto !important;
            border: 1px solid var(--iq-border) !important;
            border-radius: 14px !important;
            background: white !important;
            box-shadow: 0 24px 60px rgba(15, 23, 42, .18) !important;
        }

        .iq-page-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 22px;
        }
        .iq-eyebrow {
            margin-bottom: 5px;
            color: var(--iq-primary);
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.35px;
            text-transform: uppercase;
        }
        .iq-page-header h1 {
            margin: 0 0 5px !important;
            font-size: 27px !important;
            line-height: 1.2 !important;
            letter-spacing: -.7px !important;
        }
        .iq-page-header p { margin: 0 !important; font-size: 13px; }

        .iq-nav-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            padding-bottom: 18px;
            margin-bottom: 10px;
            border-bottom: 1px solid var(--iq-border);
        }
        .iq-nav-mark {
            width: 38px; height: 38px; display: grid; place-items: center;
            border-radius: 9px; color: white; background: #17201f;
            font-size: 15px; font-weight: 800;
        }
        .iq-nav-brand strong { display: block; color: var(--iq-text); font-size: 15px; }
        .iq-nav-brand span { color: var(--iq-muted); font-size: 9px; }
        .iq-user-card {
            margin-top: 16px; padding: 12px; border-radius: 9px;
            background: var(--iq-surface-muted);
        }
        .iq-user-card span { display: block; color: var(--iq-muted); font-size: 9px; text-transform: uppercase; letter-spacing: .8px; }
        .iq-user-card strong { display: block; margin-top: 3px; color: var(--iq-text); font-size: 12px; }

        .iq-workflow {
            display: grid; grid-template-columns: repeat(4, 1fr);
            margin: 0 0 20px; overflow: hidden;
            border: 1px solid var(--iq-border); border-radius: 11px; background: white;
        }
        .iq-step { position: relative; padding: 13px 12px; border-right: 1px solid var(--iq-border); }
        .iq-step:last-child { border-right: 0; }
        .iq-step span { display: block; color: #94a3b8; font-size: 9px; font-weight: 800; letter-spacing: .8px; }
        .iq-step strong { display: block; margin-top: 3px; color: #64748b; font-size: 11px; }
        .iq-step.active { background: var(--iq-primary-soft); }
        .iq-step.active span, .iq-step.active strong { color: var(--iq-primary); }
        .iq-step.done span, .iq-step.done strong { color: var(--iq-success); }

        .iq-success-panel {
            padding: 24px; margin-bottom: 18px; border: 1px solid #bbf7d0;
            border-radius: 12px; background: var(--iq-success-soft);
        }
        .iq-success-panel strong { display: block; color: var(--iq-success); font-size: 17px; }
        .iq-success-panel span { display: block; margin-top: 5px; color: #3f6750; font-size: 12px; }

        .iq-student-overview {
            padding: 24px; margin-bottom: 16px; border: 1px solid #cfe3df;
            border-radius: 13px; background: linear-gradient(135deg, #ffffff, #f0f7f5);
        }
        .iq-student-overview h1 { margin: 0 0 5px !important; font-size: 25px !important; }
        .iq-student-overview p { margin: 0 !important; font-size: 12px; }
        .iq-overall-score { margin-top: 20px; display: flex; align-items: baseline; gap: 9px; }
        .iq-overall-score strong { color: var(--iq-text); font-size: 38px; line-height: 1; }
        .iq-overall-score span { color: var(--iq-muted); font-size: 12px; }
        .iq-progress { height: 7px; margin-top: 13px; overflow: hidden; border-radius: 999px; background: #e2e8f0; }
        .iq-progress > span { display: block; height: 100%; border-radius: inherit; background: var(--iq-primary); }

        .iq-subject-card {
            min-height: 184px; padding: 18px; margin-bottom: 10px;
            border: 1px solid var(--iq-border); border-radius: 11px; background: white;
        }
        .iq-subject-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
        .iq-subject-card h3 { margin: 0 0 4px !important; color: var(--iq-text) !important; font-size: 16px !important; }
        .iq-subject-meta { color: var(--iq-muted); font-size: 10px; }
        .iq-status-badge { padding: 4px 8px; border-radius: 999px; font-size: 9px; font-weight: 750; white-space: nowrap; }
        .iq-status-good { color: var(--iq-success); background: var(--iq-success-soft); }
        .iq-status-risk { color: var(--iq-danger); background: var(--iq-danger-soft); }
        .iq-status-neutral { color: #475569; background: #f1f5f9; }
        .iq-subject-stats { display: flex; gap: 18px; margin-top: 17px; }
        .iq-subject-stat span { display: block; color: var(--iq-muted); font-size: 9px; text-transform: uppercase; letter-spacing: .6px; }
        .iq-subject-stat strong { display: block; margin-top: 3px; color: var(--iq-text); font-size: 14px; }
        .iq-subject-card .iq-progress { margin-top: 16px; }
        .iq-subject-progress-label { display: flex; justify-content: space-between; margin-top: 7px; color: var(--iq-muted); font-size: 9px; }

        .portal-card, .feature-section {
            border: 1px solid var(--iq-border) !important;
            border-radius: 12px !important;
            background: white !important;
            box-shadow: 0 1px 4px rgba(15, 23, 42, .04) !important;
            backdrop-filter: none !important;
        }
        .portal-card:hover { transform: none !important; border-color: #b6c8c4 !important; box-shadow: 0 5px 16px rgba(15, 23, 42, .07) !important; }
        .portal-image { height: 156px !important; filter: saturate(.65) contrast(.96) !important; }
        .feature-section { padding: 22px !important; }

        @media (max-width: 760px) {
            .block-container { padding: 14px 14px 28px !important; }
            .iq-page-header { margin-bottom: 17px; }
            .iq-page-header h1 { font-size: 23px !important; }
            .iq-workflow { grid-template-columns: repeat(2, 1fr); }
            .iq-step:nth-child(2) { border-right: 0; }
            .iq-step:nth-child(-n+2) { border-bottom: 1px solid var(--iq-border); }
            .iq-student-overview { padding: 20px 18px; }
            .iq-overall-score strong { font-size: 32px; }
            div[data-testid="stHorizontalBlock"] { gap: .65rem !important; }
        }
        </style>
        """
    )


def page_header(eyebrow, title, description):
    st.html(
        f"""
        <div class="iq-page-header">
            <div>
                <div class="iq-eyebrow">{eyebrow}</div>
                <h1>{title}</h1>
                <p>{description}</p>
            </div>
        </div>
        """
    )


def attendance_workflow(active_step):
    labels = (("01", "Select class"), ("02", "Add evidence"),
              ("03", "Review results"), ("04", "Save"))
    steps = []
    for index, (number, label) in enumerate(labels, start=1):
        state = "active" if index == active_step else "done" if index < active_step else ""
        steps.append(
            f'<div class="iq-step {state}"><span>{number}</span><strong>{label}</strong></div>'
        )
    st.html('<div class="iq-workflow">' + "".join(steps) + "</div>")
