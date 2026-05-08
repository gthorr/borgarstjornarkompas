#!/usr/bin/env python3
"""Generate 11 fully-answered dummy submissions, one per party.

Hver dummy færsla er merkt með ``app_version = "dummy-v1"`` svo hægt er að
fjarlægja þær síðar með einu SQL-skipun:

    delete from public.kompas_responses where app_version = 'dummy-v1' where true;
    select public._kompas_recompute_aggregates();

Notar sömu anon-leið og raunveruleg appið — ef þetta keyrir þá keyrir appið.

Notkun:
    SUPABASE_URL=https://...  SUPABASE_ANON_KEY=eyJ...  python3 scripts/seed_dummy_data.py
"""

from __future__ import annotations

import json
import os
import random
import sys
import uuid
from pathlib import Path

# Gerir kleift að keyra úr scripts/-möppunni eða úr verkefnaroot.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import requests

from parties import PARTIES, PARTY_ORDER
from questions import QUESTIONS, PERSONALITY_QUESTIONS, CHAOS_QUESTIONS, ALL_QUESTIONS
from scoring import rank_parties, compute_user_axis_vector, implied_party_position
from chaos import collect_personality_tags, select_archetypes


def answers_favoring(target_code: str, noise: float = 0.9) -> dict:
    """Likert-svör sem fylgja stefnu tiltekins framboðs með breitilega óvissu."""
    target = PARTIES[target_code]
    answers = {}
    for q in QUESTIONS:
        pos = implied_party_position(target, q)
        # Stærri hávaði → meira raunsæ kjósenda-blanda. Sumar spurningar
        # detta yfir „rétta megin” jafnvel þó kjósandinn fylgi ekki framboðinu
        # 100%.
        noisy = pos + random.uniform(-noise, noise)
        # 12% líkur á að kjósandinn taki þvert á flokkinn á þessari spurningu
        if random.random() < 0.12:
            noisy = -noisy + random.uniform(-0.5, 0.5)
        answers[q["id"]] = max(-2, min(2, int(round(noisy))))
    return answers


# Hlutfallslegar líkur á því að kjósandi ganga með hverju framboði — gróft mat
# sem endurspeglar stærri-flokka-bias (Samfylking, Sjálfstæðisflokkur, Píratar...).
# Þetta er BARA fyrir dummy-gögn og verður fjarlægt þegar nógu margir
# raunverulegir kjósendur hafa svarað.
PARTY_WEIGHTS = {
    "S": 0.25,
    "D": 0.18,
    "P": 0.10,
    "C": 0.09,
    "F": 0.07,
    "J": 0.07,
    "A": 0.06,
    "B": 0.06,
    "M": 0.05,
    "R": 0.04,
    "G": 0.03,
}


def sample_target_party() -> str:
    codes = list(PARTY_WEIGHTS.keys())
    weights = [PARTY_WEIGHTS[c] for c in codes]
    return random.choices(codes, weights=weights, k=1)[0]


def random_personality() -> dict:
    return {q["id"]: random.choice([-2, -1, 0, 1, 2]) for q in PERSONALITY_QUESTIONS}


def random_chaos() -> dict:
    return {q["id"]: random.choice(q["options"]) for q in CHAOS_QUESTIONS}


def build_submission(target_code: str) -> dict:
    policy_likert = answers_favoring(target_code)
    personality_likert = random_personality()
    chaos = random_chaos()

    all_likert = {**policy_likert, **personality_likert}

    tags = collect_personality_tags(personality_likert, PERSONALITY_QUESTIONS)
    archetypes = select_archetypes(tags, seed=random.randint(0, 1_000_000))
    archetype_ids = [a["id"] for a in archetypes]

    ranking = rank_parties(all_likert, ALL_QUESTIONS, PARTIES)
    top3 = [
        {
            "code": r["code"],
            "match_percent": round(r["match"] * 100, 1),
            "short_name": r["party"]["short_name"],
        }
        for r in ranking[:3]
    ]

    user_axis = compute_user_axis_vector(all_likert, ALL_QUESTIONS)
    user_axis = {k: round(float(v), 3) for k, v in user_axis.items()}

    return {
        "client_session": str(uuid.uuid4()),
        "consented": True,
        "answers_likert": {k: int(v) for k, v in all_likert.items()},
        "answers_chaos": chaos,
        "top3": top3,
        "user_axis_vector": user_axis,
        "evidence_summary": {
            "best_match_code": top3[0]["code"],
            "best_match_percent": top3[0]["match_percent"],
        },
        "archetype_ids": archetype_ids,
        "app_version": "dummy-v1",
    }


def post(url: str, key: str, payload: dict) -> tuple[int, str]:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    r = requests.post(
        f"{url.rstrip('/')}/rest/v1/kompas_responses",
        headers=headers,
        data=json.dumps(payload),
        timeout=15,
    )
    return r.status_code, r.text


def main():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not (url and key):
        sys.exit("SUPABASE_URL og SUPABASE_ANON_KEY þurfa að vera sett.")

    random.seed(42)
    for code in PARTY_ORDER:
        payload = build_submission(code)
        status, body = post(url, key, payload)
        top1 = payload["top3"][0]
        ok = "✓" if status in (200, 201, 204) else "✗"
        print(
            f"  {ok}  {code} ({PARTIES[code]['short_name']:<18})  "
            f"HTTP {status}  →  top1 {top1['code']} {top1['match_percent']:>5.1f}%"
        )


if __name__ == "__main__":
    main()
