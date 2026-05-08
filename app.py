"""
Borgarstjórnar­kompás 2026 — Streamlit app.

Þetta er ÓHÁÐ samanburðartól. Niðurstaðan sýnir hvaða framboð eru NÆST þínum
svörum út frá opinberum stefnumálum eins og við höfum kortlagt þau.
Þetta er EKKI kosningaráðgjöf og tólið mælir ekki með neinu framboði.

Sjá DATA_REVIEW.md fyrir lista yfir gögn sem þarf að staðfesta áður en þetta
er birt opinberlega.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from parties import (
    AXES,
    AXIS_DIRECTION_NOTES,
    AXIS_IDS,
    AXIS_LABELS,
    DEFAULT_TAGLINE,
    PARTIES,
    PARTY_ORDER,
)
from questions import (
    ALL_QUESTIONS,
    CHAOS_QUESTIONS,
    LIKERT_LABELS,
    LIKERT_VALUES,
    PERSONALITY_QUESTIONS,
    QUESTIONS,
    chaos_questions,
    personality_questions,
    policy_questions,
    sample_questions,
)
from scoring import (
    axis_agreement,
    biggest_agreements_and_disagreements,
    compute_user_axis_vector,
    rank_parties,
)
from chaos import (
    chaos_score,
    collect_personality_tags,
    render_archetype_blurb,
    select_archetypes,
)
import submissions
from policy_matrix import (
    POLICY_AXES,
    POLICY_AXIS_GROUPS,
    POLICY_AXIS_IDS,
    POLICY_AXIS_LOOKUP,
    POLICY_MATRIX,
    POLICY_MATRIX_DETAILS,
    ambiguous_axes,
    axes_where_parties_overlap,
    biggest_disagreement_axes,
    get_certainty,
    get_detail,
    get_reason,
    get_sources,
    most_similar_pairs,
    overall_evidence_score,
    potential_contradictions,
    strongest_opposites,
    strongest_oppositions,
    strongest_priorities,
)


# ---------------------------------------------------------------------------
# Síðustillingar
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Borgarstjórnar­kompás Reykjavíkur 2026",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Stíl-CSS — hófleg fágun, ekki yfirgnæfandi.
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, .stRadio label, .stSelectbox, .stButton {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }

h1, h2, h3, h4 { letter-spacing: -0.015em; font-weight: 700; }
h1 { font-weight: 800; }

/* HERO */
.bk-hero {
    background:
        radial-gradient(circle at 80% 20%, rgba(255,255,255,0.10), transparent 50%),
        linear-gradient(135deg, #0f172a 0%, #1d3557 45%, #2872a1 100%);
    color: white;
    padding: 2.3rem 2.2rem 2.1rem 2.2rem;
    border-radius: 18px;
    margin: 0.4rem 0 1.6rem 0;
    box-shadow: 0 14px 40px rgba(15,23,42,0.18);
    position: relative;
    overflow: hidden;
}
.bk-hero::after {
    content: "🗳️";
    position: absolute;
    bottom: -1.6rem; right: -0.6rem;
    font-size: 9rem;
    opacity: 0.08;
    transform: rotate(-12deg);
    pointer-events: none;
}
.bk-hero h1 { font-size: 2.3rem; line-height: 1.12; margin: 0 0 0.5rem 0; color: white; }
.bk-hero p { font-size: 1.05rem; max-width: 760px; opacity: 0.92; margin: 0; }
.bk-hero .bk-pill { background: rgba(255,255,255,0.16); color: white; border: none; }

.bk-disclaimer {
    background: #f5f7fb;
    border-left: 4px solid #5b8dbe;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    font-size: 0.92rem;
    color: #2a2f3a;
    margin: 0.5rem 0 1.4rem 0;
}
.bk-disclaimer strong { color: #1d2230; }

/* CARDS */
.bk-card {
    border: 1px solid #e3e6ee;
    border-radius: 14px;
    padding: 1.2rem 1.3rem;
    margin-bottom: 1.1rem;
    background: white;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04);
    transition: box-shadow 0.2s ease, transform 0.15s ease;
}
.bk-card:hover { box-shadow: 0 10px 28px rgba(15,23,42,0.07); }
.bk-card-accent { border-top: 4px solid var(--accent, #6b7a99); }
.bk-card h3 { margin-top: 0; }

/* RANK BADGE */
.bk-rank {
    display: inline-flex; align-items: center; justify-content: center;
    width: 2.2rem; height: 2.2rem; border-radius: 50%;
    font-weight: 800; font-size: 1rem;
    margin-right: 0.55rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.10);
}
.bk-rank-1 { background: linear-gradient(135deg,#fff5b8,#f4c542); color: #6f5106; }
.bk-rank-2 { background: linear-gradient(135deg,#f1f3f7,#c1c8d6); color: #3a4254; }
.bk-rank-3 { background: linear-gradient(135deg,#f3dccd,#d59b6b); color: #5a361b; }

/* LETTER PILL */
.bk-letter-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.6rem;
    height: 2.6rem;
    border-radius: 50%;
    font-weight: 800;
    color: white;
    margin-right: 0.6rem;
    font-size: 1.15rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.10);
}

/* PROGRESS BAR */
.bk-match-bar-bg {
    width: 100%;
    height: 10px;
    background: #eef0f6;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 0.3rem;
}
.bk-match-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--accent, #6b7a99), var(--accent, #6b7a99));
    border-radius: 999px;
    transition: width 0.5s ease;
}

/* BIG PERCENTAGE */
.bk-big-pct {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1;
    color: var(--accent, #1f4e8c);
    letter-spacing: -0.02em;
    margin: 0;
}
.bk-big-pct-label {
    font-size: 0.78rem; color: #5a6378; text-transform: uppercase;
    letter-spacing: 0.08em; font-weight: 600;
}

/* PILLS / TAGS */
.bk-pill {
    display: inline-block; background: #eef3fa; color: #1f4e8c;
    border: 1px solid #d4e3f1;
    border-radius: 999px; padding: 3px 11px; font-size: 0.8rem;
    margin-right: 0.3rem; font-weight: 500;
}
.bk-uncertain {
    display: inline-block;
    background: #fff5e0;
    color: #7a5b00;
    border: 1px solid #f0d790;
    border-radius: 4px;
    padding: 0 0.4rem;
    font-size: 0.78rem;
    margin-left: 0.3rem;
}

/* BONUS / SHARE BLOCKS */
.bk-bonus {
    background: linear-gradient(135deg,#fdfaf3,#fff7e3);
    border: 1px dashed #d8c98a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-top: 1.4rem;
}
.bk-bonus h4 { margin-top: 0; }

.bk-share {
    background: linear-gradient(135deg,#1d3557 0%, #2872a1 100%);
    color: white;
    padding: 1.4rem 1.5rem;
    border-radius: 14px;
    margin: 1.4rem 0 0.4rem 0;
    box-shadow: 0 8px 24px rgba(29,53,87,0.18);
}
.bk-share h3 { color: white; margin: 0 0 0.4rem 0; }
.bk-share .bk-pill { background: rgba(255,255,255,0.16); color: white; border: none; }

/* SHARED BANNER */
.bk-shared-banner {
    background: linear-gradient(90deg,#fff7d8 0%,#fff3c0 100%);
    border: 1px solid #e6cf76;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 1rem;
    color: #5e4900;
}

/* MINOR */
.bk-mini { font-size: 0.85rem; color: #5a6378; }

footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Lota — staða
# ---------------------------------------------------------------------------

def _init_state():
    st.session_state.setdefault("answers", {})         # policy + personality (Likert int)
    st.session_state.setdefault("chaos_answers", {})   # chaos (str)
    st.session_state.setdefault("submitted", False)
    st.session_state.setdefault("wizard_idx", -1)      # -1 = ekki hafið; 0..N = núverandi spurning


_init_state()


def reset_all():
    st.session_state.answers = {}
    st.session_state.chaos_answers = {}
    st.session_state.submitted = False
    st.session_state.wizard_idx = -1
    # Henda spurningarvali og lotu-auðkenni svo notandinn fái NÝJAR spurningar
    st.session_state.pop("sampled_questions", None)
    st.session_state.pop("client_session_id", None)
    st.session_state.pop("submission_saved", None)
    st.session_state.pop("consent_skipped", None)
    st.session_state.pop("consent_checkbox", None)


def get_session_questions() -> list[dict]:
    """Skilar spurningalista lotu — sömu fyrir sama notanda en breytast við reset."""
    if "sampled_questions" not in st.session_state:
        seed = submissions.ensure_session_id()
        st.session_state.sampled_questions = sample_questions(seed)
    return st.session_state.sampled_questions


# ---------------------------------------------------------------------------
# Deilanlegar niðurstöður — kóðun og afkóðun
# ---------------------------------------------------------------------------
# Niðurstöður eru kóðaðar í URL (`?r=A-73,S-71,P-68`) þannig að notandi geti
# afritað slóðina og deilt í gegnum samfélagsmiðla, e-mail eða iMessage.
# Þegar slóðin er opnuð birtist sérstakt „Deilt frá vini“ útlit.

def encode_share_token(ranking) -> str:
    top3 = ranking[:3]
    parts = [f"{r['code']}-{int(round(r['match'] * 100))}" for r in top3]
    return ",".join(parts)


def decode_share_token(token: str):
    out = []
    if not token:
        return out
    for part in token.split(","):
        if "-" not in part:
            continue
        code, pct = part.split("-", 1)
        if code in PARTIES:
            try:
                v = int(pct)
                v = max(0, min(100, v))
                out.append((code, v))
            except ValueError:
                continue
    return out


def get_share_param() -> str | None:
    try:
        params = st.query_params
        # st.query_params returns string values directly in newer Streamlit
        return params.get("r")
    except Exception:
        return None


def set_share_param(token: str | None):
    try:
        if token:
            st.query_params["r"] = token
        elif "r" in st.query_params:
            del st.query_params["r"]
    except Exception:
        pass


def share_text_for(top3) -> str:
    """Tekur top-3 listann (frá rank_parties) og býr til texta tilbúinn fyrir samfélagsmiðla."""
    lines = ["🗳️ Borgarstjórnar­kompás 2026 — mín topp 3:"]
    medals = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(top3):
        m = r["match"] * 100
        lines.append(f"{medals[i]} {r['party']['short_name']} — {m:.0f}%")
    lines.append("")
    lines.append("Þetta er ekki kosningaráðgjöf — bara samanburður á áherslum. ")
    lines.append("Prófaðu sjálf/ur ➜")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Hjálparföll fyrir UI
# ---------------------------------------------------------------------------

def disclaimer_box(extra: str = ""):
    msg = (
        "<strong>Hlutleysisskýring.</strong> Þetta tól er ekki kosningaráðgjöf. "
        "Það mælir ekki með neinu framboði og hefur ekki tengsl við neinn flokk. "
        "Lestu stefnuskrár framboðanna sjálf/ur áður en þú kýst."
    )
    if extra:
        msg += f" {extra}"
    st.markdown(f'<div class="bk-disclaimer">{msg}</div>', unsafe_allow_html=True)


def render_letter_pill(letter: str, color: str) -> str:
    return (
        f'<span class="bk-letter-pill" style="background:{color};">{letter}</span>'
    )


def show_logo_or_pill(party: dict, height: int = 64):
    logo_path = party.get("logo")
    if logo_path and os.path.exists(logo_path):
        try:
            st.image(logo_path, width=height * 2)
            return
        except Exception:
            pass
    # Fallback: stafa-kúla
    st.markdown(
        f'<div style="display:flex;align-items:center;">'
        f'{render_letter_pill(party["list_letter"], party["color"])}'
        f'<span style="font-weight:600;font-size:1.05rem;">{party["short_name"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def axis_score_chip(score: float, uncertain: bool) -> str:
    """Lítill gluggi sem sýnir stigatölu með litlum bakgrunn (transparent á báða vegu)."""
    if uncertain:
        bg = "#fff5e0"
        border = "#f0d790"
        color = "#7a5b00"
        text = f"{score:+.0f} (óvíst)"
    else:
        # Hófleg lit: blár fyrir +, grár fyrir 0, rauð-brúnn fyrir -
        if score > 0.5:
            bg, border, color = "#e7f1f9", "#b9d7ec", "#1f4e8c"
        elif score < -0.5:
            bg, border, color = "#f6e8e8", "#e0bcbc", "#7a2222"
        else:
            bg, border, color = "#f1f2f5", "#d8dbe3", "#3a4254"
        text = f"{score:+.0f}"
    return (
        f'<span style="display:inline-block;background:{bg};border:1px solid {border};'
        f'color:{color};padding:1px 8px;border-radius:5px;font-size:0.82rem;'
        f'min-width:48px;text-align:center;">{text}</span>'
    )


# ---------------------------------------------------------------------------
# Sider — siglingaskil
# ---------------------------------------------------------------------------

SHARED_TOKEN = get_share_param()


def render_shared_banner_if_present():
    if not SHARED_TOKEN:
        return
    decoded = decode_share_token(SHARED_TOKEN)
    if not decoded:
        return
    bits = " · ".join(
        f"<strong>{PARTIES[c]['list_letter']} {PARTIES[c]['short_name']}</strong> {p}%"
        for c, p in decoded
    )
    st.markdown(
        f"""
        <div class="bk-shared-banner">
            🔗 <strong>Þú ert að skoða niðurstöðu sem einhver deildi.</strong>
            Topp 3: {bits}.
            Þú getur prófað sjálf/ur — slóðin þín verður öðruvísi ef svörin þín eru öðruvísi.
        </div>
        """,
        unsafe_allow_html=True,
    )


_full_menu_unlocked = bool(st.session_state.submitted) or bool(SHARED_TOKEN)

with st.sidebar:
    st.markdown("### 🗳️ Borgarstjórnar­kompás")
    st.caption("Reykjavík 2026 — óháð samanburðartól")
    if _full_menu_unlocked:
        page = st.radio(
            "Síða",
            [
                "Niðurstöður",
                "Samanburður",
                "Stefnu-fylki",
                "Hópgögn",
                "Aðferðafræði",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        if st.button("Endurtaka prófið", use_container_width=True):
            reset_all()
            st.rerun()
    else:
        page = st.radio(
            "Síða",
            ["Wizard", "Hópgögn"],
            format_func=lambda v: "🧭 Taka prófið" if v == "Wizard" else "📊 Lifandi tölfræði",
            label_visibility="collapsed",
        )
        if page == "Wizard":
            st.info(
                "Aðrar greiningarsíður opnast þegar þú lýkur prófinu. "
                "Eitt skref í einu — ýttu á **„Áfram“** eftir hvert svar.",
                icon="🔒",
            )
            if st.session_state.wizard_idx > 0:
                if st.button("Byrja upp á nýtt", use_container_width=True):
                    reset_all()
                    st.rerun()
        else:
            st.caption(
                "Þú getur skoðað hópgögnin án þess að taka prófið. "
                "Smelltu á „Taka prófið“ að ofan til að bæta þínu eigin svari við."
            )
    st.divider()
    st.caption(
        "Þetta er **ekki kosningaráðgjöf**. Tólið sýnir hvaða framboð eru næst "
        "þínum svörum út frá opinberum stefnumálum."
    )


# ---------------------------------------------------------------------------
# Síða: Upphafssíða
# ---------------------------------------------------------------------------

def render_landing():
    # Hero
    st.markdown(
        """
        <div class="bk-hero">
            <span class="bk-pill">Reykjavík · 2026 · óháð samanburðartól</span>
            <h1 style="margin-top: 0.7rem;">Hvaða borgarstjórnarframboð passar best við þínar áherslur?</h1>
            <p>Svaraðu nokkrum spurningum á einföldum kvarða og sjáðu hvaða framboð liggja næst þínum svörum á 12 stefnuásum. Þetta er <strong>ekki kosningaráðgjöf</strong> — heldur samanburður á áherslum.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🧭 Hvernig virkar þetta?")
        st.markdown(
            "Þú svarar nokkrum spurningum á einföldum kvarða — frá **mjög ósammála** "
            "yfir í **mjög sammála**. Tólið ber svörin saman við skráða stefnu hvers "
            "framboðs á sömu málefnasviðum."
        )
    with col2:
        st.markdown("#### ⚖️ Hvað sýnir tólið?")
        st.markdown(
            "Þrjú framboð sem eru næst þínum svörum, með prósentu sem byggir á "
            "vegalengd milli þinna svara og stefnu framboðsins. Tólið mælir **ekki** "
            "með því hvern þú átt að kjósa."
        )
    with col3:
        st.markdown("#### 📚 Mikilvægt")
        st.markdown(
            "Stefnu-mat einstakra framboða er **bráðabirgða** og þarfnast "
            "staðfestingar. Lestu stefnuskrár framboðanna sjálf/ur áður en þú kýst. "
            "Sjá nánar á aðferðafræðisíðu."
        )

    disclaimer_box(
        "Þú getur skipt um síðu hvenær sem er með valmyndinni til vinstri. "
        "Svör eru aðeins geymd í þínum vafra."
    )

    st.markdown("### Framboð sem eru með í tólinu")
    st.caption(
        "Listi raðaður eftir kjörseðils-bókstaf. Litir og lógó eru notuð hóflega "
        "og engin túlkun er falin í þeim."
    )

    cols = st.columns(4)
    for i, code in enumerate(PARTY_ORDER):
        p = PARTIES[code]
        with cols[i % 4]:
            uncertain_warning = ""
            if len(p.get("uncertain_axes", [])) >= len(AXIS_IDS) // 2:
                uncertain_warning = " <span class='bk-uncertain'>óvíst</span>"
            st.markdown(
                f'<div class="bk-card" style="--accent:{p["color"]};">'
                f'{render_letter_pill(p["list_letter"], p["color"])}'
                f'<strong>{p["short_name"]}</strong>{uncertain_warning}<br/>'
                f'<span class="bk-mini">{p["name"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()
    cta_left, cta_right = st.columns([1, 2])
    with cta_left:
        if st.button("▶️  Byrja spurningalista", type="primary", use_container_width=True):
            st.toast("Veldu „Spurningalisti“ í valmyndinni til vinstri.", icon="🧭")
    with cta_right:
        st.markdown(
            "<span class='bk-mini'>≈ 25 spurningar · 5 mínútur · þú getur deilt niðurstöðunni þegar þú vilt</span>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Síða: Spurningalisti
# ---------------------------------------------------------------------------

def _likert_index_for_value(v: int) -> int | None:
    """Sýnir réttan vísi inn í LIKERT_LABELS út frá vistuðu gildi, eða None ef ósvarað."""
    for i, val in enumerate([-2, -1, 0, 1, 2]):
        if val == v:
            return i
    return None


def render_likert_question(q: dict, badge: str | None = None):
    label = q["text"]
    if badge:
        st.markdown(f"<span class='bk-mini'>{badge}</span>", unsafe_allow_html=True)
    current = st.session_state.answers.get(q["id"])
    default_idx = _likert_index_for_value(current) if current is not None else None
    choice = st.radio(
        label,
        LIKERT_LABELS,
        index=default_idx,
        key=f"radio_{q['id']}",
        horizontal=True,
        help=q.get("help"),
    )
    # Aðeins skrá svar þegar notandi hefur raunverulega smellt á valkost.
    if choice is not None:
        st.session_state.answers[q["id"]] = LIKERT_VALUES[choice]


def render_chaos_question(q: dict):
    options = ["—"] + q["options"]
    current = st.session_state.chaos_answers.get(q["id"], "—")
    default_idx = options.index(current) if current in options else 0
    choice = st.selectbox(
        q["text"],
        options,
        index=default_idx,
        key=f"chaos_{q['id']}",
    )
    if choice != "—":
        st.session_state.chaos_answers[q["id"]] = choice
    elif q["id"] in st.session_state.chaos_answers:
        del st.session_state.chaos_answers[q["id"]]


def _is_question_answered(q: dict) -> bool:
    if q.get("type") == "chaos":
        return q["id"] in st.session_state.chaos_answers
    return q["id"] in st.session_state.answers


def render_wizard():
    """Wizard-mode spurningalisti — eitt skref í einu, valmynd læst."""
    qs = get_session_questions()
    total = len(qs)
    idx = st.session_state.wizard_idx

    # ---- Forsíða (idx == -1) ----
    if idx < 0:
        st.markdown(
            """
            <div class="bk-hero">
                <span class="bk-pill">Reykjavík · 2026 · óháð samanburðartól</span>
                <h1 style="margin-top: 0.7rem;">Hvaða borgarstjórnarframboð passar best við þínar áherslur?</h1>
                <p>Þú svarar nokkrum spurningum á einföldum kvarða, eitt skref í einu. Að lokum sjást þrjú framboð sem liggja næst þínum svörum á 12 stefnuásum — auk gamansamrar persónugerðar.</p>
                <p style="opacity:0.85;font-size:0.9rem;margin-top:0.6rem;">Þetta er <strong>ekki kosningaráðgjöf</strong>. Tólið mælir ekki með neinu framboði. Lestu stefnuskrár sjálf/ur áður en þú kýst.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ---- Persónuvernd / gagnasöfnun: áberandi tilkynning UPP-FYRIR ----
        st.markdown(
            """
            <div style="background:#fff;border:1px solid #b9d7ec;border-radius:12px;
                        padding:1rem 1.2rem;margin:0 0 1.4rem 0;
                        box-shadow:0 2px 8px rgba(31,78,140,0.06);">
                <div style="display:flex;align-items:flex-start;gap:0.8rem;">
                    <div style="font-size:1.6rem;line-height:1;">🔒</div>
                    <div style="flex:1;">
                        <strong style="color:#1d3557;">Persónuvernd og gagnasöfnun</strong><br/>
                        <span style="font-size:0.92rem;color:#3a4254;">
                            Í lok prófsins færðu valfrjálst að deila svari þínu <strong>nafnlaust</strong>
                            til að hjálpa okkur að skoða heildardreifingu á svörum. Þú þarft að
                            <strong>haka virkan</strong> við samþykki — sjálfgefið er ekkert sent.
                        </span>
                        <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:0.55rem;
                                    font-size:0.86rem;">
                            <span style="color:#1f6f43;">✅ Aðeins svör + reiknuð niðurstaða</span>
                            <span style="color:#7a2222;">🚫 Engin nöfn</span>
                            <span style="color:#7a2222;">🚫 Engin tölvupóstföng</span>
                            <span style="color:#7a2222;">🚫 Engin IP eða notendareikningar</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 🧭 Hvernig virkar þetta?")
            st.markdown(
                "Spurningarnar eru á 5 punkta kvarða (mjög ósammála → mjög sammála) "
                "auk nokkurra léttari spurninga sem hafa engin áhrif á samsvörun."
            )
        with c2:
            st.markdown("#### ⚖️ Hvað sýnir tólið?")
            st.markdown(
                "Þrjú framboð sem liggja næst þínum svörum, með hreinskiptu prósentumati, "
                "ásamt heildarsamanburði á 20 rekstrarásum."
            )
        with c3:
            st.markdown("#### 🔗 Deilanlegt")
            st.markdown(
                "Niðurstöðurnar þínar fá deilanlega slóð sem þú getur sent á fjölskyldu og vini. "
                "Tólið geymir engin svör utan vafrans."
            )

        st.divider()
        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("▶️  Byrja", type="primary", use_container_width=True):
                st.session_state.wizard_idx = 0
                st.rerun()
        with c2:
            st.markdown(
                f"<span class='bk-mini'>~ {total} spurningar · ≈ 5 mínútur · valmynd opnast þegar þú klárar</span>",
                unsafe_allow_html=True,
            )
        return

    # ---- Lokað? ----
    if idx >= total:
        st.session_state.submitted = True
        st.session_state.wizard_idx = total
        st.rerun()
        return

    # ---- Núverandi spurning ----
    q = qs[idx]
    answered_count = sum(1 for q2 in qs if _is_question_answered(q2))
    progress_value = (idx) / total

    # Hero-titill
    type_label = ""
    if q.get("type") == "personality":
        type_label = '<span class="bk-pill" style="background:rgba(255,255,255,0.16);color:white;border:none;">Léttari spurning · engin áhrif á samsvörun</span>'
    elif q.get("type") == "chaos":
        type_label = '<span class="bk-pill" style="background:rgba(255,255,255,0.16);color:white;border:none;">Glundroði · algjörlega merkingarlaus</span>'
    else:
        type_label = '<span class="bk-pill" style="background:rgba(255,255,255,0.16);color:white;border:none;">Stefnu-spurning</span>'

    st.markdown(
        f"""
        <div class="bk-hero" style="padding:1.6rem 1.8rem;">
            <span class="bk-pill" style="background:rgba(255,255,255,0.16);color:white;border:none;">Spurning {idx + 1} af {total}</span>
            {type_label}
            <h1 style="margin-top:0.6rem;font-size:1.7rem;line-height:1.2;">{q['text']}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(progress_value, text=f"{answered_count} svör skráð · {idx} af {total} kláraðar")

    # Spurningin sjálf
    if q.get("type") == "chaos":
        render_chaos_question(q)
    else:
        # Líka persónuleika spurningar nota Likert
        render_likert_question(q)

    if q.get("help"):
        st.caption(q["help"])

    st.divider()

    # Navigation
    nav_back, nav_skip, nav_next = st.columns([1, 1, 1])
    with nav_back:
        if idx > 0:
            if st.button("← Til baka", use_container_width=True):
                st.session_state.wizard_idx = idx - 1
                st.rerun()
    with nav_skip:
        if not _is_question_answered(q):
            if st.button("Sleppa", use_container_width=True):
                st.session_state.wizard_idx = idx + 1
                st.rerun()
    with nav_next:
        is_last = (idx == total - 1)
        next_label = "Klára og sjá niðurstöður →" if is_last else "Áfram →"
        next_disabled = not _is_question_answered(q)
        if st.button(next_label, type="primary", use_container_width=True, disabled=next_disabled):
            if is_last:
                st.session_state.submitted = True
                st.session_state.wizard_idx = total
            else:
                st.session_state.wizard_idx = idx + 1
            st.rerun()
    if next_disabled:
        st.caption("Veldu svar (eða notaðu **Sleppa**) til að halda áfram.")


# ---------------------------------------------------------------------------
# Síða: Niðurstöður
# ---------------------------------------------------------------------------

def _try_radar_chart(top_results: list, user_axis: dict):
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None

    categories = [AXIS_LABELS[a] for a in AXIS_IDS]
    fig = go.Figure()

    # Notandinn sjálfur
    user_vals = [user_axis.get(a, 0) for a in AXIS_IDS]
    fig.add_trace(
        go.Scatterpolar(
            r=user_vals + [user_vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Þú",
            line=dict(color="#222", width=2),
            opacity=0.55,
        )
    )
    for r in top_results:
        p = r["party"]
        vals = [float(p["scores"].get(a, 0)) for a in AXIS_IDS]
        fig.add_trace(
            go.Scatterpolar(
                r=vals + [vals[0]],
                theta=categories + [categories[0]],
                name=f"{p['list_letter']} {p['short_name']}",
                line=dict(color=p["color"], width=2),
                opacity=0.85,
            )
        )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[-2.2, 2.2], tickvals=[-2, -1, 0, 1, 2]),
        ),
        showlegend=True,
        height=520,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def render_results():
    st.title("Niðurstöður")
    answered = sum(1 for q in policy_questions() if q["id"] in st.session_state.answers)
    if answered == 0:
        st.warning(
            "Þú hefur ekki svarað neinum stefnu-spurningum enn. "
            "Veldu „Spurningalisti“ í valmyndinni til vinstri til að byrja."
        )
        return

    if answered < len(policy_questions()):
        st.info(
            f"Þú hefur svarað {answered} af {len(policy_questions())} stefnu-spurningum. "
            "Niðurstaðan birtist út frá þeim svörum sem þegar liggja fyrir — "
            "þú getur farið aftur og klárað."
        )

    disclaimer_box(
        "Þetta er ekki ráðlegging um atkvæði. Tólið sýnir aðeins nánd milli þinna "
        "svara og skráðrar stefnu framboðanna á 12 stefnuásum."
    )

    qs_for_session = get_session_questions()
    ranking = rank_parties(st.session_state.answers, qs_for_session, PARTIES)
    user_axis = compute_user_axis_vector(st.session_state.answers, qs_for_session)

    top3 = ranking[:3]

    st.markdown("### 🥇 Þrjú framboð næst þínum svörum")
    st.caption(
        "Þín svör passa best við þessi framboð út frá þeim stefnuásum sem tólið mælir. "
        "Þetta er **ekki ráðlegging um atkvæði**, heldur samanburður á áherslum."
    )

    for idx, r in enumerate(top3):
        p = r["party"]
        match_pct = r["match"] * 100
        agree, disagree = biggest_agreements_and_disagreements(user_axis, p["scores"])
        rank_class = f"bk-rank-{idx + 1}"
        with st.container():
            st.markdown(
                f'<div class="bk-card bk-card-accent" style="--accent:{p["color"]};">',
                unsafe_allow_html=True,
            )
            cols = st.columns([1.1, 4, 2.2])
            with cols[0]:
                st.markdown(
                    f'<div style="display:flex;flex-direction:column;align-items:flex-start;gap:0.6rem;">'
                    f'<span class="bk-rank {rank_class}">{idx + 1}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                show_logo_or_pill(p)
            with cols[1]:
                st.markdown(f"### {p['list_letter']} — {p['short_name']}")
                st.markdown(
                    f"<span class='bk-mini'>{p['name']}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"_{p['summary']}_")
                if p.get("tagline") and p["tagline"] != DEFAULT_TAGLINE:
                    st.markdown(f"💬 *{p['tagline']}*")
            with cols[2]:
                st.markdown(
                    f"<div class='bk-big-pct-label'>Samsvörun</div>"
                    f"<div class='bk-big-pct' style='--accent:{p['color']};'>{match_pct:.0f}%</div>"
                    f'<div class="bk-match-bar-bg"><div class="bk-match-bar" '
                    f'style="width:{match_pct:.0f}%;background:{p["color"]};"></div></div>',
                    unsafe_allow_html=True,
                )

            ac_col, dc_col = st.columns(2)
            with ac_col:
                st.markdown("**Mestu samsvörun á ásum:**")
                for axis_id, agreement in agree:
                    st.markdown(
                        f"- {AXIS_LABELS[axis_id]} — {agreement*100:.0f}%"
                    )
            with dc_col:
                st.markdown("**Mest ósamstaða á ásum:**")
                for axis_id, agreement in disagree:
                    st.markdown(
                        f"- {AXIS_LABELS[axis_id]} — {agreement*100:.0f}%"
                    )

            if p.get("policy_url"):
                st.markdown(f"🔗 [Stefnuskrá / vefur]({p['policy_url']})")
            if p.get("uncertain_axes"):
                names = ", ".join(AXIS_LABELS[a] for a in p["uncertain_axes"])
                st.warning(f"⚠️ Óvissir ásar fyrir þetta framboð: {names}. Þarfnast staðfestingar.", icon="⚠️")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("**Lestu áður en þú kýst:** opinberar stefnuskrár framboða eru lokaorðið.")

    # ---- Nafnlaus gagnasöfnun ----
    render_data_collection_section(top3, user_axis)

    # ---- Deilanleiki ----
    render_share_section(top3, ranking)

    # ---- Radarrit ----
    st.divider()
    st.markdown("### 📈 Stefnuásar — þú á móti efstu þremur")
    fig = _try_radar_chart(top3, user_axis)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Plotly ekki uppsett — sleppi radar-riti.")

    # ---- Heildarröðun ----
    with st.expander("Sjá samsvörun við öll framboð"):
        rows = []
        for r in ranking:
            rows.append({
                "Listi": r["party"]["list_letter"],
                "Framboð": r["party"]["short_name"],
                "Samsvörun": f"{r['match']*100:.1f}%",
                "Óvíst (ásar)": len(r["party"].get("uncertain_axes", [])),
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # ---- Persónugerð (vibe) ----
    st.divider()
    render_personality_section(user_axis)


def render_data_collection_section(top3, user_axis):
    """Nafnlaus gagnasöfnun með áberandi samþykkis-yfirlýsingu.

    Persónuverndar-skýringin er ALLTAF sýnileg — bæði þegar Supabase er
    uppsett (raunveruleg söfnun) og þegar ekki (forskoðunar-háttur).
    """
    st.divider()
    st.markdown(
        '<div class="bk-bonus" style="background:linear-gradient(135deg,#eef3fa,#dbe7f4);'
        'border:1px solid #b9d7ec;">',
        unsafe_allow_html=True,
    )
    st.markdown("#### 🤝 Er í lagi að við geymum svarið þitt nafnlaust og órekjanlegt til greiningar?")

    # ---- Áberandi privacy-skýring (alltaf sýnileg) ----
    st.markdown(
        """
        <div style="background:white;border:1px solid #b9d7ec;border-radius:10px;
                    padding:1rem 1.1rem;margin-bottom:0.8rem;">
            <div style="display:flex;gap:1.2rem;flex-wrap:wrap;">
                <div style="flex:1;min-width:240px;">
                    <strong style="color:#1f6f43;">✅ Við söfnum:</strong>
                    <ul style="margin:0.3rem 0 0 1rem;padding:0;">
                        <li>Svörum þínum við spurningalistanum</li>
                        <li>Reiknuðum efstu 3 framboðum</li>
                        <li>Tíma og tilviljunarkenndu lotu-auðkenni</li>
                    </ul>
                </div>
                <div style="flex:1;min-width:240px;">
                    <strong style="color:#7a2222;">🚫 Við söfnum EKKI:</strong>
                    <ul style="margin:0.3rem 0 0 1rem;padding:0;">
                        <li><strong>Engin nöfn</strong></li>
                        <li><strong>Engin tölvupóstföng</strong></li>
                        <li><strong>Engin IP-tala eða staðsetning</strong></li>
                        <li><strong>Engin tenging við notendareikninga</strong> (Facebook, Google o.fl.)</li>
                    </ul>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if submissions.already_submitted():
        st.success(
            "Takk — svar þitt er þegar skráð nafnlaust. Þú getur áfram skoðað og deilt niðurstöðunum.",
            icon="✅",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if st.session_state.get("consent_skipped"):
        st.caption(
            "Þú slepptir því að deila gögnunum. Það er alveg fínt — "
            "niðurstaðan þín er bara fyrir þig."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if not submissions.is_configured():
        st.info(
            "ℹ️ Forskoðunar-háttur — gagnasöfnun er ekki uppsett í þessu umhverfi. "
            "Til að virkja: bættu Supabase-tengingu við Streamlit-secrets.",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.caption(
        "Gögnin eru notuð til að skoða heildardreifingu á svörum (t.d. hvaða framboð "
        "koma oftast efst). Þau verða aldrei seld eða framseld."
    )

    c1, c2 = st.columns([3, 2])
    with c1:
        if st.button("✅ Já — senda nafnlaust", type="primary", use_container_width=True):
            ok, msg = submissions.submit_response(
                answers_likert=st.session_state.answers,
                answers_chaos=st.session_state.chaos_answers,
                top3=top3,
                user_axis_vector=user_axis,
                evidence_summary={
                    "best_match_code": top3[0]["code"] if top3 else None,
                    "best_match_percent": round(top3[0]["match"] * 100, 1) if top3 else None,
                },
            )
            if ok:
                st.rerun()
            else:
                st.warning(msg, icon="⚠️")
    with c2:
        if st.button("Sleppa því", use_container_width=True):
            st.session_state.consent_skipped = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_share_section(top3, ranking):
    """Sýnir deilanlegan kassa með URL og forsniðnum texta + samfélagsmiðla-tengla."""
    token = encode_share_token(ranking)
    # Athugið: við skrifum EKKI sjálfvirkt í URL svo „Deilt frá vini“-banner
    # birtist ekki ranglega ef notandi ferskar sín eigin niðurstöður.
    text = share_text_for(top3)

    # Streamlit Cloud / sjálfvirk URL — ef ekki tilgreint, þá er þetta einfaldlega ?r=...
    relative_url = f"?r={token}"
    full_url_hint = relative_url

    # Notum HTML kassa fyrir áhrifaríkari útlit
    st.markdown('<div class="bk-share">', unsafe_allow_html=True)
    st.markdown("### 🔗 Deildu þínum niðurstöðum", unsafe_allow_html=True)
    st.markdown(
        "Smelltu á reitinn til að afrita. Slóðin er stutt og hleður beint þinni topp 3 niðurstöðu — "
        "vinir geta opnað hana og þá líka tekið prófið sjálfir.",
        unsafe_allow_html=True,
    )
    st.markdown("**Slóð (afrita):**")
    st.code(full_url_hint, language="text")
    st.markdown("**Texti fyrir samfélagsmiðla (afrita):**")
    st.code(text, language="text")

    # Beinir samfélagsmiðla-tenglar (fela URL inni í deilingar-link)
    import urllib.parse
    enc_text = urllib.parse.quote(text + "\n")
    enc_url = urllib.parse.quote(relative_url)
    cols = st.columns(4)
    with cols[0]:
        st.link_button(
            "Tísta (X / Twitter)",
            f"https://twitter.com/intent/tweet?text={enc_text}",
            use_container_width=True,
        )
    with cols[1]:
        st.link_button(
            "Deila á Bluesky",
            f"https://bsky.app/intent/compose?text={enc_text}",
            use_container_width=True,
        )
    with cols[2]:
        st.link_button(
            "Deila á Facebook",
            f"https://www.facebook.com/sharer/sharer.php?u={enc_url}",
            use_container_width=True,
        )
    with cols[3]:
        st.link_button(
            "Senda í tölvupósti",
            f"mailto:?subject=Borgarstjórnar%C2%ADkompás%202026&body={enc_text}",
            use_container_width=True,
        )
    st.markdown(
        "<span style='opacity:0.85;font-size:0.82rem;'>Þegar þú hýsir tólið "
        "(t.d. á streamlit.app) verða slóðirnar með fullri vefslóð sjálfkrafa — "
        "þú getur límt slóðina hér í tölvupóst, iMessage eða hvað sem er.</span>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_personality_section(user_axis: dict):
    personality_answered = any(q["id"] in st.session_state.answers for q in PERSONALITY_QUESTIONS)
    chaos_answered = any(q["id"] in st.session_state.chaos_answers for q in CHAOS_QUESTIONS)

    if not personality_answered and not chaos_answered:
        st.markdown(
            '<div class="bk-bonus">'
            '<h4>✨ Bónus: vibe-próf</h4>'
            'Þú slepptir vibe-prófinu. Það er virðingarverð ákvörðun. '
            'Ef þú vilt prófa, þá er það neðst á spurningalistasíðunni — '
            'það hefur engin áhrif á flokksamsvörun.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    tags = collect_personality_tags(st.session_state.answers, PERSONALITY_QUESTIONS)
    archetypes = select_archetypes(tags)

    st.markdown('<div class="bk-bonus">', unsafe_allow_html=True)
    st.markdown("#### ✨ Persónugerð (bara til gamans)")
    st.caption(
        "Þetta hefur **engin áhrif** á flokksamsvörun. Algjörlega óvísindalegt og "
        "byggt aðeins á svörum þínum við vibe-prófinu."
    )

    if archetypes:
        for arc in archetypes:
            st.markdown(
                f"**{arc['label_is']}**  \n"
                f"<span class='bk-mini'><em>{arc['label_en']}</em></span>  \n"
                f"{arc['description']}",
                unsafe_allow_html=True,
            )
    score, label = chaos_score(st.session_state.chaos_answers, CHAOS_QUESTIONS)
    if score > 0:
        st.markdown(
            f"**🌀 Glundroðagildi:** `{score} / 100` — *{label}*  \n"
            f"<span class='bk-mini'>(Þessi tala þýðir alls ekki neitt og breytist milli keyrsla.)</span>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Síða: Samanburður
# ---------------------------------------------------------------------------

COMPARE_AXES = [
    ("borgarlina", "Samgöngur"),
    ("husnaedi",   "Húsnæði"),
    ("velferd",    "Velferð"),
    ("skattar",    "Skattar / útgjöld"),
    ("loftslag",   "Loftslag"),
    ("skolar",     "Skólar / fjölskyldur"),
    ("lydraedi",   "Lýðræði / gagnsæi"),
    ("innflytjendur", "Inngilding"),
    ("atvinnu",    "Atvinna / skilvirkni"),
]


def render_comparison():
    st.title("Samanburður á stefnu framboða")
    disclaimer_box(
        "Stigatöflur fyrir hvert framboð eru bráðabirgða mat sem þarf að staðfesta "
        "handvirkt. Notaðu töfluna sem útgangspunkt, ekki sem endanlega heimild."
    )

    st.markdown(
        "Hver klefi sýnir stigatölu framboðs á viðkomandi stefnusviði — frá "
        "**−2** (sterk andstaða / lágur forgangur) til **+2** (sterkur stuðningur / "
        "hár forgangur). Klefar merktir „óvíst“ benda til þess að okkur skorti "
        "áreiðanlega heimild."
    )

    # Töflu með HTML svo við getum litað og merkt óvissu.
    header = ["Stefnusvið"] + [PARTIES[c]["list_letter"] for c in PARTY_ORDER]
    sub_header = [""] + [PARTIES[c]["short_name"] for c in PARTY_ORDER]

    html = ['<div style="overflow-x:auto;">']
    html.append('<table style="border-collapse:collapse;width:100%;font-size:0.9rem;">')
    html.append('<thead>')
    html.append('<tr>' + "".join(
        f'<th style="text-align:left;padding:6px 8px;border-bottom:1px solid #d8dbe3;">{h}</th>'
        for h in header
    ) + '</tr>')
    html.append('<tr>' + "".join(
        f'<th style="text-align:left;padding:0 8px 6px 8px;border-bottom:2px solid #c7cbd6;'
        f'font-weight:400;color:#5a6378;font-size:0.78rem;">{h}</th>'
        for h in sub_header
    ) + '</tr>')
    html.append('</thead><tbody>')

    for axis_id, label in COMPARE_AXES:
        row = [f'<td style="padding:8px;border-bottom:1px solid #eef0f6;font-weight:600;">{label}</td>']
        for code in PARTY_ORDER:
            p = PARTIES[code]
            score = float(p["scores"].get(axis_id, 0))
            uncertain = axis_id in p.get("uncertain_axes", [])
            row.append(
                f'<td style="padding:8px;border-bottom:1px solid #eef0f6;text-align:center;">'
                f'{axis_score_chip(score, uncertain)}'
                f'</td>'
            )
        html.append("<tr>" + "".join(row) + "</tr>")
    html.append("</tbody></table></div>")

    st.markdown("\n".join(html), unsafe_allow_html=True)

    st.divider()
    st.markdown("### Stutt yfirlit á hvert framboð")
    cols = st.columns(2)
    for i, code in enumerate(PARTY_ORDER):
        p = PARTIES[code]
        with cols[i % 2]:
            st.markdown(f"#### {p['list_letter']} — {p['short_name']}")
            st.markdown(p["summary"])
            if p.get("tagline") and p["tagline"] != DEFAULT_TAGLINE:
                st.markdown(f"💬 *{p['tagline']}*")
            if p.get("policy_url"):
                st.markdown(f"🔗 [Stefnuskrá / vefur]({p['policy_url']})")
            if p.get("notes"):
                st.markdown(f"<span class='bk-mini'>📝 {p['notes']}</span>", unsafe_allow_html=True)
            if p.get("uncertain_axes"):
                names = ", ".join(AXIS_LABELS[a] for a in p["uncertain_axes"])
                st.markdown(
                    f"<span class='bk-uncertain'>óvíst</span> "
                    f"<span class='bk-mini'>{names}</span>",
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Síða: Stefnu-fylki (deep-dive á rekstrarásum)
# ---------------------------------------------------------------------------

CERTAINTY_BADGE = {
    "high":   ("Há vissa", "#1f6f43", "#dff2e6"),
    "medium": ("Miðlungs vissa", "#7a5b00", "#fff5e0"),
    "low":    ("Lág vissa", "#7a2222", "#f6e8e8"),
}


def cert_badge(level: str) -> str:
    label, color, bg = CERTAINTY_BADGE.get(level, CERTAINTY_BADGE["low"])
    return (
        f'<span style="display:inline-block;background:{bg};color:{color};'
        f'border:1px solid {color}33;border-radius:4px;padding:1px 7px;'
        f'font-size:0.78rem;">{label}</span>'
    )


def matrix_score_chip(score: int, certainty: str, tooltip: str | None = None) -> str:
    if score > 0:
        bg, border, color = "#e7f1f9", "#b9d7ec", "#1f4e8c"
    elif score < 0:
        bg, border, color = "#f6e8e8", "#e0bcbc", "#7a2222"
    else:
        bg, border, color = "#f1f2f5", "#d8dbe3", "#3a4254"

    # Sjón­ræn aðgreining á vissustigi: solid fyrir háa, hálfgegnsætt fyrir miðlungs,
    # punkta-rammi + dauflituð fyrir lág.
    if certainty == "high":
        opacity = "1"
        border_style = "solid"
        cert_marker = ""
    elif certainty == "medium":
        opacity = "0.78"
        border_style = "solid"
        cert_marker = " ·"
    else:
        opacity = "0.55"
        border_style = "dashed"
        cert_marker = " ⚠️"

    title_attr = ""
    if tooltip:
        # CommonMark interprets blank lines inside raw HTML as ending the tag,
        # so flatten any newlines to a separator and escape quotes.
        safe = (
            tooltip.replace("\r", "")
                   .replace("\n", " · ")
                   .replace('"', "&quot;")
        )
        # collapse multiple separators
        while " ·  · " in safe:
            safe = safe.replace(" ·  · ", " · ")
        title_attr = f' title="{safe}"'

    return (
        f'<span{title_attr} style="display:inline-block;background:{bg};border:1px {border_style} {border};'
        f'color:{color};padding:1px 7px;border-radius:5px;font-size:0.82rem;'
        f'min-width:42px;text-align:center;opacity:{opacity};">'
        f'{score:+d}{cert_marker}</span>'
    )


def render_policy_matrix():
    st.title("Stefnu-fylki")
    st.markdown(
        "Þessi síða ber saman framboð á **20 rekstrar-ásum** — það er, hvar þau "
        "raunverulega standa á áþreifanlegum ákvörðunum, ekki hvaða orð þau nota."
    )
    disclaimer_box(
        "Stigatöflurnar hér eru bráðabirgða mat sem þarf að staðfesta gegn opinberum "
        "stefnuskrám. ⚠️ merkir lág vissa, · merkir miðlungs vissa. Sjá DATA_REVIEW.md."
    )

    # ---- Heildarvissa per framboð ----
    st.markdown("### 🔎 Vissustig á hverju framboði")
    cols = st.columns(4)
    for i, code in enumerate(PARTY_ORDER):
        p = PARTIES[code]
        cert = get_certainty(code)
        with cols[i % 4]:
            st.markdown(
                f'<div class="bk-card" style="--accent:{p["color"]};">'
                f'{render_letter_pill(p["list_letter"], p["color"])}'
                f'<strong>{p["short_name"]}</strong><br/>'
                f'{cert_badge(cert)}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ---- Helstu greiningarpunktar ----
    st.divider()
    a_col, b_col, c_col = st.columns(3)
    with a_col:
        st.markdown("#### ⚔️ Stærstu andstæðingar")
        for x, y, dist in strongest_opposites(3):
            st.markdown(
                f"- **{x} {PARTIES[x]['short_name']}** ↔ "
                f"**{y} {PARTIES[y]['short_name']}** "
                f"<span class='bk-mini'>(vegalengd {dist})</span>",
                unsafe_allow_html=True,
            )
    with b_col:
        st.markdown("#### 🤝 Líkust prófíl")
        for x, y, dist in most_similar_pairs(3):
            st.markdown(
                f"- **{x} {PARTIES[x]['short_name']}** ≈ "
                f"**{y} {PARTIES[y]['short_name']}** "
                f"<span class='bk-mini'>(vegalengd {dist})</span>",
                unsafe_allow_html=True,
            )
    with c_col:
        st.markdown("#### 💥 Mest ósamstaða")
        for axis_id, spread in biggest_disagreement_axes(5):
            st.markdown(
                f"- {POLICY_AXIS_LOOKUP[axis_id]['label']} "
                f"<span class='bk-mini'>(spread {spread})</span>",
                unsafe_allow_html=True,
            )

    overlap_axes = axes_where_parties_overlap()
    if overlap_axes:
        st.markdown("#### 🪢 Þar sem flest framboð eru sammála")
        st.markdown(
            ", ".join(POLICY_AXIS_LOOKUP[a]["label"] for a in overlap_axes)
            + ".  \n*<span class='bk-mini'>(Stigamunur ≤ 1 milli flestra framboða.)</span>*",
            unsafe_allow_html=True,
        )

    # ---- Heildar fylkið, flokkað eftir málefnaflokki ----
    st.divider()
    st.markdown("### 📊 Allt fylkið — eftir málefnaflokkum")
    st.caption(
        "Hver klefi: stigatala (-2..+2). ⚠️ = lág vissa, · = miðlungs vissa. "
        "Smelltu á flokk til að rúlla niður."
    )

    for group in POLICY_AXIS_GROUPS:
        with st.expander(f"📌 {group}", expanded=(group == "Samgöngur")):
            html = ['<div style="overflow-x:auto;">']
            html.append('<table style="border-collapse:collapse;width:100%;font-size:0.88rem;">')
            html.append("<thead><tr>")
            html.append('<th style="text-align:left;padding:6px 8px;border-bottom:1px solid #d8dbe3;">Ás</th>')
            for code in PARTY_ORDER:
                p = PARTIES[code]
                html.append(
                    f'<th style="text-align:center;padding:6px 8px;border-bottom:1px solid #d8dbe3;">'
                    f'<div style="display:inline-block;width:1.7rem;height:1.7rem;border-radius:50%;'
                    f'background:{p["color"]};color:white;line-height:1.7rem;font-weight:700;font-size:0.85rem;">'
                    f'{p["list_letter"]}</div></th>'
                )
            html.append("</tr></thead><tbody>")
            for axis in POLICY_AXES:
                if axis["group"] != group:
                    continue
                html.append("<tr>")
                html.append(
                    f'<td style="padding:8px;border-bottom:1px solid #eef0f6;">'
                    f'<strong>{axis["label"]}</strong><br/>'
                    f'<span class="bk-mini">{axis["description"]}</span>'
                    f'</td>'
                )
                for code in PARTY_ORDER:
                    detail = get_detail(code, axis["id"])
                    tooltip = (
                        f"{PARTIES[code]['short_name']} · vissa: {detail['certainty']} — "
                        f"{detail['reason']}"
                    )
                    html.append(
                        f'<td style="padding:8px;border-bottom:1px solid #eef0f6;text-align:center;">'
                        f'{matrix_score_chip(detail["score"], detail["certainty"], tooltip)}'
                        f'</td>'
                    )
                html.append("</tr>")
            html.append("</tbody></table></div>")
            st.markdown("\n".join(html), unsafe_allow_html=True)

    # ---- Per-party djúprýni ----
    st.divider()
    st.markdown("### 🎯 Djúprýni á hvert framboð")
    chosen_code = st.selectbox(
        "Veldu framboð",
        PARTY_ORDER,
        format_func=lambda c: f"{c} — {PARTIES[c]['short_name']}",
    )
    p = PARTIES[chosen_code]
    cert = get_certainty(chosen_code)
    cols = st.columns([1, 2])
    with cols[0]:
        show_logo_or_pill(p, height=80)
        st.markdown(cert_badge(cert), unsafe_allow_html=True)
        if p.get("policy_url"):
            st.markdown(f"🔗 [Stefnuskrá / vefur]({p['policy_url']})")
    with cols[1]:
        st.markdown(f"### {p['list_letter']} — {p['name']}")
        st.markdown(p["summary"])
        if p.get("notes"):
            st.markdown(f"<span class='bk-mini'>📝 {p['notes']}</span>", unsafe_allow_html=True)

    pri = strongest_priorities(chosen_code)
    opp = strongest_oppositions(chosen_code)
    amb = ambiguous_axes(chosen_code)
    cont = potential_contradictions(chosen_code)

    a, b = st.columns(2)
    with a:
        st.markdown("**Sterkustu áherslur:**")
        if pri:
            for axis_id, score in pri:
                st.markdown(f"- {POLICY_AXIS_LOOKUP[axis_id]['label']} `{score:+d}`")
        else:
            st.markdown("*Engin sterk áhersla skráð (eða allt 0).*")
    with b:
        st.markdown("**Sterkustu andstöður:**")
        if opp:
            for axis_id, score in opp:
                st.markdown(f"- {POLICY_AXIS_LOOKUP[axis_id]['label']} `{score:+d}`")
        else:
            st.markdown("*Engin sterk andstaða skráð.*")

    if amb:
        st.markdown("**Óljósir / blandaðir ásar:**")
        st.markdown(", ".join(POLICY_AXIS_LOOKUP[a]["label"] for a in amb))

    if cont:
        st.markdown("**Mögulegar mótsagnir (heuristic):**")
        for label, desc in cont:
            st.warning(f"{label} — {desc}", icon="🔀")

    # Heimildir og röksemd á hvern ás — full gegnsæi
    st.markdown("**Heimildir og röksemd á hvern ás:**")
    evidence = round(overall_evidence_score(chosen_code) * 100)
    st.caption(
        f"Heildar-vissa á þessu framboði: **{evidence}%** "
        f"(byggt á vegnu meðaltali yfir 20 ása)."
    )
    for group in POLICY_AXIS_GROUPS:
        with st.expander(f"📌 {group}", expanded=False):
            for axis in POLICY_AXES:
                if axis["group"] != group:
                    continue
                detail = get_detail(chosen_code, axis["id"])
                cert = detail["certainty"]
                cert_label, cert_text_color, cert_bg = CERTAINTY_BADGE.get(cert, CERTAINTY_BADGE["low"])
                src_html = ""
                if detail["sources"]:
                    src_html = " · " + " · ".join(
                        f'<a href="{s}" target="_blank">heimild</a>' for s in detail["sources"]
                    )
                else:
                    src_html = " · <span style='opacity:0.7;'>engin heimild skráð</span>"
                st.markdown(
                    f"<div style='border:1px solid #e3e6ee;border-radius:8px;padding:8px 12px;margin-bottom:6px;'>"
                    f"<strong>{axis['label']}</strong> "
                    f"{matrix_score_chip(detail['score'], cert)}"
                    f" {cert_badge(cert)}<br/>"
                    f"<span class='bk-mini'>{detail['reason']}{src_html}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Síða: Hópgögn — lifandi tölfræði (uppfærist sjálfkrafa á 60 sek)
# ---------------------------------------------------------------------------

def _archetype_label_lookup() -> dict:
    """Map archetype id → íslenskt label. Fela arketýpur sem ekki er hægt að uppfletta."""
    from chaos import ARCHETYPES
    return {a["id"]: a["label_is"] for a in ARCHETYPES}


def _render_race_chart(rows: list[dict], row_key: str, height_per_row: int = 56,
                        max_categories: int = 12):
    """Stacked horizontal bar chart — race-style. Hver röð er kategoría,
    segmenti eru framboð, lengd = fjöldi. Stærsti hluti vinnur „kapphlaupið“."""
    if not rows:
        st.caption("Engin gögn ennþá.")
        return
    df = pd.DataFrame(rows)
    if df.empty:
        st.caption("Engin gögn ennþá.")
        return

    try:
        import plotly.express as px
    except ImportError:
        st.dataframe(df, use_container_width=True)
        return

    # Halda eftir top-N kategoría í sample (mest svar)
    cat_totals = df.groupby(row_key)["n"].sum().sort_values(ascending=False)
    keep = cat_totals.head(max_categories).index.tolist()
    df = df[df[row_key].isin(keep)].copy()

    # Röð: vinsælasta kategoría neðst (Plotly bar y-as gengur upp)
    cat_order = cat_totals.head(max_categories).index.tolist()[::-1]
    df[row_key] = pd.Categorical(df[row_key], categories=cat_order, ordered=True)

    # Innan hverrar staflu — raða eftir kjörseðils-röð svo litir séu samkvæmir
    party_index = {c: i for i, c in enumerate(PARTY_ORDER)}
    df["__party_order"] = df["list_letter"].map(lambda c: party_index.get(c, 999))
    df = df.sort_values([row_key, "__party_order"])

    color_map = {c: PARTIES[c]["color"] for c in df["list_letter"].unique() if c in PARTIES}

    fig = px.bar(
        df,
        x="n",
        y=row_key,
        color="list_letter",
        color_discrete_map=color_map,
        orientation="h",
        text="list_letter",
        custom_data=["party_name", "n"],
        labels={"n": "Fjöldi", row_key: "", "list_letter": "Framboð"},
    )
    fig.update_traces(
        textposition="inside",
        textfont=dict(size=12, color="white", family="Inter, sans-serif"),
        insidetextanchor="middle",
        hovertemplate="<b>%{customdata[0]}</b><br>Fjöldi: %{customdata[1]}<extra></extra>",
        marker=dict(line=dict(width=1, color="white")),
    )
    n_cats = len(cat_order)
    fig.update_layout(
        barmode="stack",
        height=max(220, 80 + height_per_row * n_cats),
        margin=dict(l=10, r=10, t=20, b=20),
        showlegend=True,
        legend=dict(orientation="h", y=-0.18, title=""),
        xaxis=dict(showgrid=True, gridcolor="#eef0f6", title="", zeroline=False, dtick=1),
        yaxis=dict(showgrid=False, title=""),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _party_chip(code: str, count: int, big: bool = False) -> str:
    """Lítill (eða stór) hringlaga merki með listabókstaf og fjölda."""
    p = PARTIES.get(code)
    if not p:
        return ""
    color = p["color"]
    if big:
        return (
            f'<div style="display:inline-flex;align-items:center;gap:0.55rem;'
            f'background:linear-gradient(135deg,{color},{color}dd);color:white;'
            f'padding:0.55rem 0.95rem;border-radius:14px;font-weight:700;'
            f'box-shadow:0 4px 12px {color}55;">'
            f'<span style="font-size:1.5rem;">{p["list_letter"]}</span>'
            f'<span style="display:flex;flex-direction:column;line-height:1.05;">'
            f'<span style="font-size:0.95rem;">{p["short_name"]}</span>'
            f'<span style="font-size:0.78rem;opacity:0.92;font-weight:500;">'
            f'{count} {"svar" if count == 1 else "svör"}</span></span></div>'
        )
    return (
        f'<span style="display:inline-flex;align-items:center;gap:0.3rem;'
        f'background:{color}1a;border:1px solid {color}55;color:{color};'
        f'padding:2px 9px;border-radius:999px;font-size:0.82rem;'
        f'font-weight:600;margin-right:0.3rem;">'
        f'<span style="background:{color};color:white;width:1.1rem;height:1.1rem;'
        f'border-radius:50%;display:inline-flex;align-items:center;'
        f'justify-content:center;font-size:0.7rem;font-weight:800;">'
        f'{p["list_letter"]}</span>{count}</span>'
    )


def _render_champion_panel(rows: list[dict], row_key: str, row_emoji: str = ""):
    """Fyrir hverja flokku-mögulega gildi (t.d. skóstærð) sýnir 'sigurvegara'
    og hin framboðin sem litla chips. Mun skýrara en heatmap."""
    if not rows:
        st.caption("Engin gögn ennþá.")
        return
    df = pd.DataFrame(rows)
    if df.empty:
        st.caption("Engin gögn ennþá.")
        return

    for category, group in df.groupby(row_key, sort=False):
        sorted_group = group.sort_values("n", ascending=False).reset_index(drop=True)
        total = int(sorted_group["n"].sum())
        top_row = sorted_group.iloc[0]
        winners = sorted_group[sorted_group["n"] == top_row["n"]]
        runners = sorted_group.iloc[len(winners):]

        winners_html = " ".join(
            _party_chip(r["list_letter"], int(r["n"]), big=True)
            for _, r in winners.iterrows()
        )
        runners_html = ""
        if len(runners) > 0:
            runners_html = (
                "<div style='margin-top:0.55rem;'>"
                "<span style='font-size:0.78rem;color:#5a6378;margin-right:0.4rem;'>einnig:</span>"
                + " ".join(
                    _party_chip(r["list_letter"], int(r["n"]), big=False)
                    for _, r in runners.iterrows()
                )
                + "</div>"
            )

        crown = "🥇" if len(winners) == 1 else "🤝"
        st.markdown(
            f"""
            <div style="border:1px solid #e3e6ee;border-radius:14px;
                        padding:0.85rem 1.05rem;margin-bottom:0.7rem;background:white;
                        box-shadow:0 1px 3px rgba(15,23,42,0.04);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;
                            gap:1rem;flex-wrap:wrap;">
                    <div>
                        <div style="font-size:0.78rem;color:#5a6378;text-transform:uppercase;
                                    letter-spacing:0.06em;font-weight:600;">{row_emoji} {category}</div>
                        <div style="font-size:0.86rem;color:#3a4254;margin-top:0.15rem;">
                            {total} svar samtals · {crown} {'sigurvegari' if len(winners) == 1 else 'jafntefli'}
                        </div>
                    </div>
                    <div style="text-align:right;">{winners_html}</div>
                </div>
                {runners_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_aggregates_page():
    st.title("📊 Hópgögn — lifandi tölfræði")

    if not submissions.is_configured():
        st.info(
            "Gagnasöfnun er ekki uppsett í þessu umhverfi. "
            "Þessi síða birtir niðurstöður um leið og Supabase-tenging er virk."
        )
        return

    disclaimer_box(
        "Allar tölur hér eru úr nafnlausum svörum sem notendur hafa SAMÞYKKT "
        "að deila. Engin nöfn, engar IP-tölur, engar notendatengingar — aðeins "
        "samanteknar tölur. Tölfræði getur verið skökk í litlu úrtaki."
    )

    total = submissions.fetch_total()

    if st.button("🔄 Endurnýja gögn"):
        submissions.clear_aggregate_cache()
        st.rerun()
    st.caption("Gögn eru cached í 60 sek. — refresh til að ná nýjustu svörum strax.")

    if total == 0:
        st.info("Engin svör hafa enn verið skráð. Komdu aftur eftir smá.")
        return

    # ------- 1. Top-1 framboð: bar chart -------
    st.divider()
    st.markdown("### 🥇 Hvaða framboð kemur oftast efst?")
    counts = submissions.fetch_top1_counts()
    if counts:
        try:
            import plotly.express as px
            df = pd.DataFrame(counts)
            df = df.sort_values("n", ascending=False)
            df["litur"] = df["list_letter"].map(lambda c: PARTIES[c]["color"] if c in PARTIES else "#6b7a99")
            fig = px.bar(
                df, x="party_name", y="n",
                color="list_letter",
                color_discrete_map={c: PARTIES[c]["color"] for c in df["list_letter"] if c in PARTIES},
                labels={"party_name": "Framboð", "n": "Fjöldi sem fékk það efst"},
                text="n",
            )
            fig.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=20, b=10))
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.dataframe(pd.DataFrame(counts), hide_index=True, use_container_width=True)
    else:
        st.caption("Engin gögn ennþá.")

    # ------- 2. Persónugerð × framboð -------
    st.divider()
    st.markdown("### 🧠 Persónugerð × framboð")
    st.caption("Kapphlaup persónugerða — hver hefur stærsta hluta hverrar línu? Bara til gamans.")
    arch_rows = submissions.fetch_archetype_x_party()
    # Sleppa fallback-arketýpum (þær merkja „ekkert mynstur fannst“)
    arch_rows = [
        r for r in (arch_rows or [])
        if not str(r.get("archetype_id", "")).startswith("fallback_")
    ]
    if arch_rows:
        labels = _archetype_label_lookup()
        for row in arch_rows:
            row["archetype_label"] = labels.get(row.get("archetype_id"), row.get("archetype_id"))
        _render_race_chart(arch_rows, row_key="archetype_label")
    else:
        st.caption("Engin persónugerðar-gögn ennþá.")

    # ------- 3. Skóstærð × framboð -------
    st.divider()
    st.markdown("### 👟 Skóstærð × framboð")
    st.caption("Hin lengi - langþráða Reykvíska samsvörunarrannsókn. Hver er skóstærð mögulegra kjósenda flokkanna?")
    shoe_rows = submissions.fetch_shoe_x_party()
    if shoe_rows:
        size_order = ["Undir 36", "36–39", "40–43", "44–46", "Yfir 46", "Vil ekki segja"]
        for row in shoe_rows:
            row["_sort"] = size_order.index(row["shoe_size"]) if row["shoe_size"] in size_order else 999
        shoe_rows.sort(key=lambda r: r["_sort"])
        _render_race_chart(shoe_rows, row_key="shoe_size")
    else:
        st.caption("Engin skóstærðar-gögn ennþá.")

    # ------- 4. Sundlaug × framboð -------
    st.divider()
    st.markdown("### 🏊 Uppáhalds sundlaug × framboð")
    st.caption("Sjáið hvaða sundlaug býr til hvaða pólitík.")
    pool_rows = submissions.fetch_pool_x_party()
    if pool_rows:
        _render_race_chart(pool_rows, row_key="laug")
    else:
        st.caption("Engin laugar-gögn ennþá.")

    st.divider()
    st.caption(
        "📌 Tölfræðilegur fyrirvari: smáar krosstöflur eru ekki marktækar. "
        "Þetta er fyrst og fremst skemmtilegt yfirlit, ekki vísindarit."
    )


# ---------------------------------------------------------------------------
# Síða: Aðferðafræði
# ---------------------------------------------------------------------------

def render_methodology():
    st.title("Aðferðafræði")
    disclaimer_box(
        "Markmið þessarar síðu er að gera allt útreikningskerfið gegnsætt. "
        "Ef eitthvað er óljóst eða rangt — leiðréttu það beint í kóðanum. "
        "Tólið er ekki ráðgjöf, heldur reiknitól."
    )

    st.markdown(
        """
### Hvernig reiknast samsvörun?

1. **Þú svarar** spurningu á 5 punkta kvarða (-2 til +2).
2. Hver spurning tengist einum eða fleiri **stefnuásum** með skilgreindri þyngd.
3. Fyrir hvert framboð reiknum við **„afstöðu þess“ á spurningunni** sem vegið
   meðaltal stiga þess á tengdum ásum (klippt í [-2, +2]).
4. Vegalengdin milli þíns svars og afstöðu framboðs er |svar − afstaða|.
5. Hámarksvegalengd er 4 (frá -2 til +2). Samsvörun á spurningunni er
   `1 − (vegalengd / 4)`, gildi á bilinu 0..1.
6. Heildarsamsvörun framboðs er meðaltal samsvörunar yfir allar svaraðar spurningar.

Allar tölur eru rekjanlegar beint í kóðanum (`scoring.py`).
        """
    )

    st.markdown("### Stefnuásarnir 12")
    rows = []
    for axis_id, label in AXES:
        rows.append({"Ás": label, "Stefna": AXIS_DIRECTION_NOTES.get(axis_id, "")})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    st.markdown("### Yfirlit yfir spurningar")
    st.caption(
        "Aðeins **stefnuspurningar (policy)** hafa áhrif á samsvörun. "
        "Persónuleika- og glundroðaspurningar hafa engin áhrif og eru aðeins notaðar "
        "í gamansamri persónugerð."
    )
    qrows = []
    for q in policy_questions():
        qrows.append({
            "Auðkenni": q["id"],
            "Spurning": q["text"],
            "Tengdir ásar": ", ".join(f"{AXIS_LABELS[a]} ({w:+.1f})" for a, w in q["axes"]),
        })
    st.dataframe(pd.DataFrame(qrows), hide_index=True, use_container_width=True)

    st.markdown("### Mikilvægir fyrirvarar")
    st.markdown(
        """
- **Stigagjöf framboða er handvirk og bráðabirgða.** Sjá `DATA_REVIEW.md`
  fyrir lista yfir það sem þarf að staðfesta — þ.m.t. lógó, vefslóðir, slagorð
  og einstök stig.
- **Sumir ásar eru merktir „óvíst“** fyrir tiltekin framboð. Þetta er bein
  yfirlýsing um að okkur skorti góða heimild og á að lesa sem viðvörun.
- **Tólið mælir ekki með neinu framboði**, hvorki opinskátt né duldra.
- **Persónuleika- og glundroðaspurningar hafa engin áhrif** á flokksamsvörun.
  Þær eru aðeins notaðar í gamansaman persónugerðar-kassa á niðurstöðusíðu.
- **Lestu stefnuskrár framboðanna** á opinberum vefjum þeirra áður en þú kýst.
        """
    )

    st.markdown("### Heimildir")
    for code in PARTY_ORDER:
        p = PARTIES[code]
        st.markdown(f"**{p['list_letter']} — {p['short_name']}**")
        if p.get("sources"):
            for src in p["sources"]:
                st.markdown(f"- [{src}]({src})")
        else:
            st.markdown("- *(engar heimildir skráðar — þarf að bæta við)*")


# ---------------------------------------------------------------------------
# Síðu-stýring
# ---------------------------------------------------------------------------

render_shared_banner_if_present()

if page == "Wizard":
    render_wizard()
elif page == "Upphafssíða":
    render_landing()
elif page == "Niðurstöður":
    render_results()
elif page == "Samanburður":
    render_comparison()
elif page == "Stefnu-fylki":
    render_policy_matrix()
elif page == "Hópgögn":
    render_aggregates_page()
elif page == "Aðferðafræði":
    render_methodology()


# ---------------------------------------------------------------------------
# Föst niðurstöðulína á öllum síðum
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Borgarstjórnar­kompás Reykjavíkur 2026 — óháð, opinn samanburðartól. "
    "Þetta er ekki kosningaráðgjöf. Lestu stefnuskrár framboðanna sjálf/ur áður en þú kýst."
)
