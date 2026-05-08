from __future__ import annotations

"""
Spurningar fyrir borgarstjórnarkompásinn.

Þrjár tegundir spurninga:

  policy       Hefur áhrif á flokksamsvörun. Strangt orðalag.
  personality  Hefur AÐEINS áhrif á gamansama persónugerðar-lýsingu.
               Engin áhrif á pólitíska samsvörun.
  chaos        Hefur engin áhrif á neitt mikilvægt — bara til gamans.

Default tegund er "policy" ef ekki er annað sagt.

Hver policy spurning er á 5 punkta Likert-kvarða:
    -2  Mjög ósammála
    -1  Frekar ósammála
     0  Hlutlaus / veit ekki
    +1  Frekar sammála
    +2  Mjög sammála

`axes` listi inniheldur ása sem spurningin tengist, með þyngd og stefnu.
Þyngd er á bilinu 0..1 og táknar hve sterkt spurningin tengist ásnum.
Jákvæð þyngd: „sammála“ → svar fer í + átt á ásnum.
Neikvæð þyngd: „sammála“ → svar fer í − átt á ásnum.

Reglur sem þarf að virða:
- Engin policy-spurning má vera leiðandi eða hagsmunatengd.
- Orðalag á að vera hlutlaust.
- Ef spurning gæti talist tvíræð á að bæta við skýringu í `help`.
- Persónuleika- og glundroðaspurningar geta verið glettnar en mega ekki
  svívirða framboð, kjósendur eða einstaklinga.
"""

LIKERT_OPTIONS = [
    ("Mjög ósammála",          -2),
    ("Frekar ósammála",        -1),
    ("Hlutlaus / veit ekki",    0),
    ("Frekar sammála",          1),
    ("Mjög sammála",            2),
]

LIKERT_LABELS = [o for o, _ in LIKERT_OPTIONS]
LIKERT_VALUES = dict(LIKERT_OPTIONS)


