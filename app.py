import streamlit as st
import numpy as np
import scipy.integrate as integrate
import sympy as sp
import plotly.graph_objects as go
from engine import synthesize_lab

st.set_page_config(page_title="Sovereign STEM OS Ethiopia", page_icon="🇪🇹", layout="centered")
st.title("🇪🇹 Sovereign STEM & Knowledge OS")
st.caption("Autonomous Self-Healing Labs, Critical Thinking & Student-Teacher-University-MoE Infrastructure")

secret_key = st.secrets.get("SOVEREIGN_ENGINE_KEY", "")

c1, c2, c3 = st.columns(3)
with c1:
    domain = st.selectbox("🧬 Subject:", ["Auto-Detect Any Subject", "Physics", "Mathematics", "Chemistry", "Biology & Health", "Computer Science & AI", "Engineering & Energy", "Economics"])
with c2:
    tier = st.selectbox("🎓 Tier:", ["Elementary (Grades 1-6)", "High School (Grades 7-12)", "University BSc", "Postgraduate & Research"])
with c3:
    lang = st.selectbox("🌍 Language:", ["English", "Afaan Oromoo (Qubee)", "Amharic (አማርኛ)", "Trilingual (English + Afaan Oromoo + Amharic)"])

query = st.text_area("🔬 Enter ANY Scientific Problem, Curriculum Concept, or Innovation Challenge:", value="3D spiral trajectory of a charged particle in a magnetic field")

if st.button("🚀 Synthesize Autonomous Lab & National Curriculum Module", use_container_width=True):
    if not secret_key:
        st.error("System Notice: Compute engine key is awaiting initialization in server secrets.")
    else:
        with st.spinner("🧠 Reasoning from first principles & verifying in self-healing sandbox..."):
            try:
                st.session_state["lab_data"] = synthesize_lab(secret_key, query, domain, tier, lang)
            except Exception as e:
                st.error(f"System Notice: {e}")

if "lab_data" in st.session_state:
    data = st.session_state["lab_data"]
    st.divider()
    st.subheader(f"🌐 {data['title']}")
    st.caption(f"Field: **{data['subfield']}** | Mode: **{data['viz_mode']}** | Self-Healing Check: **Verified (Pass {data.get('pass_count', 1)})**")

    st.latex(data["latex_formula"])
    st.info(f"🤔 **Predict First (Critical Thinking):** {data['socratic_prediction']}")

    st.markdown("### 🎛️ Interactive Experiment Controls")
    live_vals = {}
    for k, meta in data["parameters"].items():
        live_vals[k] = st.slider(meta["label"], float(meta["min"]), float(meta["max"]), float(meta["default"]))

    try:
        sandbox = {"np": np, "integrate": integrate, "sp": sp, "go": go}
        exec(data["simulation_code"], sandbox)
        fig = sandbox["run_sim"](live_vals)
        fig.update_layout(height=520, margin=dict(l=10, r=10, b=10, t=40))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Parameter boundary reached ({e}). Adjust slider slightly.")

    t1, t2, t3, t4 = st.tabs(["👨‍🎓 Student First-Principles", "💡 Innovation & Creativity", "👩‍🏫 Teacher & University", "🏛️ MoE & National Impact"])
    with t1:
        st.write(data["student_first_principles"])
    with t2:
        st.write(data["creativity_challenge"])
    with t3:
        st.write(data["teacher_university_guide"])
    with t4:
        st.write(data["moe_national_infrastructure"])

    report = f"# {data['title']}\n**Subject:** {data['subfield']} | **Level:** {tier} | **Language:** {lang}\n\n## Equations\n$${data['latex_formula']}$$\n\n## 1. Student First-Principles\n{data['student_first_principles']}\n\n## 2. Innovation & Creativity Challenge\n{data['creativity_challenge']}\n\n## 3. Teacher & University Guide\n{data['teacher_university_guide']}\n\n## 4. MoE & National Infrastructure\n{data['moe_national_infrastructure']}\n"
    st.download_button("📥 Download Complete Student + Teacher + MoE Package (.md)", report, "SovereignSTEM_Lab_Package.md", "text/markdown", use_container_width=True)

st.divider()
st.caption("© Sovereign STEM & Knowledge OS | Built in Addis Ababa, Ethiopia 🇪🇹")
