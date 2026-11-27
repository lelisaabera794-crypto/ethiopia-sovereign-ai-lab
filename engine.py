import json
import re
import traceback
import numpy as np
import scipy.integrate as integrate
import sympy as sp
import plotly.graph_objects as go
from groq import Groq

LANG_MAP = {
    "English": "Write all outputs in clear, rigorous academic English.",
    "Afaan Oromoo (Qubee)": "Write all titles, labels, explanations, teacher guides, and questions in fluent, grammatically natural Afaan Oromoo (Qubee) using authentic Ethiopian academic terminology (Humni=Force, Saffisa=Velocity, Guutinsa=Acceleration, Anniyoo=Energy, Hanga=Mass, Ho'a=Heat, Elektiriikii=Electricity, Herrega=Mathematics, Keemistirii=Chemistry, Baayoloojii=Biology). Write like a native Oromo university professor.",
    "Amharic (አማርኛ)": "Write all titles, labels, explanations, teacher guides, and questions in fluent, grammatically natural Amharic (አማርኛ) using authentic Ethiopian academic terminology (ኃይል=Force, ፍጥነት=Velocity, ሽምጠጣ=Acceleration, ጉልበት=Energy, መጠነ-ቁስ=Mass, ሙቀት=Heat, ኤሌክትሪክ=Electricity, ሒሳብ=Mathematics, ኬሚስትሪ=Chemistry, ባዮሎጂ=Biology). Write like a native Ethiopian university professor.",
    "Trilingual (English + Afaan Oromoo + Amharic)": "Present every explanation, challenge, and engineering insight cleanly organized in three sections: 1) English, 2) Fluent Native Afaan Oromoo (Qubee), and 3) Fluent Native Amharic (አማርኛ)."
}

def pick_model(client):
    preferred = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
    try:
        avail = [m.id for m in client.models.list().data]
        for p in preferred:
            if p in avail:
                return p
        for m in avail:
            if not any(x in m.lower() for x in ["whisper", "guard", "orpheus"]):
                return m
    except Exception:
        pass
    return "openai/gpt-oss-120b"

def synthesize_lab(secret_key, query, domain, tier, lang, max_retries=3):
    client = Groq(api_key=secret_key)
    model_id = pick_model(client)
    l_rule = LANG_MAP[lang]

    prompt = (
        f"You are an autonomous scientific discovery and national education engine built in Ethiopia. "
        f"Subject: {domain}. Tier: {tier}. Language: {l_rule}. Problem: '{query}'. "
        f"Reason from first principles with zero hardcoding. Synthesize an interactive 2D or 3D simulation using numpy (`np`), scipy.integrate (`integrate`), sympy (`sp`), and plotly.graph_objects (`go`). "
        f"Use 2D plots (`go.Scatter`, `go.Bar`) for Elementary/Middle School or 1D/2D concepts, and 3D plots (`go.Scatter3d`, `go.Surface`) for spatial fields, orbits, molecules, or multi-variable systems. "
        f"Return ONLY valid JSON with these exact keys: "
        f'{{"title": "Title", "subfield": "Subfield", "viz_mode": "2D or 3D Lab", "latex_formula": "LaTeX equation", '
        f'"socratic_prediction": "Predictive question before moving sliders", '
        f'"student_first_principles": "Deep step-by-step derivation and exam misconceptions", '
        f'"creativity_challenge": "Hands-on innovation challenge to invent a real solution in Ethiopia", '
        f'"teacher_university_guide": "Lesson objectives, zero-hardware classroom demo guide, and 3 critical-thinking questions", '
        f'"moe_national_infrastructure": "Link to Ethiopian national infrastructure (GERD, solar, telecom, agriculture, health) and curriculum reform", '
        f'"parameters": {{"p1": {{"label": "Param 1 with units", "min": 0.1, "max": 10.0, "default": 2.0}}, "p2": {{"label": "Param 2 with units", "min": 0.1, "max": 10.0, "default": 1.0}}}}, '
        f'"simulation_code": "Valid Python defining `def run_sim(params):` using `np`, `integrate`, `sp`, `go`. Read `params[\'p1\']`, etc., compute accurately, return Plotly Figure `fig`. Never call `fig.show()`. Label axes with units."}}'
    )

    feedback = ""
    for attempt in range(1, max_retries + 1):
        res = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "Output strictly valid JSON only. Never use markdown code fences."},
                {"role": "user", "content": prompt + feedback}
            ],
            temperature=0.2
        )
        raw = res.choices.message.content.strip()
        cleaned = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        try:
            data = json.loads(cleaned)
            defaults = {k: float(v["default"]) for k, v in data["parameters"].items()}
            sandbox = {"np": np, "integrate": integrate, "sp": sp, "go": go}
            exec(data["simulation_code"], sandbox)
            if sandbox["run_sim"](defaults) is None:
                raise ValueError("run_sim returned None")
            data["pass_count"] = attempt
            return data
        except Exception as err:
            feedback = f"\n\nFIX ATTEMPT {attempt}: {str(err)}\n{traceback.format_exc()}\nReturn fixed valid JSON."
    raise RuntimeError("Self-healing verification reached max retries. Try rephrasing slightly.")