QUESTIONS = [
    {
        "id": "q01_velferd",
        "text": "Borgin á að auka útgjöld til velferðarþjónustu, jafnvel þó það kosti meira.",
        "axes": [("velferd", 1.0), ("skattar", 0.4)],
    },
    {
        "id": "q02_skattar_laekka",
        "text": "Lækka ætti fasteignaskatta og borgargjöld þar sem hægt er.",
        "axes": [("skattar", -1.0)],
    },
    {
        "id": "q03_bilar",
        "text": "Bílaaðgengi og bílastæði eiga að hafa forgang umfram hjólastíga og göngugötur.",
        "axes": [("bilar", 1.0)],
    },
    {
        "id": "q04_borgarlina",
        "text": "Reykjavík á að fjárfesta kröftuglega í Borgarlínunni.",
        "axes": [("borgarlina", 1.0)],
    },
    {
        "id": "q05_thetting",
        "text": "Borgin á að byggja þéttar í stað þess að þenjast út.",
        "axes": [("husnaedi", 1.0)],
    },
    {
        "id": "q06_lagreist",
        "text": "Borgin á að leggja meiri áherslu á lágreist fjölskylduhúsnæði.",
        "axes": [("husnaedi", -0.7)],
        "help": "„Sammála“ er talin andstæða þéttingar í þessu tóli.",
    },
    {
        "id": "q07_loftslag_skipulag",
        "text": "Loftslagsmarkmið eiga að móta skipulags- og samgönguákvarðanir borgarinnar.",
        "axes": [("loftslag", 1.0)],
    },
    {
        "id": "q08_skolar",
        "text": "Leik- og grunnskólamál eiga að vera helsti forgangur borgarinnar.",
        "axes": [("skolar", 1.0)],
    },
    {
        "id": "q09_eldri",
        "text": "Þjónusta við eldri borgara þarf meiri fjármögnun og athygli.",
        "axes": [("eldri", 1.0)],
    },
    {
        "id": "q10_skrifraedi",
        "text": "Borgin á að draga úr skrifræði og einfalda leyfisveitingar.",
        "axes": [("atvinnu", 0.8)],
    },
    {
        "id": "q11_lydraedi",
        "text": "Íbúar eiga oftar að kjósa eða taka þátt í könnunum um stórar ákvarðanir borgarinnar.",
        "axes": [("lydraedi", 1.0)],
    },
    {
        "id": "q12_innflytjendur",
        "text": "Reykjavík á að taka betur á móti innflytjendum og styðja við inngildingu þeirra.",
        "axes": [("innflytjendur", 1.0)],
    },
    {
        "id": "q13_adhald",
        "text": "Aðhald í rekstri er mikilvægara en að setja af stað ný verkefni.",
        "axes": [("skattar", -0.7)],
    },
    {
        "id": "q14_menning",
        "text": "Auka á stuðning við menningu, íþróttir og félagsstarf ungmenna.",
        "axes": [("menning", 1.0)],
    },
    {
        "id": "q15_endurskoda_samgongur",
        "text": "Það á að endurskoða eða gera hlé á stórum samgönguverkefnum ef kostnaður hækkar verulega.",
        "axes": [("borgarlina", -0.7)],
        "help": "„Sammála“ er talin efahyggja gagnvart stórum samgönguverkefnum eins og Borgarlínu.",
    },
    {
        "id": "q16_hverfi",
        "text": "Þjónusta í hverfum á að vera nær fólki þar sem það býr.",
        "axes": [("velferd", 0.5), ("lydraedi", 0.4)],
    },
    {
        "id": "q17_stafraent",
        "text": "Bæta á stafræna þjónustu borgarinnar til að einfalda samskipti við íbúa.",
        "axes": [("atvinnu", 0.5), ("lydraedi", 0.3)],
    },
    {
        "id": "q18_oryggi_hreinleiki",
        "text": "Auka á áherslu á öryggi, hreinleika og viðhald borgarinnar.",
        "axes": [("atvinnu", 0.4)],
        "help": "Þessi spurning vegur lítið — flest framboð styðja viðhald að einhverju marki.",
    },
    {
        "id": "q19_atvinnuvoxtur",
        "text": "Leggja á meiri áherslu á atvinnuvöxt og störf í Reykjavík.",
        "axes": [("atvinnu", 1.0)],
    },
    {
        "id": "q20_almenningshusnaedi",
        "text": "Almenningshúsnæði og óhagnaðardrifin húsnæðisfélög eiga að gegna stærra hlutverki.",
        "axes": [("velferd", 0.6), ("atvinnu", -0.5)],
    },
    {
        "id": "q21_graen_svaedi",
        "text": "Stórar skipulagsákvarðanir eiga að vernda græn svæði og náttúru í borginni.",
        "axes": [("loftslag", 0.8), ("husnaedi", -0.4)],
    },
    {
        "id": "q22_hagnyt",
        "text": "Ég kýs hagnýtar staðbundnar úrbætur fram yfir hugmyndafræðilega pólitík.",
        "axes": [("lydraedi", 0.3)],
        "help": "Þessi spurning hefur litla þyngd og er aðallega til upplýsingar.",
    },
    {
        "id": "q23_einkareksturs",
        "text": "Einkafyrirtæki eiga að gegna stærra hlutverki í þjónustu borgarinnar.",
        "axes": [("atvinnu", 1.0)],
    },
    {
        "id": "q24_borg_rekur",
        "text": "Borgin á sjálf að reka fleiri þjónustustarfsemi í eigin nafni.",
        "axes": [("atvinnu", -1.0)],
    },
    {
        "id": "q25_vidradanlegt_husnaedi",
        "text": "Borgin á að taka virkari þátt í að tryggja viðráðanlegt húsnæði.",
        "axes": [("velferd", 0.7), ("husnaedi", 0.3)],
    },
]


