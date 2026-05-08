"""
Nafnlaus svaragögn — sendir niður á Supabase REST API.

Persónuverndarleg meginregla: Engin nöfn, engin tölvupóstföng, engar
notendatengingar. Aðeins svör + reiknuð niðurstaða.

Skemmavarnir (`Row Level Security`) á Supabase eiga að krefjast `consented = true`
á hverri innsetningu. Sjá `migrations/001_create_responses.sql`.

Ef Supabase-tengið er ekki sett upp (t.d. þegar app keyrir staðbundið án
secrets) þá fara köll í engan farveg og engin villa kemur upp.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import streamlit as st


APP_VERSION = "1.0"


def _supabase_config():
    """Skilar (url, key) eða (None, None) ef ekki tilgreint."""
    try:
        s = st.secrets.get("supabase")
        if s and s.get("url") and s.get("anon_key"):
            return s["url"].rstrip("/"), s["anon_key"]
    except Exception:
        pass
    return None, None


def is_configured() -> bool:
    url, key = _supabase_config()
    return bool(url and key)


def ensure_session_id() -> str:
    """UUID sem auðkennir vafra-lotu — notað til að koma í veg fyrir tvísending."""
    if "client_session_id" not in st.session_state:
        st.session_state.client_session_id = str(uuid.uuid4())
    return st.session_state.client_session_id


def already_submitted() -> bool:
    return st.session_state.get("submission_saved", False)


def mark_submitted(record_id: str | None = None):
    st.session_state["submission_saved"] = True
    if record_id:
        st.session_state["submission_id"] = record_id


def submit_response(
    answers_likert: dict,
    answers_chaos: dict,
    top3: list[dict],
    user_axis_vector: dict,
    evidence_summary: dict | None = None,
) -> tuple[bool, str]:
    """Sendir nafnlaust svar á Supabase. Skilar (success, message)."""
    url, key = _supabase_config()
    if not (url and key):
        return False, "Supabase ekki uppsett í þessu umhverfi."

    payload = {
        "client_session": ensure_session_id(),
        "consented": True,
        "answers_likert": {k: int(v) for k, v in answers_likert.items()},
        "answers_chaos": {k: str(v) for k, v in answers_chaos.items()},
        "top3": [
            {"code": t["code"],
             "match_percent": round(float(t["match"]) * 100, 1),
             "short_name": t["party"]["short_name"]}
            for t in top3
        ],
        "user_axis_vector": {k: round(float(v), 3) for k, v in user_axis_vector.items()},
        "evidence_summary": evidence_summary or {},
        "app_version": APP_VERSION,
    }

    try:
        # Notum requests sem er hluti af Streamlit dependency stack.
        import requests
        endpoint = f"{url}/rest/v1/kompas_responses"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        resp = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=8)
        if resp.status_code in (200, 201):
            data = resp.json()
            record_id = (data[0].get("id") if isinstance(data, list) and data else None)
            mark_submitted(record_id)
            return True, "Takk fyrir — svar þitt var skráð nafnlaust."
        else:
            # 409 / 403 / 401 — láta notanda vita á einföldum nótum
            return False, f"Tókst ekki að skrá svar (HTTP {resp.status_code})."
    except Exception as e:
        return False, f"Tókst ekki að skrá svar: {type(e).__name__}."


def consent_disclosure_md() -> str:
    """Markdown-texti sem útskýrir nákvæmlega hverju er safnað og hverju ekki."""
    return (
        "**Hvað við söfnum (ef þú samþykkir):**\n\n"
        "- Svörum þínum við spurningalistanum (öll 25 stefnu-spurningar + valfrjáls vibe-spurningar)\n"
        "- Reiknuðum efstu þremur framboðum og prósentum\n"
        "- Tíma og lotu-auðkenni (tilviljunarkenndur strengur, ekki tengdur þér)\n\n"
        "**Hvað við söfnum EKKI:**\n\n"
        "- Nafninu þínu\n"
        "- Tölvupóstfangi\n"
        "- IP-tölu\n"
        "- Notendareikningi eða tengingu við Facebook / Google / aðra þjónustu\n"
        "- Staðsetningu eða tæki\n\n"
        "Gögnin eru notuð til að skoða heildardreifingu á svörum — t.d. hvaða "
        "framboð koma oftast efst — og verða aldrei seld eða framseld."
    )
