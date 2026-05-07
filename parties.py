"""
Gögn um framboð til borgarstjórnar Reykjavíkur 2026.

ATHUGIÐ: Allar tölur og lýsingar í þessari skrá eru bráðabirgða mat sem þarf
að yfirfara handvirkt áður en þetta tól er birt opinberlega. Sjá DATA_REVIEW.md.

Stigagjöf á hverjum stefnuás er á bilinu -2 til +2:
    -2  sterk andstaða / lágur forgangur
    -1  frekar andstæð / lágur forgangur
     0  hlutlaust / blandað / óvíst
    +1  frekar samþykk / hár forgangur
    +2  sterkur stuðningur / hæsti forgangur

Engar fullyrðingar um stefnu framboðs eru kynntar sem staðreyndir hér.
Tólið sýnir aðeins nánd milli notandasvara og þessa mats.
"""

# Stefnuásar (ID, sýnilegt heiti á íslensku)
AXES = [
    ("velferd",       "Velferð og félagsleg þjónusta"),
    ("skattar",       "Skattar, gjöld og fjármál borgarinnar"),
    ("bilar",         "Bílar, bílastæði og umferð"),
    ("borgarlina",    "Borgarlína og almenningssamgöngur"),
    ("husnaedi",      "Húsnæðisuppbygging og þétting byggðar"),
    ("loftslag",      "Loftslag, náttúra og græn svæði"),
    ("skolar",        "Skólar, leikskólar og fjölskyldumál"),
    ("eldri",         "Eldri borgarar"),
    ("atvinnu",       "Atvinnulíf, nýsköpun og skilvirkni"),
    ("lydraedi",      "Lýðræði, gagnsæi og íbúasamráð"),
    ("innflytjendur", "Innflytjendamál, mannréttindi og inngilding"),
    ("menning",       "Menning, íþróttir og frístundir"),
]

AXIS_LABELS = dict(AXES)
AXIS_IDS = [a for a, _ in AXES]

# Stutt útskýring á stefnu hvers áss (sýnt á aðferðafræðisíðu).
AXIS_DIRECTION_NOTES = {
    "velferd":       "+ þýðir aukin útgjöld og umfang velferðarþjónustu.",
    "skattar":       "+ þýðir vilji til hærri skatta/gjalda til að fjármagna þjónustu; − þýðir áhersla á aðhald og lægri gjöld.",
    "bilar":         "+ þýðir forgangur einkabíla og bílastæða; − þýðir forgangur hjólandi og gangandi.",
    "borgarlina":    "+ þýðir kröftugur stuðningur við Borgarlínu; − þýðir efahyggja eða andstaða.",
    "husnaedi":      "+ þýðir áhersla á þéttingu byggðar; − þýðir áhersla á útþenslu eða lágreist hverfi.",
    "loftslag":      "+ þýðir að loftslags- og umhverfismál móti ákvarðanir.",
    "skolar":        "+ þýðir hár forgangur leik- og grunnskóla og fjölskyldumála.",
    "eldri":         "+ þýðir hár forgangur þjónustu við eldri borgara.",
    "atvinnu":       "+ þýðir áhersla á atvinnulíf, einkarekstur og skilvirkni; − þýðir áhersla á opinberan rekstur.",
    "lydraedi":      "+ þýðir áhersla á íbúasamráð, gagnsæi og beint lýðræði.",
    "innflytjendur": "+ þýðir áhersla á inngildingu, mannréttindi og þjónustu við innflytjendur.",
    "menning":       "+ þýðir áhersla á aukinn stuðning við menningu, íþróttir og frístundir.",
}


# ---------------------------------------------------------------------------
# Slagorð / hallærislegasta slagorð
# ---------------------------------------------------------------------------
# Notandinn óskaði eftir sérstökum reit fyrir „minnisstæðasta / hallærislegasta
# slagorð“. Þetta er valkvætt og á aðeins að innihalda STAÐFEST raunveruleg
# slagorð frá viðkomandi framboði. Aldrei skal búa til tilvitnanir eða
# skálduð slagorð — það getur talist meiðyrði eða afbökun.
#
# Sjálfgefið er „Engin staðfest hallærisleg slaglína fundin — bættu við
# handvirkt.“ Þú þarft að staðfesta heimildir fyrir hverjum streng áður en
# tólið er birt opinberlega.
# ---------------------------------------------------------------------------
DEFAULT_TAGLINE = "Engin staðfest hallærisleg slaglína fundin — bættu við handvirkt."


def _scores(**kwargs):
    """Hjálparfall sem fyllir alla ása með 0 ef ekki tilgreint."""
    base = {a: 0 for a in AXIS_IDS}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# Framboð