# ---------------------------------------------------------------------------
# Persónuleikaspurningar — hafa AÐEINS áhrif á gamansama persónugerð.
# Hver tag-trigger samsvarar einkunn í chaos.ARCHETYPES.
# ---------------------------------------------------------------------------
PERSONALITY_QUESTIONS = [
    {
        "id": "p01_facebook",
        "type": "personality",
        "text": "Ég les athugasemdakerfi á íslenskum netmiðlum og kemst í tilfinningalegt uppnám.",
        "tags_on_agree": ["facebook"],
    },
    {
        "id": "p02_totes",
        "type": "personality",
        "text": "Ég á fleiri en þrjá fjölnota innkaupapoka.",
        "tags_on_agree": ["totes"],
    },
    {
        "id": "p03_parking_rage",
        "type": "personality",
        "text": "Ég hef hækkað röddina yfir bílastæði á síðastliðnu ári.",
        "tags_on_agree": ["parking"],
    },
    {
        "id": "p04_borgarlina_dinner",
        "type": "personality",
        "text": "Ég hef rætt Borgarlínuna í matarboði — ótilneyddur.",
        "tags_on_agree": ["borgarlina_dinner"],
    },
    {
        "id": "p05_meeting_endurance",
        "type": "personality",
        "text": "Ég gæti setið átta tíma fund í skipulagsnefnd ef það yrði kjötsúpa.",
        "tags_on_agree": ["meeting_endurance"],
    },
    {
        "id": "p06_civic_names",
        "type": "personality",
        "text": "Ég get nefnt þrjá borgarfulltrúa eftir minni — án þess að gúgla.",
        "tags_on_agree": ["civic_engagement"],
    },
    {
        "id": "p07_aðalskipulag",
        "type": "personality",
        "text": "Mér finnst aðalskipulag Reykjavíkur áhugavert lestrarefni.",
        "tags_on_agree": ["urbanism"],
    },
    {
        "id": "p08_laug",
        "type": "personality",
        "text": "Ég veit nákvæmlega hvenær er rólegast í minni uppáhalds sundlaug.",
        "tags_on_agree": ["laug"],
    },
]


# ---------------------------------------------------------------------------
# Glundroða-spurningar — hafa engin áhrif á neitt sem skiptir máli.
# ---------------------------------------------------------------------------
CHAOS_QUESTIONS = [
    {
        "id": "c01_skostaerd",
        "type": "chaos",
        "text": "Hver er skóstærðin þín?",
        "options": ["Undir 36", "36–39", "40–43", "44–46", "Yfir 46", "Vil ekki segja"],
    },
    {
        "id": "c02_uppahalds_laug",
        "type": "chaos",
        "text": "Hvaða Reykjavíkur sundlaug er best?",
        "options": [
            "Vesturbæjarlaug",
            "Laugardalslaug",
            "Sundhöllin",
            "Árbæjarlaug",
            "Breiðholtslaug",
            "Grafarvogslaug",
            "Engin þeirra — ég er meira fyrir Nauthólsvík",
        ],
    },
    {
        "id": "c03_kaffi",
        "type": "chaos",
        "text": "Hvað kostar lítill kaffibolli í 101 í dag (að þínum dómi)?",
        "options": [
            "Undir 600 kr.",
            "600–800 kr.",
            "800–1.000 kr.",
            "Yfir 1.000 kr.",
            "Ég brugga bara heima og er stoltur af því",
        ],
    },
    {
        "id": "c04_strunsa",
        "type": "chaos",
        "text": "Hvaða árstími lýsir innra ástandi þínu best í dag?",
        "options": [
            "Janúar á Hverfisgötu",
            "Mars með slabbi",
            "17. júní stutt fyrir hádegi",
            "Verslunarmannahelgi sem fór úr böndunum",
            "Október og fyrsti snjórinn",
            "Þorláksmessa kl. 22:30",
        ],
    },
    {
        "id": "c05_leiður_stadur",
        "type": "chaos",
        "text": "Hvar í Reykjavík líður þér mest eins og þú sért í tölvuleik?",
        "options": [
            "Hringtorgið við Hofsvallagötu",
            "Bílastæðahúsið Traðarkot kl. 17:30",
            "Hlemmur eftir miðnætti",
            "Sjálfsafgreiðslukassi í Bónus Skeifunni",
            "Smáralind á laugardegi",
            "IKEA á sunnudegi",
        ],
    },
]


# ---------------------------------------------------------------------------
# Sameinaður listi — interleavað þannig að persónuleika- og glundroðaspurningar
# birtast inn á milli stefnuspurninga til að halda flæðinu lifandi.
# Reglur: persónuleiki kemur reglulega (~á 4 spurninga fresti), glundroði sjaldnar.
# ---------------------------------------------------------------------------

def _interleave_questions():
    out = []
    pers_idx = 0
    chaos_idx = 0
    for i, q in enumerate(QUESTIONS):
        out.append(q)
        if (i + 1) % 4 == 0 and pers_idx < len(PERSONALITY_QUESTIONS):
            out.append(PERSONALITY_QUESTIONS[pers_idx])
            pers_idx += 1
        if (i + 1) % 7 == 0 and chaos_idx < len(CHAOS_QUESTIONS):
            out.append(CHAOS_QUESTIONS[chaos_idx])
            chaos_idx += 1
    # Restin í lokin — léttar spurningar fá eftirleik
    out.extend(PERSONALITY_QUESTIONS[pers_idx:])
    out.extend(CHAOS_QUESTIONS[chaos_idx:])
    return out


