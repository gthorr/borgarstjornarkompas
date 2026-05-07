# Data Review — verkefnalisti fyrir gagnayfirferð

> **Meginreglur.** Ekkert hér er endanlegt. Allt sem skráð er í `parties.py`,
> `policy_matrix.py` og `party_notes.md` er **bráðabirgða** og verður að bera
> saman við opinberar borgarstjórnarstefnuskrár framboðanna 2026 áður en
> tólið er birt opinberlega.

Þessi skrá er verkefnalisti. Þegar liður er staðfestur, hakaðu hann af
( `[x]` ) með stuttri tilvísun í heimildina.

---

## 1. Lógó

Vantar PNG-skrár í `assets/logos/`. Tólið fellur núna aftur í stafa-kúlu ef
skrá er ekki til staðar. Markmið: staðfesta opinber lógó frá hverjum
framboði og setja inn ferská PNG (helst >= 256px breidd).

- [ ] `a-vinstrid.png` — Vinstrihreyfingin – grænt framboð
- [ ] `b-framsokn.png` — Framsóknarflokkurinn
- [ ] `c-vidreisn.png` — Viðreisn
- [ ] `d-sjalfstaedisflokkur.png` — Sjálfstæðisflokkurinn
- [ ] `f-flokkur-folksins.png` — Flokkur fólksins
- [ ] `g-godan-daginn.png` — Góðan daginn (ekki staðfest að lógó sé til)
- [ ] `j-sosialistar.png` — Sósíalistaflokkurinn
- [ ] `m-midflokkurinn.png` — Miðflokkurinn
- [ ] `p-piratar.png` — Píratar
- [ ] `r-okkar-borg.png` — Okkar borg (ekki staðfest að lógó sé til)
- [ ] `s-samfylkingin.png` — Samfylkingin

**Heimildaröflun:** Notið helst lógó sem framboðin sjálf birta opinberlega
(t.d. á forsíðu vefs eða pressa-page). Forðist mynd­sviðsmyndir frá
fréttamiðlum (höfundarréttur óvíst).

---

## 2. Vefslóðir og stefnuskrár

Reitur `policy_url` í `parties.py` er enn í flestum tilfellum aðalsíða
landsflokks, ekki sérstök slóð á borgarstjórnarstefnuskrá 2026.

- [ ] A — Vinstrið: borgarstjórnar­stefnuskrá 2026 ekki staðfest
- [ ] B — Framsókn: borgarstjórnar­stefnuskrá 2026 ekki staðfest
- [ ] C — Viðreisn: borgarstjórnar­stefnuskrá 2026 ekki staðfest
- [ ] D — Sjálfstæðisflokkurinn: borgarstjórnar­stefnuskrá 2026 ekki staðfest
- [ ] F — Flokkur fólksins: borgarstjórnar­stefnuskrá 2026 ekki staðfest
- [ ] G — Góðan daginn: vefslóð **ekki skráð** (þarf að finna)
- [ ] J — Sósíalistar: borgarstjórnar­stefnuskrá 2026 ekki staðfest
- [ ] M — Miðflokkurinn: borgarstjórnar­stefnuskrá 2026 ekki staðfest
- [ ] P — Píratar: borgarstjórnar­stefnuskrá 2026 ekki staðfest
- [ ] R — Okkar borg: vefslóð **ekki skráð** (þarf að finna)
- [ ] S — Samfylkingin: borgarstjórnar­stefnuskrá 2026 ekki staðfest

---

## 3. Slagorð (`tagline`)

Allir reitir innihalda núna sjálfgefið `DEFAULT_TAGLINE`:

> „Engin staðfest hallærisleg slaglína fundin — bættu við handvirkt.“

**Mikilvægt.** Aðeins **staðfest, raunveruleg slagorð** mega fara hér inn.
Að búa til skáldað eða illgjarnt slagorð er bæði ósanngjarnt og getur
talist meiðyrði. Sjá athugasemd í `parties.py`.

