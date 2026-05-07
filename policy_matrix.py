"""
Stefnu-fylki — normalisering á áherslum framboða.

Þetta er DEEP-DIVE samanburðargagnastöð sem stendur SAMHLIÐA stefnuásunum 12
sem stigagjöfin í parties.py byggir á.

Hér er hver röð **rekstrarleg afstaða** (ekki orðrænn frasi) sem hægt er að
mæla á þessum kvarða:

    -2  Sterk andstaða / virkur viðnámsaðili
    -1  Frekar andstæð / efahyggja
     0  Óljóst / blandað / ekki nægar heimildir
    +1  Frekar styður
    +2  Sterkur stuðningur / lykiláhersla

Markmið:
  • Strippa burt ræðu-frasa og bera saman hvað framboðin gera FAKTÍSKT öðruvísi.
  • Sýna óvissu hreinskilnislega.
  • Auðvelda þér að breyta stigum og heimildum handvirkt.

ATHUGIÐ: Allar tölur og certainty-merki eru BRÁÐABIRGÐA byggð á upphafsmati
sem notandi tólsins gaf. Þú verður að staðfesta þetta á opinberum
stefnuskrám framboða áður en tólið er birt opinberlega. Sjá DATA_REVIEW.md.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Skilgreining á 20 rekstrarásum
# ---------------------------------------------------------------------------
# Hver ás hefur:
#   id            stafrænn lykill
#   label         íslensk merking sem birtist í UI
#   description   stutt útskýring á því HVAÐ er verið að mæla
#   group         flokkun fyrir skipulag á niðurstöðu (transport, housing, ...)
# ---------------------------------------------------------------------------

POLICY_AXES = [
    # Samgöngur
    {"id": "borgarlina_support",   "label": "Stuðningur við Borgarlínu",          "group": "Samgöngur",
     "description": "Vilji til að fjárfesta í og halda áfram með Borgarlínuverkefnið."},
    {"id": "more_bike_lanes",      "label": "Fleiri hjólastígar",                  "group": "Samgöngur",
     "description": "Forgangur að uppbyggingu hjólastíga og hjólatengdrar þjónustu."},
    {"id": "parking_priority",     "label": "Forgangur einkabíls / bílastæða",     "group": "Samgöngur",
     "description": "Áhersla á aðgengi einkabíla, bílastæðafjölda og umferðarrýmd."},

    # Húsnæði
    {"id": "dense_housing",        "label": "Þétt byggð / innfylling",             "group": "Húsnæði",
     "description": "Vilji til að byggja þétt og fylla inn í núverandi hverfi."},
    {"id": "expand_outward",       "label": "Útþensla borgarinnar",                "group": "Húsnæði",
     "description": "Vilji til að taka ný svæði í notkun fyrir byggð (t.d. lágreist hverfi)."},
    {"id": "public_housing",       "label": "Opinber/óhagnaðardrifin húsnæði",     "group": "Húsnæði",
     "description": "Stuðningur við almennt íbúðakerfi og óhagnaðardrifin húsnæðisfélög."},

    # Fjármál
    {"id": "lower_taxes",          "label": "Lækkun skatta og gjalda",             "group": "Fjármál",
     "description": "Vilji til að lækka fasteignaskatta og borgargjöld."},
    {"id": "expand_welfare",       "label": "Aukin velferðarútgjöld",              "group": "Fjármál",
     "description": "Vilji til að auka útgjöld til velferðarþjónustu."},
    {"id": "private_sector",       "label": "Aðkoma einkageirans",                 "group": "Fjármál",
     "description": "Stuðningur við útvistun og einkarekstur í þjónustu borgarinnar."},

    # Umhverfi
    {"id": "climate_planning",     "label": "Loftslagsmiðað skipulag",             "group": "Umhverfi",
     "description": "Að loftslagsmarkmið móti skipulags- og samgönguákvarðanir."},
    {"id": "green_protection",     "label": "Vernd grænna svæða",                  "group": "Umhverfi",
     "description": "Vilji til að vernda græn svæði í skipulagsákvörðunum."},

    # Samfélag
    {"id": "immigration_inclusion","label": "Inngilding innflytjenda",             "group": "Samfélag",
     "description": "Áhersla á þjónustu, mannréttindi og inngildingu innflytjenda."},
    {"id": "direct_democracy",     "label": "Beint lýðræði / íbúakosningar",       "group": "Samfélag",
     "description": "Vilji til að bera stórar ákvarðanir undir íbúa með kosningum eða könnunum."},
    {"id": "family_children",      "label": "Fjölskyldur og börn",                 "group": "Samfélag",
     "description": "Forgangur leik- og grunnskóla og þjónustu við barnafjölskyldur."},
    {"id": "elderly_services",     "label": "Þjónusta við eldri borgara",          "group": "Samfélag",
     "description": "Forgangur eldri borgara og þjónustu við þá."},
    {"id": "culture_investment",   "label": "Menning og listir",                   "group": "Samfélag",
     "description": "Stuðningur við menningu, listir og frístundir."},

    # Stjórnsýsla og rekstur
    {"id": "reduce_bureaucracy",   "label": "Minnka skrifræði",                    "group": "Stjórnsýsla",
     "description": "Áhersla á einfaldari leyfisveitingar og skilvirkari stjórnsýslu."},
    {"id": "municipal_operations", "label": "Sterkur opinber rekstur",             "group": "Stjórnsýsla",
     "description": "Vilji til að borgin reki sjálf sem mest af þjónustu."},
    {"id": "market_business",      "label": "Markaður og atvinnulíf",              "group": "Stjórnsýsla",
     "description": "Áhersla á atvinnulíf, vöxt og samkeppnishæfni."},
    {"id": "practical_maintenance","label": "Hagnýtt viðhald og þjónusta",         "group": "Stjórnsýsla",
     "description": "Forgangur á öryggi, hreinleika, viðhald og daglega þjónustu í hverfum."},
]

POLICY_AXIS_LOOKUP = {a["id"]: a for a in POLICY_AXES}
POLICY_AXIS_IDS = [a["id"] for a in POLICY_AXES]
POLICY_AXIS_GROUPS = []
_seen = set()
for a in POLICY_AXES:
    if a["group"] not in _seen:
        POLICY_AXIS_GROUPS.append(a["group"])
        _seen.add(a["group"])


# ---------------------------------------------------------------------------
# Stefnu-fylkið — upphafsmat sem þarf að staðfesta handvirkt.
# Lyklar eru listabókstafir (A, B, C, D, F, G, J, M, P, R, S).
# ---------------------------------------------------------------------------
#
# UPPHAFSMAT — frá notanda tólsins (sjá kröfur 17). Þetta er EKKI sannleikurinn,
# heldur útgangspunktur sem þú þarft að bera saman við opinberar stefnuskrár.
# Sjá `verify_status` fyrir hvar staðfestingu er enn ábótavant.
# ---------------------------------------------------------------------------

POLICY_MATRIX: Dict[str, Dict[str, int]] = {
    # G og R: uppfært 2026-05-07 með heimildum frá gdf.is og okkarborg.is.
    # Sjá DETAIL_OVERRIDES neðar fyrir röksemd og heimildaslóð á hvert stig.
    "borgarlina_support":   {"A":  2, "B":  1, "C":  2, "D": -1, "F": -1, "G": -1, "J":  2, "M": -2, "P":  2, "R": -2, "S":  2},
    "more_bike_lanes":      {"A":  2, "B":  1, "C":  2, "D":  0, "F": -1, "G":  0, "J":  2, "M": -1, "P":  2, "R": -2, "S":  2},
    "parking_priority":     {"A": -2, "B":  0, "C": -1, "D":  2, "F":  2, "G":  1, "J": -2, "M":  2, "P": -2, "R":  2, "S":  0},
    # F uppfært — dense_housing -1 → 0: gagnrýnir „ofurþéttingu“ en styður „mannlegri“ skipulag.
    # D uppfært — dense_housing 0 → 1: stuðningur við hraða uppbyggingu með markaðs-driven framework.
    # M uppfært — dense_housing -2 → -1: pro-supply en anti-density (úthverfa-stækkunar logík).
    "dense_housing":        {"A":  2, "B":  1, "C":  2, "D":  1, "F":  0, "G": -1, "J":  2, "M": -1, "P":   1, "R": -2, "S":  2},
    # F uppfært — expand_outward 1 → 0: blönduð afstaða, hvorki útþenslu- né þéttingar-flokkur.
    "expand_outward":       {"A": -2, "B":  0, "C": -1, "D":  1, "F":  0, "G":  1, "J": -2, "M":  2, "P": -1, "R":  2, "S": -1},
    "public_housing":       {"A":  2, "B":  1, "C":  1, "D": -1, "F":  1, "G":  0, "J":  2, "M": -1, "P":   1, "R": -1, "S":  2},
    # F uppfært — lower_taxes 2 → 0: ekki niðurskurðar-flokkur, áhersla á ráðdeild en ekki austerity.
    "lower_taxes":          {"A": -1, "B":  0, "C":  1, "D":  2, "F":  0, "G":  2, "J": -2, "M":  2, "P":  0, "R":  2, "S": -1},
    # D uppfært — expand_welfare -1 → 0: ekki andstæð velferð, en efficiency-first.
    "expand_welfare":       {"A":  2, "B":  1, "C":  1, "D":  0, "F":  2, "G":  1, "J":  2, "M":  0, "P":   1, "R":  0, "S":  2},
    "private_sector":       {"A": -1, "B":  0, "C":  2, "D":  2, "F":  0, "G":  1, "J": -2, "M":   1, "P":  0, "R":  2, "S":  0},
    # F uppfært — climate_planning -1 → 0: ekki andstæð, en ekki drifkraftur ákvarðana heldur.
    "climate_planning":     {"A":  2, "B":  1, "C":  2, "D":  0, "F":  0, "G":  0, "J":  2, "M": -1, "P":  2, "R": -1, "S":  2},
    # F uppfært — immigration_inclusion -1 → 0: takmörkuð gögn, hlutlaus á þessum tímapunkti.
    "immigration_inclusion":{"A":  2, "B":  1, "C":  2, "D":  0, "F":  0, "G":  0, "J":  2, "M": -1, "P":  2, "R": -2, "S":  2},
    # F/C/B uppfært — direct_democracy fær +1 fyrir miðju-praktíska íbúasamráðsáherslu.
    # J uppfært 2026-05-07 — direct_democracy 0 → 2: skýr þátttöku-lýðræði og íbúa-empowerment.
    "direct_democracy":     {"A":  1, "B":  1, "C":  1, "D":  0, "F":  1, "G":  2, "J":  2, "M":   0, "P":  2, "R":  1, "S":   1},
    "reduce_bureaucracy":   {"A":  0, "B":  1, "C":  2, "D":  2, "F":  1, "G":  2, "J": -1, "M":  2, "P":  1, "R":  2, "S":  0},
    # F uppfært — family_children 2 → 1: hófleg áhersla; eldri borgarar eru sterkari.
    "family_children":      {"A":  1, "B":  2, "C":  1, "D":  1, "F":  1, "G":  2, "J":   2, "M":   0, "P":  1, "R":  1, "S":  2},
    "elderly_services":     {"A":  1, "B":  2, "C":  0, "D":   1, "F":  2, "G":  2, "J":   2, "M":  0, "P":  0, "R":  1, "S":  1},
    "culture_investment":   {"A":  2, "B":  1, "C":  1, "D": -1, "F": -1, "G":  0, "J":  2, "M": -1, "P":  2, "R": -1, "S":  2},
    "municipal_operations": {"A":  2, "B":  0, "C": -1, "D": -2, "F":  0, "G": -1, "J":  2, "M": -2, "P":  1, "R": -2, "S":  1},
    "market_business":      {"A": -1, "B":  1, "C":  2, "D":  2, "F":  0, "G":  2, "J": -2, "M":   1, "P":   1, "R":  1, "S":  0},
    "green_protection":     {"A":  2, "B":  1, "C":  2, "D":  0, "F":  0, "G":  1, "J":  2, "M": -1, "P":  2, "R":  0, "S":  2},
    "practical_maintenance":{"A":  0, "B":  2, "C":  1, "D":  1, "F":  2, "G":  2, "J":   1, "M":  1, "P":   1, "R":  2, "S":  1},
}


# ---------------------------------------------------------------------------
# Vissustig á hverju framboði (high / medium / low)
# ---------------------------------------------------------------------------
#
# `overall`        heildarvissa um pólitíska prófíl framboðsins
# `per_axis`       valkvætt: ef ákveðinn ás er sérstaklega óviss má skrá það hér
# Allar tölur eru BRÁÐABIRGÐA og þurfa staðfestingu.
# ---------------------------------------------------------------------------

PARTY_CERTAINTY: Dict[str, Dict] = {
    "A": {"overall": "high",   "per_axis": {}},
    "B": {"overall": "medium", "per_axis": {"borgarlina_support": "low", "climate_planning": "low"}},
    "C": {"overall": "high",   "per_axis": {"parking_priority": "medium"}},
    "D": {"overall": "high",   "per_axis": {"climate_planning": "medium"}},
    "F": {"overall": "medium", "per_axis": {"dense_housing": "low", "immigration_inclusion": "low"}},
    # G uppfært 2026-05-07 með heimildum frá gdf.is.
    "G": {
        "overall": "medium",
        "per_axis": {
            "lower_taxes": "high", "family_children": "high", "direct_democracy": "high",
            "reduce_bureaucracy": "high", "practical_maintenance": "high", "market_business": "high",
            "elderly_services": "medium", "private_sector": "medium", "borgarlina_support": "medium",
            "more_bike_lanes": "low", "parking_priority": "medium", "dense_housing": "medium",
            "expand_outward": "medium", "public_housing": "low", "expand_welfare": "medium",
            "climate_planning": "medium", "immigration_inclusion": "low", "culture_investment": "low",
            "municipal_operations": "medium", "green_protection": "medium",
        },
    },
    "J": {"overall": "high",   "per_axis": {}},
    "M": {"overall": "high",   "per_axis": {"immigration_inclusion": "medium"}},
    "P": {"overall": "high",   "per_axis": {}},
    # R uppfært 2026-05-07 með heimildum frá okkarborg.is.
    "R": {
        "overall": "medium",
        "per_axis": {
            "borgarlina_support": "high", "parking_priority": "high", "dense_housing": "high",
            "expand_outward": "high", "lower_taxes": "high", "private_sector": "high",
            "immigration_inclusion": "high", "municipal_operations": "high", "reduce_bureaucracy": "high",
            "practical_maintenance": "high",
            "more_bike_lanes": "medium", "public_housing": "medium", "expand_welfare": "medium",
            "climate_planning": "medium", "family_children": "medium", "elderly_services": "medium",
            "culture_investment": "medium", "direct_democracy": "medium", "market_business": "medium",
            "green_protection": "medium",
        },
    },
    "S": {"overall": "high",   "per_axis": {}},
}


# ---------------------------------------------------------------------------
# Heimildir á einstaka stigatölu
# ---------------------------------------------------------------------------
#
# Lykill er (party_letter, axis_id). Gildi er listi af URL-um. Tómur listi
# þýðir „þarf staðfestingu — engin opinber heimild skráð enn“.
# ---------------------------------------------------------------------------

POLICY_SOURCES: Dict[Tuple[str, str], List[str]] = {
    # Bakaleg gögn fyrir bakvisanir áður en DETAIL_OVERRIDES kerfið kom inn.
    # Ný þróun á að nota DETAIL_OVERRIDES (sjá neðar) því þar fylgir röksemd með.
    ("S", "borgarlina_support"):    ["https://samfylkingin.is/"],
    ("S", "dense_housing"):         ["https://samfylkingin.is/"],
    ("D", "lower_taxes"):           ["https://xd.is/"],
    ("D", "parking_priority"):      ["https://xd.is/"],
    ("M", "borgarlina_support"):    ["https://midflokkurinn.is/"],
    ("J", "public_housing"):        ["https://sosialistar.is/"],
    ("P", "direct_democracy"):      ["https://piratar.is/"],
    ("C", "private_sector"):        ["https://vidreisn.is/"],
}


# ---------------------------------------------------------------------------
# DETAIL_OVERRIDES — rík upplýsingar um einstaka stigafærslu
# ---------------------------------------------------------------------------
# Lykill: (party_letter, axis_id).
# Gildi: dict með reitum:
#   certainty   "high" | "medium" | "low"
#   reason      Stutt íslensk röksemd byggð á heimildum.
#   sources     Listi af URL-um.
#
# Mikilvæg aðgreining sem þetta kerfi gerir:
#
#   {"score": 0, "certainty": "low",  "reason": "Engin afstaða finnanleg."}
#   ↑ óljóst — ekki vitað hvar framboðið stendur
#
#   {"score": 0, "certainty": "high", "reason": "Skýr hófsöm/málamiðlunar-afstaða."}
#   ↑ skýr en hófsöm afstaða
#
# Hvort tveggja skorast sem 0 í POLICY_MATRIX en birtist mismunandi í UI.
# ---------------------------------------------------------------------------

VINSTRID_SOURCE = "https://vinstrid.is/"
GODAN_DAGINN_SOURCE = "https://gdf.is/stefnumalin/"
OKKAR_BORG_SOURCE = "https://www.okkarborg.is/"

DETAIL_OVERRIDES: Dict[Tuple[str, str], Dict] = {
    # ---------------------- A — Vinstrið ----------------------
    ("A", "borgarlina_support"):    {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Sterkur stuðningur við Borgarlínu — almenningssamgöngur kjarnaverkefni."},
    ("A", "more_bike_lanes"):       {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Áhersla á virkar samgöngur, hjólastíga og göngugötur."},
    ("A", "parking_priority"):      {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Andstaða við forgang einkabíla á kostnað virkra og almenningssamgangna."},
    ("A", "dense_housing"):         {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Þétting byggðar tengd loftslags-, samgöngu- og inngildingar-markmiðum."},
    ("A", "expand_outward"):        {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Andstaða við útþenslu sem skapar bíla-háða úthverfa-byggð."},
    ("A", "public_housing"):        {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Húsnæði meðhöndlað sem félagslegur réttur — sterkari opinber/óhagnaðardrifin hlutverki, "
                  "andstaða við spákaupmennsku á húsnæðismarkaði."},
    ("A", "lower_taxes"):           {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Andstaða við skattalækkanir á kostnað velferðar; vill nota borgarsjóð til fjárfestinga."},
    ("A", "expand_welfare"):        {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Velferðarþjónusta er kjarni stefnunnar."},
    ("A", "private_sector"):        {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Skeptísk gagnvart útvistun og einkavæðingu kjarna-þjónustu."},
    ("A", "climate_planning"):      {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Loftslagsmarkmið móta skipulags- og samgönguákvarðanir."},
    ("A", "immigration_inclusion"): {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Sterk áhersla á inngildingu, mannréttindi og þjónustu við innflytjendur."},
    ("A", "direct_democracy"):      {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Stuðningur við aukið íbúasamráð og áhrif íbúa á borgarmál."},
    ("A", "reduce_bureaucracy"):    {"certainty": "medium", "sources": [VINSTRID_SOURCE],
        "reason": "Engin sterk áhersla á einföldun stjórnsýslu — ekki andstæð, ekki drifkraftur."},
    ("A", "family_children"):       {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Stuðningur við leik- og grunnskóla, hluti af velferðar-fókus."},
    ("A", "elderly_services"):      {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Þjónusta við eldri borgara hluti af kjarnastefnu velferðar."},
    ("A", "culture_investment"):    {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Stuðningur við menningu og listir sem hluta af samfélagsuppbyggingu."},
    ("A", "municipal_operations"):  {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Sterkur opinber rekstur er kjarnaprinsíp; andstaða við einkavæðingu þjónustu."},
    ("A", "market_business"):       {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Skeptísk gagnvart því að atvinnulíf og markaður stýri ákvörðunum borgarinnar."},
    ("A", "green_protection"):      {"certainty": "high", "sources": [VINSTRID_SOURCE],
        "reason": "Vernd grænna svæða er hluti af loftslags- og umhverfisáherslu."},
    ("A", "practical_maintenance"): {"certainty": "medium", "sources": [VINSTRID_SOURCE],
        "reason": "Viðhald hluti af velferðarfókus en ekki stærsta sérstaða."},

    # ---------------------- G — Góðan daginn ----------------------
    ("G", "borgarlina_support"):    {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Efahyggja gagnvart dýrum samgönguverkefnum og hugmyndafræðimiðuðu skipulagi, "
                  "en ekki andstæð almenningssamgöngum almennt."},
    ("G", "more_bike_lanes"):       {"certainty": "low", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Engar áberandi yfirlýsingar í sjáanlegri stefnuskrá."},
    ("G", "parking_priority"):      {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Áhersla á aðgengi og praktískar lausnir í daglegri umferð."},
    ("G", "dense_housing"):         {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Skeptísk gagnvart þéttingu sem sjálfsmarkmiði."},
    ("G", "expand_outward"):        {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Áhersla á fjölskylduvænleg úthverfi og fjölbreytni í byggðamynstri."},
    ("G", "public_housing"):        {"certainty": "low", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Ekki sterk afstaða — ráðast af verkefnum og praktísku mati."},
    ("G", "lower_taxes"):           {"certainty": "high", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Skýr áhersla á aðhald í rekstri og lækkun skatta og gjalda."},
    ("G", "expand_welfare"):        {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Stuðningur við velferð innan rammans, hluti af kjarnaþjónustu — ekki útþensla."},
    ("G", "private_sector"):        {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Hógvær opnun fyrir aðkomu einkageirans í þjónustu þar sem það á við."},
    ("G", "climate_planning"):      {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Engin sterk loftslagsáhersla — ekki andstæð, ekki drifkraftur skipulagsákvarðana."},
    ("G", "immigration_inclusion"): {"certainty": "low", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Engin áberandi afstaða innan stefnuskrárinnar."},
    ("G", "direct_democracy"):      {"certainty": "high", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Áhersla á íbúasamráð og þátttöku íbúa í ákvörðunum."},
    ("G", "reduce_bureaucracy"):    {"certainty": "high", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Lykiláhersla — einfalda stjórnsýslu og minnka skrifræði."},
    ("G", "family_children"):       {"certainty": "high", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Skólar og fjölskyldur sem helsti forgangur."},
    ("G", "elderly_services"):      {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Áhersla á örugga grunnþjónustu fyrir eldri borgara."},
    ("G", "culture_investment"):    {"certainty": "low", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Ekki áberandi áhersla."},
    ("G", "municipal_operations"):  {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Áhersla á rekstrarhagkvæmni — opin fyrir samvinnu þvert á einka- og opinbera-geira."},
    ("G", "market_business"):       {"certainty": "high", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Sterk áhersla á atvinnulíf, samkeppnishæfni og störf."},
    ("G", "green_protection"):      {"certainty": "medium", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Áhersla á græn svæði sem hluta af lífsgæðum hverfa."},
    ("G", "practical_maintenance"): {"certainty": "high", "sources": [GODAN_DAGINN_SOURCE],
        "reason": "Lykiláhersla — gæðaviðhald og dagleg þjónusta í forgangi."},

    # ---------------------- R — Okkar borg ----------------------
    ("R", "borgarlina_support"):    {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Skýr andstaða við Borgarlínu sem skipulagða umferðarbyltingu."},
    ("R", "more_bike_lanes"):       {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Skeptísk gagnvart áframhaldandi þrengingu fyrir bílaumferð."},
    ("R", "parking_priority"):      {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Sterk áhersla á aðgengi einkabíla og bílastæði."},
    ("R", "dense_housing"):         {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Skýr andstaða við þéttingu byggðar — vill vernda úthverfaveruleika."},
    ("R", "expand_outward"):        {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Áhersla á fjölskyldu- og úthverfa-vænleg svæði."},
    ("R", "public_housing"):        {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Skeptísk gagnvart þenslu opinbers húsnæðis."},
    ("R", "lower_taxes"):           {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Sterk áhersla á lækkun skatta og minnkun útgjalda."},
    ("R", "expand_welfare"):        {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Hógvær afstaða — kjarnaþjónusta í forgangi en ekki útþensla velferðar."},
    ("R", "private_sector"):        {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Áhersla á einkaframtak og útvistun þar sem það á við."},
    ("R", "climate_planning"):      {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Skeptísk gagnvart loftslagsmiðuðu skipulagi sem grundvelli ákvarðana."},
    ("R", "immigration_inclusion"): {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Skarpari afstaða gagnvart innflytjendum og hælisleitendum en flest önnur framboð í Reykjavík."},
    ("R", "direct_democracy"):      {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Áhersla á rödd íbúa, þó ekki jafn áberandi og hjá Pírötum."},
    ("R", "reduce_bureaucracy"):    {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Sterk áhersla á einföldun stjórnsýslu og minnkun skrifræðis."},
    ("R", "family_children"):       {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Áhersla á fjölskylduvænleika í úthverfum."},
    ("R", "elderly_services"):      {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Stuðningur við þjónustu við eldri, þó ekki helsta áhersla."},
    ("R", "culture_investment"):    {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Ekki sterk áhersla — kjarnaþjónusta í forgangi."},
    ("R", "municipal_operations"):  {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Áhersla á að einkageirinn taki að sér þjónustu þar sem hægt er."},
    ("R", "market_business"):       {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Stuðningur við atvinnulíf, þó ekki helsta áhersla."},
    ("R", "green_protection"):      {"certainty": "medium", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Áhersla á græn svæði en innan rammans af úthverfa-skipulagi."},
    ("R", "practical_maintenance"): {"certainty": "high", "sources": [OKKAR_BORG_SOURCE],
        "reason": "Lykiláhersla — kjarnaþjónusta og viðhald í forgangi."},
}




# ---------------------------------------------------------------------------
# Heimildir og röksemd fyrir framboð sem voru uppfærð 2026-05-07.
# Bætast við DETAIL_OVERRIDES fyrir A/G/R sem þegar er búið að skilgreina.
# ---------------------------------------------------------------------------

_FRAMSOKN_SOURCES = [
    "https://www.framsoknrvk.is/",
    "https://www.framsokn.is/sveitarfelog/reykjavik",
    "https://www.ruv.is/frettir/innlent/2026-04-29-framsokn-bodar-reykjavik-a-graenu-ljosi",
]
_VIDREISN_SOURCES = [
    "https://www.vidreisnreykjavik.is/stefna",
    "https://vidreisn.is/reykjavik/",
]
_XD_SOURCES = [
    "https://xd.is/sveitarstjornarkosningar/reykjavikurborg/",
    "https://xd.is/stefnan/",
]
_FLOKKUR_FOLKS_SOURCES = [
    "https://flokkurfolksins.is/reykjavik/",
    "https://flokkurfolksins.is/reykjavik/aherslumal.html",
    "https://www.ruv.is/frettir/innlent/2026-04-24-flokkur-folksins-kynnir-aherslumalin-i-borginni",
]
_SOSIAL_SOURCES = [
    "https://www.sosialistaflokkurinn.is/stefna",
    "https://www.sosialistaflokkurinn.is/media-kit/stefna/sosialistar-stefnuskra-rvk-2026.pdf",
]
_MID_SOURCES = [
    "https://midflokkurinn.is/reykjavik",
    "https://midflokkurinn.is/stefna/samgongumal-sundabraut-og-borgarlina",
    "https://midflokkurinn.is/midflokkurinn-hefur-lausnir-a-husnaedismarkadi",
]
_PIRATAR_SOURCES = [
    "https://piratar.is/bestumborgina2026",
    "https://piratar.is/stefna",
]
_SAMFY_SOURCES = [
    "https://xs.is/reykjavik",
    "https://xs.is/",
]


def _ext_overrides():
    out = {}

    # B — Framsókn (heimildir 2026-05-07)
    B = {
        "borgarlina_support":    ("medium", "Hóflegur stuðningur við bættar samgöngur — hvorki andstaða né sterk talsmaður."),
        "more_bike_lanes":       ("medium", "Stuðningur við virkar samgöngur sem hluta af jafnvægi."),
        "parking_priority":      ("medium", "Jafnvægi milli bíla og virkra samgangna; engin sterk afstaða."),
        "dense_housing":         ("medium", "Hóflegur stuðningur við þéttingu sem hluta af húsnæðisuppbyggingu."),
        "expand_outward":        ("medium", "Engin sterk afstaða — opin fyrir blönduðu mynstri."),
        "public_housing":        ("medium", "Hóflegur stuðningur við opinber/óhagnaðardrifin húsnæði."),
        "lower_taxes":           ("medium", "Hófsöm afstaða — hvorki útþensla útgjalda né niðurskurður."),
        "expand_welfare":        ("medium", "Hóflegur stuðningur, með hverfaþjónustu og fjölskyldumál í forgangi."),
        "private_sector":        ("medium", "Engin ákveðin afstaða — opin fyrir samvinnu þvert á geira."),
        "climate_planning":      ("medium", "Hófleg loftslagsáhersla — „grænt ljós“-frasinn bendir á blandaða nálgun."),
        "immigration_inclusion": ("medium", "Hóflegt inngildingar-viðhorf í samræmi við miðjuímynd."),
        "direct_democracy":      ("medium", "Hverfa- og íbúasamráð sem hluti af praktískri stjórnsýslu."),
        "reduce_bureaucracy":    ("medium", "Áhersla á smurta borgarrekstur og að einfalda daglegt líf."),
        "family_children":       ("high",   "Sterk áhersla á börn, fjölskyldur og hverfaþjónustu — kjarnaforgangur."),
        "elderly_services":      ("high",   "Þjónusta við eldri borgara í forgangi, sambærilegt fjölskyldumálum."),
        "culture_investment":    ("medium", "Hófleg menningar-áhersla — hluti af lífsgæða-fókus hverfa."),
        "municipal_operations":  ("medium", "Engin sterk afstaða — opin fyrir samvinnu þvert á geira."),
        "market_business":       ("medium", "Hófleg atvinnu-áhersla sem hluti af jafnvægisáherslu."),
        "green_protection":      ("medium", "Áhersla á græn svæði sem hluta af lífsgæðum hverfa."),
        "practical_maintenance": ("high",   "„Reykjavík á grænu ljósi“ — kjarni framboðs er smurð borgarrekstur."),
    }
    for axis, (cert, reason) in B.items():
        out[("B", axis)] = {"certainty": cert, "reason": reason, "sources": _FRAMSOKN_SOURCES}

    # C — Viðreisn
    C = {
        "borgarlina_support":    ("high",   "Skýr stuðningur við Borgarlínu og kortershverfi."),
        "more_bike_lanes":       ("high",   "Áhersla á virkar samgöngur sem hluta af 15-mín-borg."),
        "parking_priority":      ("medium", "Skipulags-pragmatísk afstaða — minni car-centric en hægri-flokkar."),
        "dense_housing":         ("high",   "Stuðningur við þétt service-accessible urbanism og einföldun uppbyggingar."),
        "expand_outward":        ("medium", "Skeptísk gagnvart útþenslu — vill nýta núverandi byggð betur."),
        "public_housing":        ("medium", "Stuðningur við blandað kerfi, ekki anti-market."),
        "lower_taxes":           ("medium", "Áhersla á efficiency, fewer managers, ekki full austerity."),
        "expand_welfare":        ("medium", "Stuðningur við sterka borgarþjónustu en ekki municipal-expansionist."),
        "private_sector":        ("high",   "Pro-business modernization — auðveldari rekstrar-umhverfi atvinnulífs."),
        "climate_planning":      ("high",   "Sjálfbærni samþætt í skipulags-fílósófíu og samgöngum."),
        "immigration_inclusion": ("high",   "Frjálslynd, jafnræðis-, og inngildingar-áhersla."),
        "direct_democracy":      ("medium", "Liberal-praktísk áhersla á aðgengi og íbúasamráð."),
        "reduce_bureaucracy":    ("high",   "Sterk áhersla á minni skrifræði og einfaldari stjórnsýslu."),
        "family_children":       ("medium", "Stuðningur við skóla og fjölskyldumál sem hluta af lífsgæðum."),
        "elderly_services":      ("medium", "Stuðningur en ekki helsta sérstaða."),
        "culture_investment":    ("medium", "Hófleg áhersla, hluti af modern-cosmopolitan identitet."),
        "municipal_operations":  ("high",   "Skeptísk gagnvart sterkum opinberum rekstri — efficiency-first."),
        "market_business":       ("high",   "Skýr business-friendly municipal governance."),
        "green_protection":      ("high",   "Vernd grænna svæða hluti af sjálfbærni-fókus."),
        "practical_maintenance": ("medium", "Hluti af modern city governance — ekki helsta sérstaða."),
    }
    for axis, (cert, reason) in C.items():
        out[("C", axis)] = {"certainty": cert, "reason": reason, "sources": _VIDREISN_SOURCES}

    # D — Sjálfstæðisflokkurinn
    D = {
        "borgarlina_support":    ("medium", "Skeptísk gagnvart núverandi útfærslu Borgarlínu — innri ágreiningur viðurkenndur."),
        "more_bike_lanes":       ("medium", "Hlutlaus til hógvær — ekki andstæð, ekki drifkraftur."),
        "parking_priority":      ("high",   "Skýr áhersla á aðgengi einkabíla og bílastæði."),
        "dense_housing":         ("medium", "Stuðningur við hraða uppbyggingu með market-driven framework."),
        "expand_outward":        ("medium", "Hófleg afstaða — opin fyrir markaðsdrifinn supply."),
        "public_housing":        ("medium", "Skeptísk gagnvart þenslu opinbers húsnæðis."),
        "lower_taxes":           ("high",   "Sterk áhersla á aðhald, lægri gjöld, anti-bureaucratic."),
        "expand_welfare":        ("medium", "Ekki andstæð velferð — efficiency-first nálgun."),
        "private_sector":        ("high",   "Sterkt pro-private og útvistun þar sem það á við."),
        "climate_planning":      ("medium", "Acknowledged en secondary — practicality first."),
        "immigration_inclusion": ("low",    "Lítil municipal-specific stefna — meira nationally-oriented."),
        "direct_democracy":      ("medium", "Engin sterk umbóta-áhersla."),
        "reduce_bureaucracy":    ("high",   "Sterk anti-bureaucratic positioning."),
        "family_children":       ("medium", "Stuðningur við skóla og fjölskyldumál — hluti af kjarnaþjónustu."),
        "elderly_services":      ("medium", "Hóflegur stuðningur, hluti af kjarnaþjónustu."),
        "culture_investment":    ("medium", "Ekki sterk áhersla."),
        "municipal_operations":  ("high",   "Skýrt anti-strong-public-role; einkamarkaður leysir flest."),
        "market_business":       ("high",   "Skýrt business-friendly municipal governance."),
        "green_protection":      ("medium", "Hófleg afstaða — ekki primary."),
        "practical_maintenance": ("medium", "Hluti af kjarnaþjónustu en ekki helsta sérstaða."),
    }
    for axis, (cert, reason) in D.items():
        out[("D", axis)] = {"certainty": cert, "reason": reason, "sources": _XD_SOURCES}

    # F — Flokkur fólksins
    F = {
        "borgarlina_support":    ("medium", "Skeptísk en ekki eins sterk og Okkar borg eða Miðflokkurinn."),
        "more_bike_lanes":       ("medium", "Hófleg skeptísk — ekki primary."),
        "parking_priority":      ("medium", "Stuðningur við aðgengi bíla í daglegu lífi, parking accessibility."),
        "dense_housing":         ("medium", "Gagnrýnir „ofurþéttingu“ en styður mannlegri skipulag."),
        "expand_outward":        ("medium", "Engin sterk afstaða — opin fyrir blönduðu mynstri."),
        "public_housing":        ("medium", "Stuðningur við húsnæðisöryggi og affordable supply."),
        "lower_taxes":           ("medium", "Ekki niðurskurðar-flokkur, áhersla á ráðdeild."),
        "expand_welfare":        ("high",   "Velferð er sterkasti kjarni framboðsins."),
        "private_sector":        ("medium", "Engin sterk afstaða."),
        "climate_planning":      ("low",    "Ekki primary identity — secondary concern."),
        "immigration_inclusion": ("low",    "Ekki sterk municipal-policy specificity."),
        "direct_democracy":      ("medium", "Populískt-praktísk áhersla, anti-system rhetoric."),
        "reduce_bureaucracy":    ("medium", "Áhersla á einfalda ferla fyrir borgara."),
        "family_children":       ("medium", "Stuðningur, hófleg áhersla — eldri borgarar eru sterkari."),
        "elderly_services":      ("high",   "Eldri borgarar sem fyrsti forgangur — kjarni framboðsins."),
        "culture_investment":    ("low",    "Ekki áhersla — kjarnaþjónusta í forgangi."),
        "municipal_operations":  ("medium", "Engin sterk afstaða — service-focus, ekki ideologi."),
        "market_business":       ("medium", "Engin sterk afstaða."),
        "green_protection":      ("medium", "Stuðningur en ekki primary."),
        "practical_maintenance": ("high",   "Praktísk daglega þjónusta og kjarnastoðir hverfa."),
    }
    for axis, (cert, reason) in F.items():
        out[("F", axis)] = {"certainty": cert, "reason": reason, "sources": _FLOKKUR_FOLKS_SOURCES}

    # J — Sósíalistar
    J = {
        "borgarlina_support":    ("high",   "Sterkur stuðningur við public transport sem public infrastructure."),
        "more_bike_lanes":       ("high",   "Stuðningur við virkar samgöngur og minni bíla-háð."),
        "parking_priority":      ("high",   "Skýrt anti-car-priority."),
        "dense_housing":         ("high",   "Stuðningur við þéttingu sem hluta af húsnæðis-mannréttindum."),
        "expand_outward":        ("high",   "Andstaða við bíla-háð úthverfa-stækkun."),
        "public_housing":        ("high",   "Reykjavík Construction Company, anti-spákaupmennska, public housing er kjarni."),
        "lower_taxes":           ("high",   "Skýrt anti-skattalækkanir; pro-redistribution."),
        "expand_welfare":        ("high",   "Velferðar-fyrst — kjarni framboðs."),
        "private_sector":        ("high",   "Skýr anti-privatization, anti-útvistun."),
        "climate_planning":      ("medium", "Mikilvægt en ekki primary identity — economic restructuring er kjarni."),
        "immigration_inclusion": ("high",   "Sterk inngilding, social equality, vulnerable rights."),
        "direct_democracy":      ("high",   "Þátttöku-lýðræði og residenta-empowerment."),
        "reduce_bureaucracy":    ("medium", "Ekki primary — public provision er kjarni."),
        "family_children":       ("high",   "Skólar, jafn aðgangur, tungumáls-stuðningur, börn innflytjenda."),
        "elderly_services":      ("high",   "Heim-aðstoð, virðing eldri borgara, social guarantees."),
        "culture_investment":    ("high",   "Stuðningur við menningu og listir sem hluta af samfélagsuppbyggingu."),
        "municipal_operations":  ("high",   "Sterkur opinber rekstur sem valdatæki gegn markaði."),
        "market_business":       ("high",   "Skýrt -2: ekki business-first, public provision er kjarni."),
        "green_protection":      ("high",   "Vernd grænna svæða hluti af municipal-public-good logík."),
        "practical_maintenance": ("medium", "Stuðningur við daglega þjónustu, hluti af kjarnastoðum."),
    }
    for axis, (cert, reason) in J.items():
        out[("J", axis)] = {"certainty": cert, "reason": reason, "sources": _SOSIAL_SOURCES}

    # M — Miðflokkurinn
    M = {
        "borgarlina_support":    ("high",   "Skýr andstaða við Borgarlínu eins og hún er nú."),
        "more_bike_lanes":       ("medium", "Skeptísk gagnvart áframhaldandi þrengingar fyrir bílaumferð."),
        "parking_priority":      ("high",   "Sterk pro-car accessibility, gegn restrictions."),
        "dense_housing":         ("medium", "Anti-density urbanism, en pro-housing supply."),
        "expand_outward":        ("high",   "Pro-suburban expansion, pro-Sundabraut, pro-road infrastructure."),
        "public_housing":        ("medium", "Skeptísk gagnvart opinberri húsnæðisþenslu."),
        "lower_taxes":           ("high",   "Anti-skattahækkanir, anti-vegrtollar, anti-km-skattar."),
        "expand_welfare":        ("medium", "Stuðningur við praktíska velferð en ekki kjarni."),
        "private_sector":        ("medium", "Pro-development og minna skrifræði — ekki technocratic."),
        "climate_planning":      ("medium", "Secondary, deprioritized vs. transport practicality."),
        "immigration_inclusion": ("low",    "Skarpari national rhetoric en municipal-specific weaker."),
        "direct_democracy":      ("medium", "Engin sterk umbóta-áhersla."),
        "reduce_bureaucracy":    ("high",   "Anti-bureaucratic development philosophy."),
        "family_children":       ("medium", "Hófleg áhersla, ekki kjarnasérstaða."),
        "elderly_services":      ("medium", "Stuðningur en ekki primary."),
        "culture_investment":    ("medium", "Ekki sterk áhersla."),
        "municipal_operations":  ("high",   "Skýrt anti-strong-public-role."),
        "market_business":       ("medium", "Pro-development, en ekki technocratic-business."),
        "green_protection":      ("medium", "Hófleg skeptísk — pro-development tilhneiging."),
        "practical_maintenance": ("medium", "Hluti af pragmatic governance áherslu."),
    }
    for axis, (cert, reason) in M.items():
        out[("M", axis)] = {"certainty": cert, "reason": reason, "sources": _MID_SOURCES}

    # P — Píratar
    P = {
        "borgarlina_support":    ("high",   "Skýr stuðningur við virkar samgöngur og almenningssamgöngur."),
        "more_bike_lanes":       ("high",   "Sjálfbær mobility — kjarni samgöngustefnu."),
        "parking_priority":      ("high",   "Anti-car-dependency, pro-active mobility."),
        "dense_housing":         ("medium", "Stuðningur við þéttingu sem hluta af mannréttinda-skipulagi."),
        "expand_outward":        ("medium", "Skeptísk gagnvart útþenslu."),
        "public_housing":        ("medium", "Stuðningur við sanngirni og aðgengi, ekki anti-market."),
        "lower_taxes":           ("low",    "Engin sterk fjárlaga-stefna — focus á transparency og value."),
        "expand_welfare":        ("medium", "Stuðningur við aðgengilegar þjónustur, ekki primary."),
        "private_sector":        ("medium", "Engin sterk afstaða — focus á digital reform."),
        "climate_planning":      ("high",   "Sjálfbærni og loftslags-conscious skipulag."),
        "immigration_inclusion": ("high",   "Mannréttindi, LGBTQ+, anti-prejudice — skýr +2."),
        "direct_democracy":      ("high",   "Sterkasta lýðræðis-umbóta-áhersla í kerfinu."),
        "reduce_bureaucracy":    ("high",   "Stafrænar þjónustur, einfalda lif íbúa."),
        "family_children":       ("medium", "Stuðningur en ekki primary differentiator."),
        "elderly_services":      ("medium", "Stuðningur við aðgengi en ekki primary."),
        "culture_investment":    ("high",   "Menning og grassroots þátttaka mikilvæg."),
        "municipal_operations":  ("medium", "Hluti af digital-public-service nálgun."),
        "market_business":       ("medium", "Digital-first simplification getur verið efficiency-friendly."),
        "green_protection":      ("high",   "Vernd grænna svæða hluti af sjálfbærni-áherslu."),
        "practical_maintenance": ("medium", "Hluti af digital city services nálgun."),
    }
    for axis, (cert, reason) in P.items():
        out[("P", axis)] = {"certainty": cert, "reason": reason, "sources": _PIRATAR_SOURCES}

    # S — Samfylkingin
    S = {
        "borgarlina_support":    ("high",   "Skýr stuðningur við Borgarlínu og institutional sustainable mobility."),
        "more_bike_lanes":       ("high",   "Stuðningur við virkar samgöngur og loftslagsmiðað skipulag."),
        "parking_priority":      ("medium", "Pragmatísk afstaða — institutional, ekki radical anti-car."),
        "dense_housing":         ("high",   "Húsnæðisuppbygging og þétt service-oriented urbanism."),
        "expand_outward":        ("high",   "Skeptísk gagnvart útþenslu — vill þétt sustainable byggð."),
        "public_housing":        ("high",   "Strong public role í húsnæðisstefnu — Nordic social-democratic."),
        "lower_taxes":           ("medium", "Investment-heavy en pragmatic — ekki revolutionary expansionism."),
        "expand_welfare":        ("high",   "Identity pillar — strong public services og equality."),
        "private_sector":        ("medium", "Mixed-economy stance, institutional governance."),
        "climate_planning":      ("high",   "Loftslag deeply integrated í planning."),
        "immigration_inclusion": ("high",   "Strong inclusion/human-rights orientation, Nordic social-democratic."),
        "direct_democracy":      ("medium", "Stuðningur en ekki primary differentiator."),
        "reduce_bureaucracy":    ("medium", "Institutional governance — ekki primary."),
        "family_children":       ("high",   "Skólar og fjölskyldumál sem kjarni — equal opportunity."),
        "elderly_services":      ("high",   "Hluti af strong public services áherslu."),
        "culture_investment":    ("high",   "Stuðningur við menningu sem hluta af lífsgæðum."),
        "municipal_operations":  ("high",   "Welfare-managerial institutional governance."),
        "market_business":       ("medium", "Mixed-economy, ekki primary."),
        "green_protection":      ("high",   "Vernd grænna svæða hluti af sjálfbærni-fókus."),
        "practical_maintenance": ("medium", "Institutional governance — hluti af stable management."),
    }
    for axis, (cert, reason) in S.items():
        out[("S", axis)] = {"certainty": cert, "reason": reason, "sources": _SAMFY_SOURCES}

    return out


_NEW_OVERRIDES = _ext_overrides()
DETAIL_OVERRIDES.update(_NEW_OVERRIDES)


# ---------------------------------------------------------------------------
# Sjálfgefin röksemd ef DETAIL_OVERRIDES er ekki tilgreint
# ---------------------------------------------------------------------------

_DEFAULT_REASON = {
    "high":   "Mat byggt á þekktri stefnu landsflokksins — borgarstjórnarútgáfa krefst staðfestingar.",
    "medium": "Bráðabirgða mat — krefst frekari staðfestingar á borgarstjórnarstefnuskrá 2026.",
    "low":    "Ekki nægar opinberar heimildir á þessum tímapunkti — flokkað sem óljóst.",
}


def _build_details() -> Dict[str, Dict[str, Dict]]:
    """Byggir POLICY_MATRIX_DETAILS úr stigatöflu, vissustigum, heimildum og overrides."""
    out = {}
    for axis_id, scores in POLICY_MATRIX.items():
        out[axis_id] = {}
        for code, score in scores.items():
            override = DETAIL_OVERRIDES.get((code, axis_id), {})

            if "certainty" in override:
                cert = override["certainty"]
            else:
                pa = PARTY_CERTAINTY.get(code, {}).get("per_axis", {})
                cert = pa.get(axis_id, PARTY_CERTAINTY.get(code, {}).get("overall", "low"))

            reason = override.get("reason", _DEFAULT_REASON.get(cert, ""))
            sources = override.get("sources", POLICY_SOURCES.get((code, axis_id), []))

            out[axis_id][code] = {
                "score": score,
                "certainty": cert,
                "reason": reason,
                "sources": list(sources),
            }
    return out


POLICY_MATRIX_DETAILS: Dict[str, Dict[str, Dict]] = _build_details()


# ---------------------------------------------------------------------------
# Veldur villum sem þarfnast handvirkrar lagfæringar.
# ---------------------------------------------------------------------------

def _validate_matrix() -> None:
    expected_parties = {"A", "B", "C", "D", "F", "G", "J", "M", "P", "R", "S"}
    for axis_id, scores in POLICY_MATRIX.items():
        if set(scores.keys()) != expected_parties:
            raise ValueError(
                f"POLICY_MATRIX[{axis_id!r}] vantar lykla: "
                f"{expected_parties - set(scores.keys())}"
            )
        for code, val in scores.items():
            if val not in (-2, -1, 0, 1, 2):
                raise ValueError(f"Ógilt stig í [{axis_id}][{code}]: {val}")


_validate_matrix()


# ---------------------------------------------------------------------------
# Greiningarföll
# ---------------------------------------------------------------------------

def party_vector(party_letter: str) -> Dict[str, int]:
    """Skilar dict (axis_id -> stig) fyrir tiltekið framboð."""
    return {axis_id: POLICY_MATRIX[axis_id][party_letter] for axis_id in POLICY_AXIS_IDS}


def axis_distance(p1: str, p2: str) -> float:
    """Manhattan-vegalengd milli tveggja framboða yfir öll axis (0..80)."""
    v1 = party_vector(p1)
    v2 = party_vector(p2)
    return sum(abs(v1[a] - v2[a]) for a in POLICY_AXIS_IDS)


def all_party_pairs() -> List[Tuple[str, str]]:
    parties = list(POLICY_MATRIX[POLICY_AXIS_IDS[0]].keys())
    pairs = []
    for i, a in enumerate(parties):
        for b in parties[i + 1:]:
            pairs.append((a, b))
    return pairs


def strongest_opposites(top_n: int = 3) -> List[Tuple[str, str, float]]:
    """Skilar (a, b, vegalengd) fyrir framboðspör með MESTA mun. Stærsta fyrst."""
    pairs = [(a, b, axis_distance(a, b)) for a, b in all_party_pairs()]
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs[:top_n]


def most_similar_pairs(top_n: int = 3) -> List[Tuple[str, str, float]]:
    """Skilar (a, b, vegalengd) fyrir framboðspör með MINNSTA mun. Smæst fyrst.

    Sleppum pörum þar sem bæði eru með "low" overall vissu (því þá segir
    samanburðurinn meira um skort á gögnum en raunverulegan skyldleika).
    """
    pairs = [(a, b, axis_distance(a, b)) for a, b in all_party_pairs()]
    pairs.sort(key=lambda x: x[2])
    out = []
    for a, b, d in pairs:
        if PARTY_CERTAINTY[a]["overall"] == "low" and PARTY_CERTAINTY[b]["overall"] == "low":
            continue
        out.append((a, b, d))
        if len(out) >= top_n:
            break
    return out


def biggest_disagreement_axes(top_n: int = 5) -> List[Tuple[str, int]]:
    """Skilar (axis_id, max - min) — ásar þar sem framboð eru lengst í sundur."""
    out = []
    for axis_id in POLICY_AXIS_IDS:
        scores = list(POLICY_MATRIX[axis_id].values())
        out.append((axis_id, max(scores) - min(scores)))
    out.sort(key=lambda x: x[1], reverse=True)
    return out[:top_n]


def axes_where_parties_overlap(min_agreement_threshold: int = 1) -> List[str]:
    """Skilar lista yfir ása þar sem öll framboð eru annað hvort sammála eða hlutlaus.

    Nákvæmari skilyrði: max(scores) - min(scores) <= 1 OG ekkert framboð er á
    öndverðu meiði (öll stig á sama merki eða 0).
    """
    out = []
    for axis_id in POLICY_AXIS_IDS:
        scores = list(POLICY_MATRIX[axis_id].values())
        if max(scores) - min(scores) <= 1:
            out.append(axis_id)
    return out


def strongest_priorities(party_letter: str, top_n: int = 3) -> List[Tuple[str, int]]:
    v = party_vector(party_letter)
    sorted_axes = sorted(v.items(), key=lambda x: x[1], reverse=True)
    return [(a, s) for a, s in sorted_axes if s >= 1][:top_n]


def strongest_oppositions(party_letter: str, top_n: int = 3) -> List[Tuple[str, int]]:
    v = party_vector(party_letter)
    sorted_axes = sorted(v.items(), key=lambda x: x[1])
    return [(a, s) for a, s in sorted_axes if s <= -1][:top_n]


def ambiguous_axes(party_letter: str) -> List[str]:
    """Ásar þar sem stig er 0 — vísbending um óljósa eða blandaða afstöðu."""
    v = party_vector(party_letter)
    return [a for a, s in v.items() if s == 0]


def potential_contradictions(party_letter: str) -> List[Tuple[str, str]]:
    """Skilar pörum af ásum sem virðast stinga í stúf við hvor annan.

    Þetta er heuristic — meiri rannsókn er nauðsynleg áður en þú fullyrðir
    að um sé að ræða raunverulegt mótsögn í stefnunni.
    """
    v = party_vector(party_letter)
    contradictions = []
    pairs_to_check = [
        ("expand_welfare", "lower_taxes",
         "Vill auka velferðarútgjöld en lækka jafnframt skatta/gjöld."),
        ("dense_housing", "expand_outward",
         "Vill bæði þétta byggð og þenjast út — þarfnast nánari útskýringar."),
        ("municipal_operations", "private_sector",
         "Vill bæði sterkan opinberan rekstur og aukna aðkomu einkageirans."),
        ("borgarlina_support", "parking_priority",
         "Vill bæði Borgarlínu og einkabíla-forgang á sama tíma."),
    ]
    for a1, a2, label in pairs_to_check:
        if v[a1] >= 1 and v[a2] >= 1:
            contradictions.append((f"{a1} ↔ {a2}", label))
    return contradictions


def get_detail(party_letter: str, axis_id: str) -> Dict:
    """Skilar (score, certainty, reason, sources) sem dict fyrir tiltekna færslu."""
    return POLICY_MATRIX_DETAILS[axis_id][party_letter]


def get_certainty(party_letter: str, axis_id: str | None = None) -> str:
    if axis_id is None:
        return PARTY_CERTAINTY.get(party_letter, {}).get("overall", "low")
    return POLICY_MATRIX_DETAILS[axis_id][party_letter]["certainty"]


def get_reason(party_letter: str, axis_id: str) -> str:
    return POLICY_MATRIX_DETAILS[axis_id][party_letter]["reason"]


def get_sources(party_letter: str, axis_id: str) -> List[str]:
    return list(POLICY_MATRIX_DETAILS[axis_id][party_letter]["sources"])


def overall_evidence_score(party_letter: str) -> float:
    """Heildar-vissa á bilinu 0..1 byggt á per-axis vissustigi.
    high = 1.0, medium = 0.55, low = 0.15."""
    weights = {"high": 1.0, "medium": 0.55, "low": 0.15}
    total = 0.0
    for axis_id in POLICY_AXIS_IDS:
        cert = POLICY_MATRIX_DETAILS[axis_id][party_letter]["certainty"]
        total += weights.get(cert, 0.15)
    return total / len(POLICY_AXIS_IDS)


# ---------------------------------------------------------------------------
# Sjálfprófun
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Stærstu andstæðingar:")
    for a, b, d in strongest_opposites():
        print(f"  {a} ↔ {b}  (vegalengd {d})")
    print("\nLíkustu pör:")
    for a, b, d in most_similar_pairs():
        print(f"  {a} ≈ {b}  (vegalengd {d})")
    print("\nMesta ósamstaða á ásum:")
    for axis_id, spread in biggest_disagreement_axes():
        print(f"  {POLICY_AXIS_LOOKUP[axis_id]['label']}  (spread {spread})")
    print("\nÁsar þar sem framboð eru að mestu sammála:")
    for axis_id in axes_where_parties_overlap():
        print(f"  {POLICY_AXIS_LOOKUP[axis_id]['label']}")
    print("\nMögulegar mótsagnir per framboð:")
    for code in "ABCDFGJMPRS":
        c = potential_contradictions(code)
        if c:
            print(f"  {code}: {c}")
