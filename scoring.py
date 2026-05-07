"""
Útreikningur á samsvörun milli notandasvara og stefnu framboðs.

Aðferðin er viljandi einföld og gegnsæ:

1. Fyrir hverja spurningu reiknum við „afstöðu framboðs“ á þeirri spurningu
   út frá stigum þess á tengdum ásum (vegið meðaltal, klippt í [-2, +2]).
2. Vegalengdin milli notandasvars og afstöðu framboðs er |svar − afstaða|.
3. Hámarksvegalengd er 4 (frá -2 til +2). Samsvörun á spurningu er
       1 − (vegalengd / 4)
   sem gefur tölu á bilinu 0..1.
4. Heildarsamsvörun framboðs er einfalt meðaltal samsvörunar yfir allar spurningar.

Þetta þýðir að jafnvel þó tólið virðist „flókið“ er hægt að rekja hverja
prósentu beint til svara notanda og opinberlega skráðra stiga framboðs.
Ekkert er falið og ekkert framboð fær falinn forgang.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from parties import AXIS_IDS


# ---------------------------------------------------------------------------
# Kjarna útreikningar
# ---------------------------------------------------------------------------

def implied_party_position(party: dict, question: dict) -> float:
    """Reikna afstöðu framboðs á einni spurningu (gildi á bilinu -2..+2).

    Þyngdir geta verið neikvæðar (þá snýst stefnan við), svo við notum
    hreina þyngd til að leggja saman vog en upprunalegan formerki til að
    margfalda við stigið.
    """
    total_weighted = 0.0
    total_abs_weight = 0.0
    for axis, weight in question["axes"]:
        score = party["scores"].get(axis, 0)
        total_weighted += score * weight
        total_abs_weight += abs(weight)
    if total_abs_weight == 0:
        return 0.0
    pos = total_weighted / total_abs_weight
    # Klippa í gilt bil
    return max(-2.0, min(2.0, pos))


def party_match(answers: Dict[str, int], questions: List[dict], party: dict) -> Tuple[float, List[dict]]:
    """Reikna samsvörun framboðs við svör notanda.

    Aðeins spurningar af type == "policy" eru notaðar í útreikningi á
    pólitískri samsvörun. Persónuleika- og glundroðaspurningar (chaos)
    hafa ENGIN áhrif á niðurstöðu pólitísks mats.

    Skilar (heildarsamsvörun 0..1, listi með nákvæmum upplýsingum á hverja spurningu).
    """
    per_question = []
    total = 0.0
    counted = 0
    for q in questions:
        # Eingöngu stefnu-spurningar (policy) hafa áhrif á samsvörun.
        if q.get("type", "policy") != "policy":
            continue
        if q["id"] not in answers:
            # Spurning ekki svarað enn — sleppum henni alveg
            continue
        user = float(answers[q["id"]])
        pos = implied_party_position(party, q)
        distance = abs(user - pos)
        match = 1.0 - (distance / 4.0)
        per_question.append({
            "question": q,
            "user_answer": user,
            "party_position": pos,
            "match": match,
        })
        total += match
        counted += 1
    overall = (total / counted) if counted else 0.0
    return overall, per_question


def rank_parties(answers: Dict[str, int], questions: List[dict], parties: Dict[str, dict]) -> List[dict]:
    """Skila lista yfir framboð, raðað eftir samsvörun (mest fyrst)."""
    results = []
    for code, party in parties.items():
        overall, per_q = party_match(answers, questions, party)
        results.append({
            "code": code,
            "party": party,
            "match": overall,
            "per_question": per_q,
        })
    results.sort(key=lambda r: r["match"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Hjálparfall fyrir niðurstöðusíðu
# ---------------------------------------------------------------------------

def compute_user_axis_vector(answers: Dict[str, int], questions: List[dict]) -> Dict[str, float]:
    """Aggrega svör notanda á ása.

    Skilar dict (axis_id -> meðalstigatala á bilinu -2..+2).
    Notar vegið meðaltal yfir spurningar sem snerta hvern ás.
    """
    weighted_sum = {a: 0.0 for a in AXIS_IDS}
    total_weight = {a: 0.0 for a in AXIS_IDS}
    for q in questions:
        if q.get("type", "policy") != "policy":
            continue
        if q["id"] not in answers:
            continue
        user = float(answers[q["id"]])
        for axis, weight in q["axes"]:
            # Þyngdarmerki segir til um hvort sammála sé í + eða − átt á ásnum
            weighted_sum[axis] += user * weight
            total_weight[axis] += abs(weight)
    out = {}
    for a in AXIS_IDS:
        if total_weight[a] > 0:
            out[a] = max(-2.0, min(2.0, weighted_sum[a] / total_weight[a]))
        else:
            out[a] = 0.0
    return out


def axis_agreement(user_axis: Dict[str, float], party_scores: Dict[str, float]) -> List[Tuple[str, float]]:
    """Skila lista yfir (axis_id, samsvörun 0..1) raðaðan eftir samsvörun (mest fyrst)."""
    out = []
    for axis in AXIS_IDS:
        u = user_axis.get(axis, 0.0)
        p = float(party_scores.get(axis, 0))
        d = abs(u - p) / 4.0
        out.append((axis, max(0.0, 1.0 - d)))
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def biggest_agreements_and_disagreements(
    user_axis: Dict[str, float],
    party_scores: Dict[str, float],
    n: int = 3,
) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
    """Skila (mestu samsvarandi ásar, mestu ósamsvarandi ásar)."""
    sorted_pairs = axis_agreement(user_axis, party_scores)
    return sorted_pairs[:n], list(reversed(sorted_pairs))[:n]


# ---------------------------------------------------------------------------
# Sjálfprófun
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Einföld sjálfprófun til að sannreyna að útreikningurinn sé samkvæmur sjálfum sér.
    from parties import PARTIES
    from questions import QUESTIONS

    # 1) Allir með 0: allir eiga að vera með 100% samsvörun gagnvart hlutlausum ásum
    #    (vegna þess að hver svör vs hlutlaus afstaða gefur fjarlægð 0 á þeim spurningum).
    neutral = {q["id"]: 0 for q in QUESTIONS}
    ranked_neutral = rank_parties(neutral, QUESTIONS, PARTIES)
    print("\n[Hlutlaus svör]")
    for r in ranked_neutral[:5]:
        print(f"  {r['code']} {r['party']['short_name']:<22}  {r['match']*100:5.1f}%")

    # 2) Spegla svör á tilteknu framboði — það á að enda efst.
    target = "S"
    target_party = PARTIES[target]
    answers = {}
    for q in QUESTIONS:
        # Reikna afstöðu framboðs á spurningunni og nota það sem svar (rúnnað).
        pos = implied_party_position(target_party, q)
        answers[q["id"]] = max(-2, min(2, round(pos)))
    ranked = rank_parties(answers, QUESTIONS, PARTIES)
    print(f"\n[Svör spegluð á {target}]")
    for r in ranked[:5]:
        print(f"  {r['code']} {r['party']['short_name']:<22}  {r['match']*100:5.1f}%")
    assert ranked[0]["code"] == target, f"Vænt: {target}, fékk: {ranked[0]['code']}"
    print("OK")