- [ ] A — Vinstrið
- [ ] B — Framsókn
- [ ] C — Viðreisn
- [ ] D — Sjálfstæðisflokkurinn
- [ ] F — Flokkur fólksins
- [ ] G — Góðan daginn
- [ ] J — Sósíalistar
- [ ] M — Miðflokkurinn
- [ ] P — Píratar
- [ ] R — Okkar borg
- [ ] S — Samfylkingin

---

## 4. 12-ása stigatöflur (`parties.py` → `scores`)

Tólið notar 12-ása einföldun fyrir spurningalistann. **Uppfært 2026-05-07** með
heimildum fyrir A, G og R. Aðrir flokkar bíða enn yfirferðar.

Öll 11 framboð voru **heimildaröflun-uppfærð 2026-05-07**. Eftir er enn að bera
saman við endanlegar stefnuskrár borgarstjórnarframboða 2026 þegar þær eru
birtar opinberlega.

| Listi | Heimild | Eftir | Sérlega óvissir ásar (12-axis `uncertain_axes`) |
|-------|---------|-------|--------------------------------------------------|
| A | ✅ vinstrid.is | nákvæmari útfærsla á atvinnumálum | — |
| B | ✅ framsoknrvk.is + RÚV | nákvæmari útfærsla á borgarlinu/loftslagi | — |
| C | ✅ vidreisnreykjavik.is | endurskoðun bílar / parking-priority | — |
| D | ✅ xd.is/reykjavikurborg | innri ágreiningur um Borgarlínu | innflytjendur |
| F | ✅ flokkurfolksins.is/reykjavik | loftslag / inngilding sjónarmið | loftslag, innflytjendur, menning |
| G | ✅ gdf.is/stefnumalin | inngilding / menning | innflytjendur, menning |
| J | ✅ sosialistaflokkurinn.is/stefna | nákvæmari útfærsla á efficiency-mörkum | — |
| M | ✅ midflokkurinn.is/reykjavik | innflytjenda-stefna á borgarstigi | innflytjendur |
| P | ✅ piratar.is/bestumborgina2026 | atvinnu- og fjárlagastefna | skattar |
| R | ✅ okkarborg.is | menning / culture-investment | — |
| S | ✅ xs.is/reykjavik | nákvæm fjármögnunar-skil | — |

---

## 5. 20-ása stefnu-fylki (`policy_matrix.py`)

Sama meginregla: bráðabirgða útgangspunktur frá notanda tólsins. Allir lyklar
þurfa að bera saman við opinber gögn. Sjá `policy_matrix.py` fyrir alla 220
stigafærslur.

**Lykilatriði sem á að skoða fyrst:**
- [ ] Sannreyna allar tölur fyrir „Borgarlína support“ (öflug pólariseringsás)
- [ ] Sannreyna „Lower taxes/fees“ tölur (skarp aðgreining)
- [ ] Sannreyna „Public housing“ tölur
- [ ] Sannreyna „Direct democracy / referendums“
- [ ] Endurskoða allar `G` (Góðan daginn) tölur — núna allar 0 með low-vissu
- [ ] Endurskoða allar `R` (Okkar borg) tölur — núna allar 0 með low-vissu

**Mikilvægt:** Þegar þú bætir við vísbendingu, skráðu líka heimild í
`POLICY_SOURCES[(party, axis)]` í sömu skrá.

---

## 6. Vissustig (`PARTY_CERTAINTY`) — uppfært 2026-05-07

Hvert framboð er með `overall` vissustig + per-axis stillingar. `evidence_score`
er reiknað sem vegið meðaltal yfir 20 ása (high=1.0, medium=0.55, low=0.15).

