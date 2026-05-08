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


def _compute_archetype_ids(answers_likert: dict) -> list[str]:
    """Reiknar arketýpu-IDs frá persónuleikasvörum, með try/except svo að
    submission bregst ekki ef chaos-modulinn breytist."""
    try:
        from questions import personality_questions
        from chaos import collect_personality_tags, select_archetypes
        tags = collect_personality_tags(answers_likert, personality_questions())
        archetypes = select_archetypes(tags)
        return [a["id"] for a in archetypes if a.get("id")]
    except Exception:
        return []


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
        "archetype_ids": _compute_archetype_ids(answers_likert),
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


# ---------------------------------------------------------------------------
# RPC-fetch fyrir lifandi tölfræðisíðu
# ---------------------------------------------------------------------------

def _rest_select(view_or_table: str, params: dict | None = None) -> list | None:
    """SELECT á view/table í gegnum PostgREST. Aðeins notað fyrir MVs sem hafa
    `grant select to anon` — engar PII-tengdar töflur."""
    url, key = _supabase_config()
    if not (url and key):
        return None
    try:
        import requests
        endpoint = f"{url}/rest/v1/{view_or_table}"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
        }
        q = {"select": "*"}
        if params:
            q.update(params)
        r = requests.get(endpoint, headers=headers, params=q, timeout=8)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=60, show_spinner=False)
def fetch_total() -> int:
    """Heildarfjöldi svara. Cached í 60 sek."""
    out = _rest_select("kompas_total_mv")
    if isinstance(out, list) and out:
        return int(out[0].get("total", 0)) if isinstance(out[0], dict) else 0
    return 0


@st.cache_data(ttl=60, show_spinner=False)
def fetch_top1_counts() -> list[dict]:
    out = _rest_select("kompas_top1_counts_mv", {"order": "n.desc"})
    return out or []


@st.cache_data(ttl=60, show_spinner=False)
def fetch_shoe_x_party() -> list[dict]:
    out = _rest_select("kompas_shoe_x_party_mv")
    return out or []


@st.cache_data(ttl=60, show_spinner=False)
def fetch_pool_x_party() -> list[dict]:
    out = _rest_select("kompas_pool_x_party_mv")
    return out or []


@st.cache_data(ttl=60, show_spinner=False)
def fetch_archetype_x_party() -> list[dict]:
    out = _rest_select("kompas_archetype_x_party_mv")
    return out or []


def clear_aggregate_cache():
    """Hreinsar cache fyrir lifandi gögn — notað af „Endurnýja“ takka."""
    fetch_total.clear()
    fetch_top1_counts.clear()
    fetch_shoe_x_party.clear()
    fetch_pool_x_party.clear()
    fetch_archetype_x_party.clear()


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
