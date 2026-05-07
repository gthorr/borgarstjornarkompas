"""
Glundroðakerfi — gamansamir persónugerðar-titlar og ekkert annað.

Þetta kerfi:
  • Hefur ENGIN áhrif á samsvörun framboða.
  • Notar aðeins persónuleika- og glundroða-svör.
  • Birtir titla á borð við „Borgarlínu-öfgamaður“ í einum kassa á
    niðurstöðusíðu, með skýrri „bara til gamans“ merkingu.

Hér er bæði íslensk útgáfa titla og ensk hliðstæða (sem notandinn
óskaði sérstaklega eftir). Báðar útgáfur birtast saman, ensk útgáfa
er smærri og skáletruð.
"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Persónugerðir
# ---------------------------------------------------------------------------
ARCHETYPES = [
    {
        "id": "facebook_commenter",
        "label_is": "Vottaður Facebook-athugasemdaritari Reykjavíkur",
        "label_en": "Certified Reykjavík Facebook commenter",
        "description": "Þú lest, þú bregst við, þú sefur ekki vel. Reykjavík þakkar þér.",
        "required": ["facebook"],
    },
    {
        "id": "parking_discourse",
        "label_is": "Hættulega niðursokkin/n í bílastæðaumræðu",
        "label_en": "Dangerously invested in parking discourse",
        "description": "Þú heyrir orðið „bílastæði“ og hjartað slær örar — í báðar áttir.",
        "required": ["parking"],
    },
    {
        "id": "tote_bags",
        "label_is": "Á næstum örugglega fjóra fjölnota innkaupapoka",
        "label_en": "Likely to own 4 reusable tote bags",
        "description": "Þú átt fleiri poka en þú þarft og veist nákvæmlega hvar þeir liggja.",
        "required": ["totes"],
    },
    {
        "id": "council_material",
        "label_is": "Gæti óvart endað í borgarstjórn",
        "label_en": "Could accidentally become a city council member",
        "description": "Bara eitt símtal og þú segir „já, ég get tekið þetta að mér í eitt kjörtímabil“.",
        "required_any_of": [["meeting_endurance", "civic_engagement"]],
        "required": ["meeting_endurance", "civic_engagement"],  # bæði þurfa að vera virk
    },
    {
        "id": "borgarlina_extremist",
        "label_is": "Borgarlínu-öfgamaður (í góðu)",
        "label_en": "Borgarlína extremist",
        "description": "Þú átt minnst þrjár skoðanir á tíðnitöflu og einn vinur er hættur að bjóða þér í kvöldmat.",
        "required": ["borgarlina_dinner"],
    },
    {
        "id": "urbanist",
        "label_is": "Lítillega úr böndum sloppinn borgarsinni",
        "label_en": "Mildly unhinged urbanist",
        "description": "Þú hefur ákveðnar skoðanir á þéttleika hverfa og myndir gjarnan deila þeim.",
        "required": ["urbanism"],
    },
    {
        "id": "zoning_marathoner",
        "label_is": "Myndi lifa af átta tíma fund í skipulagsnefnd",
        "label_en": "Would survive 8 hours in a zoning committee meeting",
        "description": "Þú sækir í gæði, ekki hraða. Og kjötsúpu.",
        "required": ["meeting_endurance"],
    },
    {
        "id": "laugar_local",
        "label_is": "Á sinn eigin morgunstól í pottinum",
        "label_en": "Has a regular pot seat",
        "description": "Þú þekkir starfsfólkið, þú þekkir veðrið, þú þekkir skoðanir nágranna í 9. potti.",
        "required": ["laug"],
    },
    {
        "id": "civic_nerd",
        "label_is": "Borgarmálanörd með hæfilega heilbrigt jafnvægi",
        "label_en": "Healthily nerdy civic mind",
        "description": "Þú getur nefnt borgarfulltrúa á annarri tilraun og það er alveg nógu gott.",
        "required": ["civic_engagement"],
    },
]


# Sjálfgefnir titlar þegar enginn smellur fellur (eða notandi sleppti vibe-prófinu).
FALLBACK_ARCHETYPES = [
    {
        "id": "fallback_calm",
        "label_is": "Hófstillt/ur kosningabær/-bæja",
        "label_en": "Reasonable Reykjavík voter",
        "description": "Þú notaðir tólið og fórst aftur að lifa lífinu. Það er fínn vibe.",
    },
    {
        "id": "fallback_mystery",
        "label_is": "Pólitísk ráðgáta í vetrarjakka",
        "label_en": "Political mystery in a winter coat",
        "description": "Erfitt að lesa þig — það er stundum styrkur.",
    },
    {
        "id": "fallback_weather",
        "label_is": "Veðráttuháð skoðanafólk",
        "label_en": "Weather-dependent opinion-haver",
        "description": "Þú hefur sterkari skoðanir í björtu veðri. Það á við um okkur öll.",
    },
]


# ---------------------------------------------------------------------------
# Útreikningar
# ---------------------------------------------------------------------------

def collect_personality_tags(answers: Dict[str, int], personality_qs: List[dict]) -> Dict[str, int]:
    """Telur saman tag-merki út frá persónuleikasvörum.

    Aðeins svör >= +1 (frekar/mjög sammála) virkja tag.
    Mjög sammála (+2) gefur 2 stig, frekar sammála (+1) gefur 1 stig.
    """
    tags: Dict[str, int] = {}
    for q in personality_qs:
        v = answers.get(q["id"], 0)
        if v >= 1:
            for tag in q.get("tags_on_agree", []):
                tags[tag] = tags.get(tag, 0) + (2 if v >= 2 else 1)
    return tags


def select_archetypes(tags: Dict[str, int], max_n: int = 3, seed: int | None = None) -> List[dict]:
    """Velur 1–`max_n` persónugerðir út frá tag-merkjum.

    Hver persónugerð krefst þess að ÖLL `required` tag-merki séu til staðar
    (gildi > 0). Persónugerðir sem uppfylla skilyrði eru raðaðar eftir
    samanlagðri þyngd merkja, með smá slembivali til að birting breytist
    milli keyrslna.
    """
    rng = random.Random(seed)

    eligible: List[Tuple[int, dict]] = []
    for arc in ARCHETYPES:
        required = arc.get("required", [])
        if not all(tags.get(t, 0) > 0 for t in required):
            continue
        weight = sum(tags.get(t, 0) for t in required)
        # Smá slembi-bólga svo röð breytist milli keyrslna
        weight_jitter = weight + rng.uniform(0, 0.5)
        eligible.append((weight_jitter, arc))

    if not eligible:
        # Pikk slembna fallback
        return [rng.choice(FALLBACK_ARCHETYPES)]

    eligible.sort(key=lambda x: x[0], reverse=True)
    chosen = [arc for _, arc in eligible[:max_n]]
    return chosen


def chaos_score(answers: Dict[str, int | str], chaos_qs: List[dict]) -> Tuple[int, str]:
    """Reiknar gjörsamlega merkingarlausa „glundroðatölu“ og lýsingu á henni.

    Talan er á bilinu 0–100 og táknar EKKERT.
    """
    rng = random.Random()
    answered = 0
    aggregate = 0
    for q in chaos_qs:
        ans = answers.get(q["id"])
        if ans is None or ans == "":
            continue
        answered += 1
        # Notum stafrófs-vísi val ef strengur, annars hreina tölu
        if isinstance(ans, str):
            options = q.get("options", [])
            try:
                idx = options.index(ans)
            except ValueError:
                idx = 0
            aggregate += (idx + 1) * 13
        else:
            aggregate += int(ans) * 7
    if answered == 0:
        return 0, "Engin glundroðagildi tiltæk."

    score = (aggregate + rng.randint(0, 11)) % 101

    if score < 20:
        label = "Furðanlega rólegt yfirborð. Eitthvað er kraumar þó undir."
    elif score < 40:
        label = "Hófleg ringulreið. Innan venjulegra reykvískra marka."
    elif score < 60:
        label = "Klassísk höfuðborgarbúa-úlfúð. Heilbrigð að mestu."
    elif score < 80:
        label = "Hressilega úr böndunum sloppinn vibe."
    else:
        label = "Stjórnlaus borgarstjórnar-orka. Þú þarft sennilega vatnsglas."
    return score, label


def render_archetype_blurb(archetypes: List[dict]) -> str:
    """Skilar samanteknum lýsingartexta fyrir niðurstöðusíðu."""
    if not archetypes:
        return ""
    out_lines = []
    for arc in archetypes:
        out_lines.append(f"**{arc['label_is']}**  \n*{arc['label_en']}* — {arc['description']}")
    return "\n\n".join(out_lines)


# ---------------------------------------------------------------------------
# Sjálfprófun
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from questions import personality_questions, chaos_questions

    sample_answers = {
        "p01_facebook": 2,
        "p03_parking_rage": 1,
        "p05_meeting_endurance": 2,
        "p06_civic_names": 2,
        "c01_skostaerd": "40–43",
        "c02_uppahalds_laug": "Vesturbæjarlaug",
        "c03_kaffi": "Yfir 1.000 kr.",
    }
    tags = collect_personality_tags(sample_answers, personality_questions())
    print("Tags:", tags)
    arcs = select_archetypes(tags, seed=42)
    print("Archetypes:", [a["label_is"] for a in arcs])
    score, label = chaos_score(sample_answers, chaos_questions())
    print(f"Chaos: {score} — {label}")