| Listi | Overall | Evidence score | Heimildir |
|-------|---------|----------------|-----------|
| A | high   | 0.96 | vinstrid.is |
| B | medium | 0.62 | framsoknrvk.is + RÚV (29. apríl) |
| C | high   | 0.78 | vidreisnreykjavik.is |
| D | high   | 0.67 | xd.is/sveitarstjornarkosningar/reykjavikurborg |
| F | medium | 0.56 | flokkurfolksins.is/reykjavik/aherslumal.html |
| G | medium | 0.61 | gdf.is/stefnumalin |
| J | high   | 0.93 | sosialistaflokkurinn.is/stefna + stefnuskra-rvk-2026.pdf |
| M | high   | 0.67 | midflokkurinn.is/reykjavik + samgöngustefna |
| P | high   | 0.73 | piratar.is/bestumborgina2026 |
| R | medium | 0.78 | okkarborg.is |
| S | high   | 0.84 | xs.is/reykjavik |

**Mikilvægt:** „Lág vissa á ás“ og „skýr hófsöm afstaða“ eru aðgreind í
tólinu — sjá `DETAIL_OVERRIDES` í `policy_matrix.py`.

- [ ] Endurskoða vissustig á B og F (lágstig).
- [ ] Bæta heimildum fyrir aðrar flokka (C, D, F, J, M, P, S).
- [ ] Færa lágvissu-ása G (innflytjendur, menning) upp þegar betri heimildir liggja fyrir.

---

## 7. `party_notes.md` (ritstjórnar-skissur)

Þetta er gagnaskrá með stuttum lýsingum, gamansömum staðalímyndum og
„most distinctive policy“ á hverju framboði. Allt þetta þarf yfirlestur.

- [ ] Yfirlesa allt — leiðrétta rangfærslur
- [ ] Athuga tóninn — ekkert ósanngjarnt eða stinandi
- [ ] Sleppa „stereotypical voter“ köflum ef þér finnst þeir ekki passa
- [ ] Bæta við heimildum þar sem fullyrðingar eru gerðar

---

## 8. Spurningarnar 25 (`questions.py`)

- [ ] Lestu yfir orðalag — ætti að vera hlutlaust og auðskilið.
- [ ] Athugaðu þyngdir (`axes`) — endurspegla þær raunverulega það sem
  spurningin spyr um?
- [ ] Tilraunalista með fjölskyldumeðlim, athuga hvort einhver spurning er
  ruglandi.

---

## 9. Persónuleika- og glundroðaspurningar

Engar staðreyndir, en þarf ritstjórnar-yfirlestur:

- [ ] Allar `PERSONALITY_QUESTIONS` — er einhver of stingandi?
- [ ] Allar `CHAOS_QUESTIONS` — er einhver svæsin staðalímynd?
- [ ] `ARCHETYPES` í `chaos.py` — engin titlun á að móðga hóp eða einstakling.

---

## 10. Hýsing og deilanleiki

- [ ] Setja upp Streamlit Cloud (eða aðra hýsingu) svo `?r=...` slóðir virki.
- [ ] Prófa að deila slóð milli tækja og tryggja að niðurstaða birtist rétt.
- [ ] Bæta við OpenGraph-myndum og titli ef Streamlit hýsing leyfir.
- [ ] Athuga afköst — síðan á að vera mobile-vænleg.

---

## 11. Áður en birt er opinberlega — lokaprófunarlisti

- [ ] Allar tölur staðfestar gegn opinberum heimildum
- [ ] Allar heimildir skráðar í `POLICY_SOURCES`
- [ ] Vissustig endurskoðuð
- [ ] Lógó komin í `assets/logos/`
- [ ] Slagorð aðeins staðfest, raunveruleg
- [ ] `party_notes.md` ritstjórnar-yfirlesið
- [ ] Prófað á að minnsta kosti 3 mismunandi tækjum
- [ ] Hlutleysisskýring sýnileg á öllum síðum
- [ ] Engin ráðlegging um hvern eigi að kjósa á neinni síðu
