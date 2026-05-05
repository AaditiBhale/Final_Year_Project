from __future__ import annotations

import os

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:5000")

st.set_page_config(
    page_title="Manufacturing AI Platform",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #f4f7fb 0%, #eaf0f7 52%, #dfe8f2 100%);
        color: #1e2a37;
    }
    html, body, [class*="css"] {
        font-family: "Inter", sans-serif;
        color: #1e2a37;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1200px;
    }
    h1, h2, h3 {
        color: #1f2f43 !important;
    }
    h1 {
        font-family: "Playfair Display", serif;
        font-size: 2.6rem !important;
        margin-bottom: 0.2rem;
    }
    p, label, div, span, li, a {
        color: #243447 !important;
    }
    .hero-card {
        background: rgba(250, 253, 255, 0.97);
        border: 1px solid #d4e0ec;
        border-radius: 20px;
        padding: 1.25rem 1.2rem;
        box-shadow: 0 12px 26px rgba(48, 77, 107, 0.10);
        margin-bottom: 0.4rem;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #1e2a37 !important;
        border: 1px solid #c7d6e6 !important;
        border-radius: 12px !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #6e7f93 !important;
    }
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        background: linear-gradient(135deg, #356fa8 0%, #295b8c 100%);
        color: #f4f9ff !important;
        font-weight: 800;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 6px 14px rgba(34, 82, 128, 0.25);
        letter-spacing: 0.2px;
    }
    .stButton > button p,
    .stButton > button span {
        font-weight: 800 !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.04);
    }
    .stMarkdown, .stMarkdown *, .stCaption, .stCaption * {
        color: #243447 !important;
    }
    [data-testid="stAlertContent"] * {
        color: #243447 !important;
    }
    [data-testid="stImage"] img {
        border-radius: 14px;
        border: 1px solid #cad9e8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <h1>Integrated Manufacturing AI Platform</h1>
        <p style="margin: 0.2rem 0 0 0; color: #3e546d !important;">
            Multimodal GenAI + Agentic AI + Docker/Kubernetes in one polished workspace.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2)

with left:
    st.subheader("Multimodal Manufacturing Creator")
    prompt = st.text_area(
        "Describe your manufacturing concept",
        placeholder="Example: Eco-friendly smart conveyor module for MSME factories",
    )
    if st.button("Generate Narrative + Visual"):
        if not prompt.strip():
            st.warning("Please enter a concept prompt.")
        else:
            with st.spinner("Generating concept..."):
                response = requests.post(
                    f"{API_BASE}/api/genai/create",
                    json={"prompt": prompt},
                    timeout=90,
                )
                if response.ok:
                    data = response.json()
                    st.markdown("### Narrative")
                    st.write(data.get("narrative", "No narrative returned"))
                    st.markdown("### Prototype Visual")
                    st.image(data.get("image_url", ""), use_column_width=True)
                else:
                    err = response.json()
                    st.error(
                        f"Generation failed: {err.get('error', 'unknown_error')} | "
                        f"{err.get('details', 'No details available')}"
                    )

with right:
    st.subheader("Multi-Agent Manufacturing System")
    topic = st.text_input(
        "Enter sourcing/operations objective",
        placeholder="Example: optimize supplier reliability for EV components or drone motor sourcing",
    )
    if st.button("Run Researcher + Writer Agents"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Running agent pipeline..."):
                response = requests.post(
                    f"{API_BASE}/api/agentic/run",
                    json={"topic": topic},
                    timeout=90,
                )
                if response.ok:
                    data = response.json()
                    st.markdown(
                        f"**Detected focus:** {data.get('detected_focus', 'General manufacturing program')}"
                    )
                    st.markdown("### Final Report")
                    st.markdown(data.get("final_report", "No report returned"))
                else:
                    err = response.json()
                    st.error(
                        f"Agent pipeline failed: {err.get('error', 'unknown_error')} | "
                        f"{err.get('details', 'No details available')}"
                    )
