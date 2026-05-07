# Borgarstjórnar­kompás Reykjavíkur 2026

Óháð Streamlit-tól sem hjálpar fjölskyldum að bera saman borgarstjórnar­framboð
Reykjavíkur 2026 við sínar eigin áherslur.

> ⚠️ **Þetta er ekki kosningaráðgjöf.** Tólið mælir ekki með neinu framboði.
> Það sýnir aðeins hvaða framboð liggja næst þínum svörum út frá opinberum
> stefnumálum eins og við höfum kortlagt þau. **Lestu stefnuskrár framboðanna
> sjálf/ur áður en þú kýst.**

---

## Hvað er innifalið

- **25 stefnuspurningar** á 5 punkta Likert-kvarða (mjög ósammála → mjög sammála).
- **12 stefnuásar** sem spurningarnar feeda inn í.
- **20-axis stefnu-fylki** (`policy_matrix.py`) — dýpri rekstrarlegur samanburður.
- **Persónugerð (vibe-próf)** sem hefur **engin** áhrif á flokksamsvörun — bara til gamans.
- **Glundroðagildi** — algjörlega merkingarlaus tala til skemmtunar.
- **Niðurstöður**: topp 3 framboð, prósenta, ásar þar sem er mest samstaða og ósamstaða.
- **Radarrit**: þú á móti efstu þremur á öllum 12 ásum (Plotly).
- **Samanburðartafla**: öll framboð á öllum lykilásum.
- **Stefnu-fylki**: 20-ása djúprýni með vissustigi, mótsögnum og heimildum.
- **Aðferðafræðisíða**: gagnsætt útreikningskerfi.
- **Deilanleg niðurstaða**: slóð með topp 3 + tilbúinn texti fyrir samfélagsmiðla.
- **Ítarleg DATA_REVIEW.md** og `party_notes.md` fyrir ritstjórnar-yfirferð.

---

## Setja upp og keyra

```bash
cd ~/Development/borgarstjornarkompas
python -m venv .venv
source .venv/bin/activate    # eða .venv\Scripts\activate á Windows
pip install -r requirements.txt
streamlit run app.py
```

Streamlit opnar tólið á `http://localhost:8501`.

---

## Skráarskipan

```
borgarstjornarkompas/
├── app.py               # Streamlit forritið — UI, síðustýring, deiling
├── parties.py           # 11 framboð: 12-ása stigatöflur, lógóslóðir, vefslóðir
├── policy_matrix.py     # 20-ása rekstrarlegt fylki + greiningarföll
├── questions.py         # 25 stefnu, 8 persónuleika, 5 glundroða spurningar
├── scoring.py           # Útreikningur á samsvörun (gegnsæ, einföld vegalengd)
├── chaos.py             # Persónugerðir og glundroðagildi (engin áhrif á samsvörun)
├── requirements.txt
├── README.md            # þetta skjal
├── DATA_REVIEW.md       # listi yfir ÖLL gögn sem þarf að staðfesta
├── party_notes.md       # ritstjórnar-yfirlit á hvert framboð
└── assets/
    └── logos/
        ├── README.md    # útskýrir hvað vantar
        └── (vantar)     # PNG-skrár fyrir hvert framboð (sjá DATA_REVIEW)
```

---

## Hvernig þú uppfærir gögnin

### Stigatöflur framboða
Breyttu beint í `parties.py` (12-ása einföldun fyrir spurningalistann) og
`policy_matrix.py` (20-ása rekstrarlegt fylki).

### Heimildir
Bæta heimildum við `policy_matrix.py` í dictinu `POLICY_SOURCES`:
```python
POLICY_SOURCES[("S", "dense_housing")] = ["https://samfylkingin.is/stefna/..."]
```

### Vissustig
Stilltu `PARTY_CERTAINTY` í `policy_matrix.py`. `overall` er heildarmat;
`per_axis` er valkvæð fín-stilling.

### Slagorð
`tagline` reiturinn í `parties.py`. **Aðeins staðfest, raunveruleg slagorð**
mega fara þangað — annars skal lesa skýringartextann í kóðanum áður en breytt er.

### Lógó
Set PNG-skrár í `assets/logos/` með nöfnum eins og `a-vinstrid.png`. Tólið
fellur sjálfkrafa aftur í stafa-kúlu ef skrá vantar.

---

## Hvernig útreikningurinn virkar (stutt útgáfa)

1. Notandi svarar spurningu á 5 punkta kvarða (-2..+2).
2. Hver spurning tengist 1+ stefnuásum með skilgreindri þyngd.
3. „Afstaða framboðs á spurningu“ = vegið meðaltal stiga þess á tengdum ásum.
4. Vegalengd = |svar − afstaða| ; samsvörun = `1 − vegalengd / 4`.
5. Heildarsamsvörun = meðaltal yfir svaraðar spurningar.

Sjá nákvæmari lýsingu á aðferðafræðisíðu tólsins eða í `scoring.py`.

---

## Hlutleysi

- Tólið mælir ekki með neinu framboði.
- Stigagjöf á framboðum er handvirk — sjá DATA_REVIEW.md fyrir hvað þarf að staðfesta.
- Persónuleika- og glundroðaspurningar hafa **engin** áhrif á samsvörun.
- Litir og lógó eru hófleg og ætluð sem auðkenni, ekki skoðanaleg yfirlýsing.
- Heimildir eru sýndar á aðferðafræðisíðu og sem tenglar á stefnu-fylki.

---

## Næstu skref áður en þetta er birt opinberlega

1. Klára DATA_REVIEW.md — staðfesta öll stig, lógó, vefslóðir og slagorð.
2. Bæta opinberum heimildum (URL) við hvert stig sem máli skiptir.
3. Bæta lógóum í `assets/logos/`.
4. Yfirlesa `party_notes.md` — það er ritstjórnar-skissur, ekki sannleikur.
5. Prófa með nokkrum úr fjölskyldunni og lagfæra orðalag.
6. Hýsa á Streamlit Cloud eða annars staðar svo deilanlegar slóðir virki.