# ---------------------------------------------------------------------------
# ATHUGIÐ: list_letter er stafurinn á kjörseðli. Vefslóðir og lógó eru
# bráðabirgða — sjá DATA_REVIEW.md fyrir lista yfir það sem þarf að staðfesta.
# Litir eru notaðir hóflega í UI og eru ekki ætlaðir sem skoðanaleg yfirlýsing.
# ---------------------------------------------------------------------------
PARTIES = {
    "A": {
        "list_letter": "A",
        "name": "Vinstrihreyfingin – grænt framboð",
        "short_name": "Vinstrið",
        "logo": "assets/logos/a-vinstrid.png",
        "color": "#2E7D32",
        "website": "https://vinstrid.is/",
        "policy_url": "https://vinstrid.is/",
        "summary": (
            "Húsnæði sem félagslegur réttur, sterk loftslags- og samgöngustefna, "
            "öflug almannaþjónusta og inngilding. Skeptísk gagnvart einkavæðingu "
            "og spákaupmennsku á húsnæðismarkaði."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(
            velferd=2, skattar=1, bilar=-2, borgarlina=2, husnaedi=2,
            loftslag=2, skolar=1, eldri=1, atvinnu=-1, lydraedi=1,
            innflytjendur=2, menning=2,
        ),
        "uncertain_axes": [],
        "notes": "Uppfært 2026-05-07 með heimildum frá vinstrid.is. Stefnan er rekstrarlega samfelld; húsnæði er meðhöndlað sem félagslegur réttur.",
        "sources": [
            "https://vinstrid.is/",
        ],
    },
    "B": {
        "list_letter": "B",
        "name": "Framsóknarflokkurinn",
        "short_name": "Framsókn",
        "logo": "assets/logos/b-framsokn.png",
        "color": "#7B6E3B",
        "website": "https://www.framsoknrvk.is/",
        "policy_url": "https://www.framsoknrvk.is/",
        "summary": (
            "Praktísk miðjustjórnun með áherslu á börn, fjölskyldur, eldri borgara, hverfaþjónustu og smurta borgarrekstur. „Reykjavík á grænu ljósi“ er kjarna-frasinn — minna ideologi, meira praktík."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(velferd=1, skattar=0, bilar=1, borgarlina=1, husnaedi=1, loftslag=1, skolar=2, eldri=2, atvinnu=1, lydraedi=1, innflytjendur=1, menning=1),
        "uncertain_axes": [],
        "notes": "Uppfært 2026-05-07 með heimildum frá framsoknrvk.is og umfjöllun RÚV (29. apríl).",
        "sources": [
            "https://www.framsoknrvk.is/",
            "https://www.framsokn.is/sveitarfelog/reykjavik",
            "https://www.ruv.is/frettir/innlent/2026-04-29-framsokn-bodar-reykjavik-a-graenu-ljosi",
        ],
    },
    "C": {
        "list_letter": "C",
        "name": "Viðreisn",
        "short_name": "Viðreisn",
        "logo": "assets/logos/c-vidreisn.png",
        "color": "#F2A93B",
        "website": "https://www.vidreisnreykjavik.is/",
        "policy_url": "https://www.vidreisnreykjavik.is/stefna",
        "summary": (
            "Liberal-praktísk borgarstjórnun: kortershverfi (15-mín-borg), sjálfbærar samgöngur, einföldun stjórnsýslu, frjálslynt inngildingar-viðhorf og modern european city governance."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(velferd=1, skattar=-1, bilar=-1, borgarlina=2, husnaedi=2, loftslag=2, skolar=1, eldri=0, atvinnu=2, lydraedi=1, innflytjendur=2, menning=1),
        "uncertain_axes": [],
        "notes": "Uppfært 2026-05-07 með heimildum frá vidreisnreykjavik.is.",
        "sources": [
            "https://www.vidreisnreykjavik.is/stefna",
            "https://vidreisn.is/reykjavik/",
        ],
    },
    "D": {
        "list_letter": "D",
        "name": "Sjálfstæðisflokkurinn",
        "short_name": "Sjálfstæðisflokkur",
        "logo": "assets/logos/d-sjalfstaedisflokkur.png",
        "color": "#1F4E8C",
        "website": "https://xd.is/sveitarstjornarkosningar/reykjavikurborg/",
        "policy_url": "https://xd.is/sveitarstjornarkosningar/reykjavikurborg/",
        "summary": (
            "Borgaraleg fjárhagsleg stjórnsýsla: aðhald, einkareksturs-vænn rekstur, anti-bureaucracy, áhersla á aðgengi einkabíla og pro-housing-supply með markaðs-driven framework. Innri ágreiningur um Borgarlínu."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(velferd=0, skattar=-2, bilar=2, borgarlina=-1, husnaedi=1, loftslag=0, skolar=1, eldri=1, atvinnu=2, lydraedi=0, innflytjendur=0, menning=-1),
        "uncertain_axes": ['innflytjendur'],
        "notes": "Uppfært 2026-05-07 með heimildum frá xd.is/reykjavikurborg.",
        "sources": [
            "https://xd.is/sveitarstjornarkosningar/reykjavikurborg/",
            "https://xd.is/stefnan/",
        ],
    },
    "F": {
        "list_letter": "F",
        "name": "Flokkur fólksins",
        "short_name": "Flokkur fólksins",
        "logo": "assets/logos/f-flokkur-folksins.png",
        "color": "#E55A2B",
        "website": "https://flokkurfolksins.is/reykjavik/",
        "policy_url": "https://flokkurfolksins.is/reykjavik/aherslumal.html",
        "summary": (
            "Velferðar-populískur framboð: eldri borgarar í forgangi, viðkvæmir hópar, húsnæðisöryggi, „mannlegri“ skipulag (gegn ofurþéttingu), praktísk daglega þjónusta. Anti-bureaucratic en ekki austerity."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(velferd=2, skattar=0, bilar=1, borgarlina=-1, husnaedi=0, loftslag=0, skolar=1, eldri=2, atvinnu=0, lydraedi=1, innflytjendur=0, menning=-1),
        "uncertain_axes": ['loftslag', 'innflytjendur', 'menning'],
        "notes": "Uppfært 2026-05-07 með heimildum frá flokkurfolksins.is/reykjavik.",
        "sources": [
            "https://flokkurfolksins.is/reykjavik/",
            "https://flokkurfolksins.is/reykjavik/aherslumal.html",
            "https://www.ruv.is/frettir/innlent/2026-04-24-flokkur-folksins-kynnir-aherslumalin-i-borginni",
        ],
    },
    "G": {
        "list_letter": "G",
        "name": "Góðan daginn",
        "short_name": "Góðan daginn",
        "logo": "assets/logos/g-godan-daginn.png",
        "color": "#9C8DC4",
        "website": "https://gdf.is/",
        "policy_url": "https://gdf.is/stefnumalin/",
        "summary": (
            "Praktísk borgarrekstur, aðhald og einföld stjórnsýsla. Skólar og fjölskyldur "
            "í forgangi, atvinnulíf og íbúasamráð sem kjarnaprinsíp. Skeptísk gagnvart "
            "dýrum samgönguverkefnum og hugmyndafræðimiðuðu skipulagi."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(
            velferd=1, skattar=-2, bilar=1, borgarlina=-1, husnaedi=-1,
            loftslag=0, skolar=2, eldri=2, atvinnu=2, lydraedi=2,
            innflytjendur=0, menning=0,
        ),
        "uncertain_axes": ["innflytjendur", "menning"],
        "notes": "Uppfært 2026-05-07 með heimildum frá gdf.is/stefnumalin/. Áður var allt merkt óvíst — nú er stærsti hluti ása staðfestur. Innflytjenda- og menningar-ásar eru þó enn lágvissir.",
        "sources": [
            "https://gdf.is/stefnumalin/",
        ],
    },
    "J": {
        "list_letter": "J",
        "name": "Sósíalistaflokkur Íslands",
        "short_name": "Sósíalistar",
        "logo": "assets/logos/j-sosialistar.png",
        "color": "#B22222",
        "website": "https://www.sosialistaflokkurinn.is/",
        "policy_url": "https://www.sosialistaflokkurinn.is/stefna",
        "summary": (
            "Demókratísk-sósíalísk munisipalismi: Reykjavík Construction Company, almenningshúsnæði, anti-spákaupmennska, sterkur opinber rekstur, þátttöku-lýðræði og jöfn aðgengi viðkvæmra hópa."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(velferd=2, skattar=2, bilar=-2, borgarlina=2, husnaedi=2, loftslag=1, skolar=2, eldri=2, atvinnu=-2, lydraedi=2, innflytjendur=2, menning=2),
        "uncertain_axes": [],
        "notes": "Uppfært 2026-05-07 með heimildum frá sosialistaflokkurinn.is/stefna og borgar-stefnuskrá 2026.",
        "sources": [
            "https://www.sosialistaflokkurinn.is/stefna",
            "https://www.sosialistaflokkurinn.is/media-kit/stefna/sosialistar-stefnuskra-rvk-2026.pdf",
        ],
    },
    "M": {
        "list_letter": "M",
        "name": "Miðflokkurinn",
        "short_name": "Miðflokkurinn",
        "logo": "assets/logos/m-midflokkurinn.png",
        "color": "#16365C",
        "website": "https://midflokkurinn.is/reykjavik",
        "policy_url": "https://midflokkurinn.is/reykjavik",
        "summary": (
            "Úthverfa-pragmatísk anti-urbanism: skýr Borgarlínu-andstaða, pro-Sundabraut, pro-bíla-aðgengi, anti-vegtollar/km-skattar, pro-housing-supply með úthverfa-stækkunar logík (anti-density)."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(velferd=0, skattar=-2, bilar=2, borgarlina=-2, husnaedi=-1, loftslag=-1, skolar=0, eldri=0, atvinnu=1, lydraedi=0, innflytjendur=-1, menning=-1),
        "uncertain_axes": ['innflytjendur'],
        "notes": "Uppfært 2026-05-07 með heimildum frá midflokkurinn.is/reykjavik og samgöngu-stefnu.",
        "sources": [
            "https://midflokkurinn.is/reykjavik",
            "https://midflokkurinn.is/stefna/samgongumal-sundabraut-og-borgarlina",
            "https://midflokkurinn.is/midflokkurinn-hefur-lausnir-a-husnaedismarkadi",
        ],
    },
    "P": {
        "list_letter": "P",
        "name": "Píratar",
        "short_name": "Píratar",
        "logo": "assets/logos/p-piratar.png",
        "color": "#3F2E56",
        "website": "https://piratar.is/bestumborgina2026",
        "policy_url": "https://piratar.is/bestumborgina2026",
        "summary": (
            "Demókratísk-progressíf gagnsæis-umbót: stafræn borgarþjónusta, beint lýðræði, mannréttindi (LGBTQ+, minorities), sjálfbærar samgöngur, loftslags-conscious skipulag — process before ideology."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(velferd=1, skattar=0, bilar=-2, borgarlina=2, husnaedi=1, loftslag=2, skolar=1, eldri=0, atvinnu=1, lydraedi=2, innflytjendur=2, menning=2),
        "uncertain_axes": ['skattar'],
        "notes": "Uppfært 2026-05-07 með heimildum frá piratar.is/bestumborgina2026 og piratar.is/stefna.",
        "sources": [
            "https://piratar.is/bestumborgina2026",
            "https://piratar.is/stefna",
        ],
    },
    "R": {
        "list_letter": "R",
        "name": "Okkar borg",
        "short_name": "Okkar borg",
        "logo": "assets/logos/r-okkar-borg.png",
        "color": "#5B8DBE",
        "website": "https://www.okkarborg.is/",
        "policy_url": "https://www.okkarborg.is/",
        "summary": (
            "Andstaða við Borgarlínu og þéttingu byggðar. Áhersla á aðgengi einkabíla, "
            "kjarnaþjónustu, einföldun stjórnsýslu og úthverfa-vænleg fjölskylduskipulag. "
            "Skarpari afstaða gagnvart innflytjendamálum en flest önnur framboð í Reykjavík."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(
            velferd=0, skattar=-2, bilar=2, borgarlina=-2, husnaedi=-2,
            loftslag=-1, skolar=1, eldri=1, atvinnu=1, lydraedi=1,
            innflytjendur=-2, menning=-1,
        ),
        "uncertain_axes": [],
        "notes": "Uppfært 2026-05-07 með heimildum frá okkarborg.is. Áður var allt merkt óvíst — nú er stærsti hluti ása staðfestur. Stefnan er sterkari og skarpari en upphafsmat benti til.",
        "sources": [
            "https://www.okkarborg.is/",
        ],
    },
    "S": {
        "list_letter": "S",
        "name": "Samfylkingin",
        "short_name": "Samfylkingin",
        "logo": "assets/logos/s-samfylkingin.png",
        "color": "#C8102E",
        "website": "https://xs.is/reykjavik",
        "policy_url": "https://xs.is/reykjavik",
        "summary": (
            "Norræn jafnaðar-borgarstjórnun: húsnæðis-uppbygging, þétt þjónustu-tengd byggð, Borgarlína, sterk velferð og skólar, jafnræðis- og inngildingar-áhersla, loftslag samþætt í skipulagi — institutional og managerial."
        ),
        "tagline": DEFAULT_TAGLINE,
        "scores": _scores(velferd=2, skattar=1, bilar=0, borgarlina=2, husnaedi=2, loftslag=2, skolar=2, eldri=1, atvinnu=0, lydraedi=1, innflytjendur=2, menning=2),
        "uncertain_axes": [],
        "notes": "Uppfært 2026-05-07 með heimildum frá xs.is/reykjavik.",
        "sources": [
            "https://xs.is/reykjavik",
            "https://xs.is/",
        ],
    },
}


# Röð á kjörseðli (stafrófsröð listabókstafs).
PARTY_ORDER = ["A", "B", "C", "D", "F", "G", "J", "M", "P", "R", "S"]