ALL_QUESTIONS = _interleave_questions()


def policy_questions():
    return [q for q in ALL_QUESTIONS if q.get("type", "policy") == "policy"]


def personality_questions():
    return [q for q in ALL_QUESTIONS if q.get("type") == "personality"]


def chaos_questions():
    return [q for q in ALL_QUESTIONS if q.get("type") == "chaos"]


def question_axis_summary():
    """Skilar yfirliti yfir hvaða ásar eru mældir og hversu margar spurningar tengjast þeim."""
    counts = {}
    for q in policy_questions():
        for axis, _ in q.get("axes", []):
            counts[axis] = counts.get(axis, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Per-session sampling — gefur hverjum notanda einstakan undirlist svo þeir
# fái EKKI sömu spurningar í hvert skipti sem þeir taka prófið.
#
# Reglur:
#   • Policy: ax-balanced — hver helsti ás (frumáás í q["axes"][0]) fær minnst
#     eina spurningu áður en seðlast til viðbótar.
#   • Personality + Chaos: einföld slembiröðun, taka N efstu.
#   • Allt seedað með stöðugum string (session_id), svo sami notandi fær sömu
#     spurningar ef þeir refresh-a — en nýr notandi (eða „Endurtaka prófið“)
#     fær nýjar spurningar.
# ---------------------------------------------------------------------------

import random as _random


def _axis_balanced_policy(rng: _random.Random, n: int) -> list[dict]:
    """Skilar `n` policy-spurningum, þar sem hver helsti ás er tryggður."""
    by_axis: dict[str, list[dict]] = {}
    for q in QUESTIONS:
        if not q.get("axes"):
            continue
        primary_axis = q["axes"][0][0]
        by_axis.setdefault(primary_axis, []).append(q)

    chosen_ids: set[str] = set()
    out: list[dict] = []

    # 1. Pick one from each primary-axis bucket (covers every axis at least once)
    axes_shuffled = list(by_axis.keys())
    rng.shuffle(axes_shuffled)
    for axis in axes_shuffled:
        bucket = [q for q in by_axis[axis] if q["id"] not in chosen_ids]
        if not bucket:
            continue
        pick = rng.choice(bucket)
        out.append(pick)
        chosen_ids.add(pick["id"])
        if len(out) >= n:
            return out

    # 2. Fill remaining slots from the rest, in random order
    remaining = [q for q in QUESTIONS if q["id"] not in chosen_ids]
    rng.shuffle(remaining)
    while len(out) < n and remaining:
        out.append(remaining.pop(0))
    return out


def sample_questions(seed: str | int,
                     policy_count: int = 22,
                     personality_count: int = 6,
                     chaos_count: int = 3) -> list[dict]:
    """Skilar interleaved spurningalista, deterministically seeded.

    Sami `seed` → sömu spurningar (góð UX við refresh).
    Nýr `seed` → nýjar spurningar (góð UX við „Endurtaka prófið“).
    """
    rng = _random.Random(seed)

    sampled_policy = _axis_balanced_policy(rng, min(policy_count, len(QUESTIONS)))

    pers_pool = list(PERSONALITY_QUESTIONS)
    rng.shuffle(pers_pool)
    sampled_personality = pers_pool[:personality_count]

    chaos_pool = list(CHAOS_QUESTIONS)
    rng.shuffle(chaos_pool)
    sampled_chaos = chaos_pool[:chaos_count]

    # Interleave eins og _interleave_questions gerir
    out: list[dict] = []
    pers_idx = 0
    chaos_idx = 0
    for i, q in enumerate(sampled_policy):
        out.append(q)
        if (i + 1) % 4 == 0 and pers_idx < len(sampled_personality):
            out.append(sampled_personality[pers_idx])
            pers_idx += 1
        if (i + 1) % 7 == 0 and chaos_idx < len(sampled_chaos):
            out.append(sampled_chaos[chaos_idx])
            chaos_idx += 1
    out.extend(sampled_personality[pers_idx:])
    out.extend(sampled_chaos[chaos_idx:])
    return out
