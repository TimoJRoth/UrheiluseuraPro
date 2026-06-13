# Lähdekartoitus – koko Suomi

UrheiluseuraPro:n **kattava tietolähdeinventaario**. Tavoite on rakentaa Suomen laajin urheiluseurarekisteri yhdistämällä useita tietolähteitä yhdeksi tietokannaksi.

> **Tila:** Suunnittelu- ja kartoitusvaihe. Scrapereita ei ole toteutettu. robots.txt-sarakkeet on merkitty *Tarkistettava* – ne varmistetaan ennen ingestointia.

## Sisällysluettelo

1. [Kenttälegenda](#kenttälegenda)
2. [Yhteenveto](#yhteenveto)
3. [Valtakunnalliset lajiliitot](#1-valtakunnalliset-lajiliitot)
4. [Liikunnan aluejärjestöt (liikuntavälineet)](#2-liikunnan-aluejärjestöt-liikuntavälineet)
5. [Olympiakomitea ja kattojärjestöt](#3-olympiakomitea-ja-kattojärjestöt)
6. [Suomisport](#4-suomisport)
7. [Kuntien seurarekisterit](#5-kuntien-liikuntapalveluiden-seurarekisterit)
8. [Avustusrekisterit](#6-avustusrekisterit)
9. [Liikuntatilojen käyttäjärekisterit](#7-liikuntatilojen-käyttäjärekisterit)
10. [Varausjärjestelmät](#8-varausjärjestelmät)
11. [Muut julkiset seurahakemistot](#9-muut-julkiset-seurahakemistot)
12. [Päällekkäisyysanalyysi](#päällekkäisyysanalyysi)
13. [Optimaalinen keruujärjestys](#optimaalinen-keruujärjestys)
14. [Seuraavat askeleet](#seuraavat-askeleet)

---

## Kenttälegenda

| Sarake | Selitys |
|--------|---------|
| **K/O/E** | Kyllä / Osittain / Ei – löytyykö kenttä lähteestä |
| **Muoto** | HTML, API, PDF, Excel (yksi tai useampi) |
| **Vaikeus** | 1 (helppo) – 5 (hyvin vaikea) scraperin toteutus |
| **Prioriteetti** | P1 (kriittinen) – P4 (myöhemmin / epävarma hyöty) |
| **robots.txt** | Sallittu / Rajoitettu / Tarkistettava / Ei saatavilla |

---

## Yhteenveto

| Ryhmä | Lähteitä | Arvioitu seuroja (brutto) | Uniikkeja (netto-arvio) | P1-lähteitä |
|-------|----------|---------------------------|-------------------------|-------------|
| Lajiliitot | 68 | ~12 000–15 000 | ~8 000 (lajipäällekkäisyys) | 4 |
| Aluejärjestöt | 19 | ~4 000–6 000 | ~3 500 | 3 |
| Olympiakomitea / kattojärjestöt | 5 | ~100–150 (jäsenliitot, ei seuroja) | – | 1 |
| Suomisport | 3 | ~9 000–11 000 | ~9 000 | 2 |
| Kuntien seurarekisterit | 35+ | ~3 000–5 000 | ~2 500 | 5 |
| Avustusrekisterit | 12 | ~2 000–4 000 | ~1 500 (täydentää) | 2 |
| Liikuntatilojen käyttäjät | 10 | ~1 500–3 000 | ~1 000 (täydentää) | 2 |
| Varausjärjestelmät | 8 | ~2 000–4 000 | ~1 500 (täydentää) | 1 |
| Muut hakemistot | 10 | ~15 000+ (yhdistykset) | ~3 000 (suodatus) | 2 |
| **Yhteensä (brutto)** | **~170** | **~25 000+** | **~12 000–15 000 uniikkia seuraa** | **~22** |

**Tavoitetietokanta:** 12 000–15 000 deduplikoitua urheiluseuraa, joista 80 %+:lla nimi + laji + kunta, 50 %+:lla yhteystiedot.

---

## 1. Valtakunnalliset lajiliitot

Suomessa on noin **70 valtakunnallista lajiliittoa** (Olympiakomitea listaa ~90 jäsenjärjestöä, sisältäen myös alajärjestöjä). Alla kaikki merkittävät lajiliitot, joilla on seurarekisteri tai seurahaku.

**Yhteinen kenttäkuvio:** Useimmat tarjoavat seuran nimen ja lajin; kunta, osoite ja yhteystiedot vaihtelevat. Monilla lajiliitoilla data on Laji.fi-palvelussa.

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| **Laji.fi (aggregaattori)** | https://www.laji.fi | Koko Suomi | 8 000–10 000 | K | K | O | E | O | E | E | E | Tarkistettava | HTML | 2 | **P1** | Usean liiton yhteinen haku; paras lähtöpiste |
| Suomen Palloliitto | https://www.palloliitto.fi/seurat | Koko Suomi | ~1 200 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P1** | Jalkapallo, futsal |
| Suomen Jääkiekkoliitto | https://www.finhockey.fi | Koko Suomi | ~400 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P1** | Myös Tulospalvelu.fi |
| Suomen Salibandyliitto | https://www.fisb.fi | Koko Suomi | ~400 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Suomen Pesäpalloliitto | https://www.pesis.fi | Koko Suomi | ~350 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Vahva aluejako |
| Suomen Koripalloliitto | https://www.basket.fi | Koko Suomi | ~300 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Suomen Lentopalloliitto | https://www.svl.fi | Koko Suomi | ~250 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Suomen Uimariliitto | https://www.uima.fi | Koko Suomi | ~200 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Suomen Voimisteluliitto | https://www.voimistelu.fi | Koko Suomi | ~300 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Voimistelu, cheerleading |
| Suomen Urheiluliitto | https://www.athletics.fi | Koko Suomi | ~200 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Yleisurheilu |
| Suomen Hiihdon liitto | https://www.hiihtoliitto.fi | Koko Suomi | ~350 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Mäki, maa, yhdistetty |
| Suomen Ampumahiihtoliitto | https://www.biathlon.fi | Koko Suomi | ~80 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Suunnistusliitto | https://www.suunnistusliitto.fi | Koko Suomi | ~200 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Sotkanet.fi-tulospalvelu |
| Suomen Tennisliitto | https://www.tennis.fi | Koko Suomi | ~150 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Purjehdusliitto | https://www.purjehdusliitto.fi | Koko Suomi | ~150 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Golfliitto | https://www.golf.fi | Koko Suomi | ~150 | K | K | O | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Ratsastusliitto | https://www.ratsastus.fi | Koko Suomi | ~150 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Pyöräilyliitto | https://www.pyoraily.fi | Koko Suomi | ~100 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Kamppailulajiliitto | https://www.kamppailulajiliitto.fi | Koko Suomi | ~200 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Kattojärjestö |
| Suomen Judo liitto | https://www.judo.fi | Koko Suomi | ~80 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Karate liitto | https://www.karate.fi | Koko Suomi | ~60 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Taekwondoliitto | https://www.taekwondo.fi | Koko Suomi | ~50 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Aikidoliitto | https://www.aikido.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Painiliitto | https://www.painiliitto.fi | Koko Suomi | ~50 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Nyrkkeilyliitto | https://www.nyrkkeily.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Voimailuliitto | https://www.voimailuliitto.fi | Koko Suomi | ~100 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Nostolajit |
| Suomen Käsipalloliitto | https://www.kasipallo.fi | Koko Suomi | ~80 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Sulkapalloliitto | https://www.sulkapallo.fi | Koko Suomi | ~60 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Squashliitto | https://www.squash.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Rugbyliitto | https://www.rugby.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Krikettiliitto | https://www.cricket.fi | Koko Suomi | ~15 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | Pieni laji |
| Suomen Amerikkalaisen jalkapallon liitto | https://www.americanfootball.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Beacvolley liitto | https://www.beachvolley.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Rantalentopalloliitto | https://www.rantalentopallo.fi | Koko Suomi | ~25 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Frisbeegolfliitto | https://www.frisbeegolfliitto.fi | Koko Suomi | ~200 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Suuri seuramäärä |
| Suomen Kiipeilyliitto | https://www.kiipeily.fi | Koko Suomi | ~50 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Luisteluliitto | https://www.figureskating.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Curlingliitto | https://www.curling.fi | Koko Suomi | ~25 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Keilailuliitto | https://www.keilailu.fi | Koko Suomi | ~80 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Biljardiliitto | https://www.biljardi.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Triathlonliitto | https://www.triathlon.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Moottoriurheiluliitto | https://www.moottoriurheiluliitto.fi | Koko Suomi | ~100 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 3 | **P3** | Monipuolinen |
| Suomen Purjehtijaliitto (SPS) | https://www.purjehtijaliitto.fi | Koko Suomi | ~80 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Purjehdus, melonta |
| Suomen Melontaliitto | https://www.melonta.fi | Koko Suomi | ~50 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Umpimelontaliitto | https://www.kanootti.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Soutuliitto | https://www.soutu.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Jousiammunta liitto | https://www.jousiammunta.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Ampumaurheiluliitto | https://www.ampumaurheiluliitto.fi | Koko Suomi | ~60 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Maastohiihto (Hiihtoliitto ala) | https://www.hiihtoliitto.fi | Koko Suomi | ~200 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Päällekkäin hiihdon kanssa |
| Suomen Lasketteluliitto | https://www.slalom.fi | Koko Suomi | ~80 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Alppihiihto |
| Suomen Freestyle-hiihto | https://www.freestyle.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Snowboarding | https://www.snowboarding.fi | Koko Suomi | ~20 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Cheerleadingliitto | https://www.cheerleading.fi | Koko Suomi | ~50 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Tanssiliitto | https://www.tanssiliitto.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Kilpatanssi |
| Suomen Voimisteluliitto – trampoliini | https://www.trampoliini.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Pöytätennisliitto | https://www.poytatenis.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Softball-liitto | https://www.softball.fi | Koko Suomi | ~20 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Baseboll-liitto | https://www.baseball.fi | Koko Suomi | ~15 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Kendo liitto | https://www.kendo.fi | Koko Suomi | ~15 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Muaythai liitto | https://www.muaythai.fi | Koko Suomi | ~20 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Savate liitto | https://www.savate.fi | Koko Suomi | ~10 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Floorball (F-liiga seurat) | https://www.fisb.fi | Koko Suomi | – | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Sama kuin salibandy |
| Suomen E-sports liitto | https://www.suomen-esports.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 3 | **P4** | Rajallinen perinteinen seura-käsite |
| Suomen Padel liitto | https://www.padel.fi | Koko Suomi | ~80 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Nopeasti kasvava |
| Suomen Krokettiliitto | https://www.kroketti.fi | Koko Suomi | ~10 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Ringetteliitto | https://www.ringette.fi | Koko Suomi | ~40 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Jääpalloliitto | https://www.jaapalloliitto.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Suomen Rollerskoliitto | https://www.rollerskoliitto.fi | Koko Suomi | ~15 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Rullalautaliitto | https://www.rullalautaliitto.fi | Koko Suomi | ~10 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Parkour liitto | https://www.parkour.fi | Koko Suomi | ~15 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Ketteran liitto | https://www.kettera.fi | Koko Suomi | ~20 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | |
| Suomen Veteraaniurheiluliitto | https://www.svu.fi | Koko Suomi | ~50 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P4** | Masters-urheilu |
| Suomen Paraurheiluliitto | https://www.paraurheilu.fi | Koko Suomi | ~30 | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Erityisliikunta |

---

## 2. Liikunnan aluejärjestöt (liikuntavälineet)

Suomessa on **19 alueellista liikuntavälinettä**, jotka tukevat paikallista seuratoimintaa. Ne ylläpitävät alueellisia seura- ja järjestölistauksia, tarjoavat neuvontaa ja jakavat usein avustuksia.

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| Etelä-Suomen Liikunta ja Urheilu (ELSA) | https://www.elsa.fi | Uusimaa, Kymenlaakso, Etelä-Karjala | 800–1 200 | K | O | O | E | O | O | O | O | Tarkistettava | HTML, PDF | 2 | **P1** | Suurin volyymi |
| Liikuntaväline Pirkanmaa | https://www.liikuntaväline.fi | Pirkanmaa | 300–400 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P1** | Hyvä pilottialue |
| Länsi-Uudenmaan Liikunta | https://www.lansiuudenmaanliikunta.fi | Länsi-Uusimaa | 200–300 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P1** | Espoo, Kauniainen, Kirkkonummi |
| Itä-Uudenmaan Liikunta | https://www.itauudenmaanliikunta.fi | Itä-Uusimaa | 150–200 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Porvoo, Loviisa |
| Varsinais-Suomen Liikunta ja Urheilu (VALSU) | https://www.valsu.fi | Varsinais-Suomi | 250–350 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Turku, Salo |
| Pohjois-Pohjanmaan Liikunta | https://www.pohjois-pohjanmaanliikunta.fi | Pohjois-Pohjanmaa | 200–300 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Oulu |
| Keski-Suomen Liikunta | https://www.keski-suomenliikunta.fi | Keski-Suomi | 200–300 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Jyväskylä |
| Pohjois-Savon Liikunta | https://www.pohjois-savonliikunta.fi | Pohjois-Savo | 150–200 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Kuopio |
| Pohjois-Karjalan Liikunta | https://www.pohjois-karjalanliikunta.fi | Pohjois-Karjala | 150–200 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Joensuu |
| Etelä-Pohjanmaan Liikunta | https://www.epl.fi | Etelä-Pohjanmaa | 150–200 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Seinäjoki |
| Satakunnan Liikunta ja Urheilu | https://www.slsu.fi | Satakunta | 150–200 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Pori |
| Pohjanmaan Liikunta | https://www.pohjanmaanliikunta.fi | Pohjanmaa | 150–200 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Vaasa |
| Kanta-Hämeen Liikunta | https://www.kanta-hameenliikunta.fi | Kanta-Häme | 120–180 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | Hämeenlinna |
| Kymenlaakson Liikunta | https://www.kymenlaaksonliikunta.fi | Kymenlaakso | 100–150 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Kouvola (osin ELSA) |
| Etelä-Karjalan Liikuntaväline | https://www.etelakarjalanliikuntaväline.fi | Etelä-Karjala | 100–150 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Lappeenranta |
| Etelä-Savon Liikuntaväline | https://www.etelasavonliikuntaväline.fi | Etelä-Savo | 100–150 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Mikkeli |
| Keski-Pohjanmaan Liikunta | https://www.keski-pohjanmaanliikunta.fi | Keski-Pohjanmaa | 80–120 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Kokkola |
| Kainuun Liikunta ja Urheilu | https://www.kainuunliikunta.fi | Kainuu | 80–120 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Kajaani |
| Lapin Liikunta | https://www.lapinliikunta.fi | Lappi | 150–200 | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Rovaniemi, laaja alue |

---

## 3. Olympiakomitea ja kattojärjestöt

Nämä eivät suoraan listaa kaikkia seuroja, mutta tarjoavat **jäsenjärjestöverkoston** ja valtakunnallisen näkymän.

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| Suomen Olympiakomitea – jäsenjärjestöt | https://www.olympiakomitea.fi | Koko Suomi | ~90 liittoa (ei seuroja) | K | K | E | E | O | O | E | O | Tarkistettava | HTML | 1 | **P1** | Master-lista lajiliitoista; ei seuratason dataa |
| Suomen Paralympiakomitea | https://www.paralympia.fi | Koko Suomi | ~20 liittoa | K | K | E | E | O | O | E | O | Tarkistettava | HTML | 1 | **P3** | Paraurheilu |
| Suomen Liikunta ja Urheilu (SLU) | https://www.slu.fi | Koko Suomi | – | K | O | E | E | O | O | E | O | Tarkistettava | HTML | 1 | **P2** | Kattojärjestö; ohjaa aluejärjestöihin |
| Nuori Suomi | https://www.nuorisuomi.fi | Koko Suomi | ~500 (lasten liikunta) | K | O | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Lasten ja nuorten liikuntakerhot |
| Suomen Latu (retkeily) | https://www.suomenlatu.fi | Koko Suomi | ~200 paikallisyhdistystä | K | K | O | E | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | Retkeily/hiihto, ei perinteinen urheiluseura |

---

## 4. Suomisport

Suomisport on **Suomen tärkein keskitetty seurarekisteri** lisenssi- ja jäsenyysdatalla.

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| Suomisport – seurahaku | https://www.suomisport.fi | Koko Suomi | 9 000–11 000 | K | K | O | O | O | O | O | O | Tarkistettava | HTML | 3 | **P1** | Laajin yksittäinen lähde; JS-painotteinen |
| Suomisport – API (Sportti-ID) | https://www.suomisport.fi/developers | Koko Suomi | 9 000–11 000 | K | K | O | O | O | O | O | O | API-ehdot | API | 2 | **P1** | API-dokumentaatio selvitettävä; preferoidaan scraperin sijaan |
| Suomisport – lisenssitiedot | https://www.suomisport.fi | Koko Suomi | – | K | K | O | E | E | E | E | E | Tarkistettava | HTML | 3 | **P2** | Aktiiviset lisenssinhaltijat; ei kaikkia seuroja |

---

## 5. Kuntien liikuntapalveluiden seurarekisterit

309 kuntaa/kaupunkia – suurimmat ylläpitävät seurarekistereitä. Alla **20 suurinta** + maakuntakohtainen yhteenveto.

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| Helsinki – urheiluseurat | https://www.hel.fi/liikunta | Helsinki | 300–400 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 3 | **P1** | Monimutkainen sivurakenne |
| Tampere – liikunta ja urheiluseurat | https://www.tampere.fi/liikunta | Tampere | 150–200 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P1** | Selkeä pilottikunta |
| Espoo – liikuntaseurat | https://www.espoo.fi/liikunta | Espoo | 200–250 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 3 | **P1** | |
| Vantaa – urheiluseurat | https://www.vantaa.fi/liikunta | Vantaa | 150–200 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 3 | **P1** | |
| Turku – liikuntaseurat | https://www.turku.fi/liikunta | Turku | 120–150 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Oulu – liikuntaseurat | https://www.ouka.fi/liikunta | Oulu | 120–150 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Jyväskylä – seurat | https://www.jyvaskyla.fi/liikunta | Jyväskylä | 100–130 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Lahti – liikuntaseurat | https://www.lahti.fi/liikunta | Lahti | 80–100 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Kuopio – liikuntaseurat | https://www.kuopio.fi/liikunta | Kuopio | 80–100 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P2** | |
| Pori – seurat | https://www.pori.fi/liikunta | Pori | 60–80 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Joensuu – liikuntaseurat | https://www.joensuu.fi/liikunta | Joensuu | 70–90 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Lappeenranta – seurat | https://www.lappeenranta.fi/liikunta | Lappeenranta | 60–80 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Hämeenlinna – seurat | https://www.hameenlinna.fi/liikunta | Hämeenlinna | 60–80 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Vaasa – seurat | https://www.vaasa.fi/liikunta | Vaasa | 70–90 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Seinäjoki – liikuntaseurat | https://www.seinajoki.fi/liikunta | Seinäjoki | 60–80 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Rovaniemi – liikuntaseurat | https://www.rovaniemi.fi/liikunta | Rovaniemi | 60–80 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Mikkeli – seurat | https://www.mikkeli.fi/liikunta | Mikkeli | 50–70 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Kouvola – liikuntaseurat | https://www.kouvola.fi/liikunta | Kouvola | 50–70 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Porvoo – seurat | https://www.porvoo.fi/liikunta | Porvoo | 50–70 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| Kotka – liikuntaseurat | https://www.kotka.fi/liikunta | Kotka | 40–60 | K | O | K | O | O | O | O | O | Tarkistettava | HTML | 2 | **P3** | |
| **Muut 280+ kuntaa (skaalattava malli)** | Vaihtelee | Koko Suomi | 1 000–2 000 | O | O | K | O | O | O | O | O | Tarkistettava | HTML, PDF | 3–4 | **P3** | Sama ingestoripohja, kuntakohtainen konfiguraatio |

**Maakuntakohtainen kuntakattavuus (arvio):**

| Maakunta | Kuntia | Seurarekisteriä arvio | Seuroja (arvio) |
|----------|--------|----------------------|-----------------|
| Uusimaa | 26 | 8–10 | 800–1 000 |
| Pirkanmaa | 22 | 5–7 | 300–400 |
| Varsinais-Suomi | 27 | 4–6 | 250–350 |
| Pohjois-Pohjanmaa | 30 | 3–5 | 200–300 |
| Keski-Suomi | 23 | 3–4 | 150–250 |
| Muut 14 maakuntaa | 181 | 20–40 yhteensä | 800–1 500 |

---

## 6. Avustusrekisterit

Kuntien ja valtion **liikunta-avustusten saajalistat** paljastavat aktiiviset seurat, joita ei välttämättä löydy lajiliitoista.

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| Helsinki – liikunta-avustukset | https://www.hel.fi/paatokset | Helsinki | 200–300 | K | E | K | E | E | E | E | O | Tarkistettava | HTML, PDF | 4 | **P2** | Päätöskirjat PDF; yhteyshenkilö usein |
| Tampere – toiminta-avustukset | https://www.tampere.fi/liikunta | Tampere | 100–150 | K | E | K | E | E | E | E | O | Tarkistettava | HTML, PDF | 4 | **P2** | |
| Espoo – liikunta-avustukset | https://www.espoo.fi/liikunta | Espoo | 150–200 | K | E | K | E | E | E | E | O | Tarkistettava | HTML, PDF | 4 | **P2** | |
| Vantaa – avustukset | https://www.vantaa.fi/liikunta | Vantaa | 100–150 | K | E | K | E | E | E | E | O | Tarkistettava | HTML, PDF | 4 | **P3** | |
| Opetus- ja kulttuuriministeriön liikuntapaikkarahoitus | https://www.minedu.fi | Koko Suomi | 500–1 000 | K | E | O | E | E | E | E | O | Tarkistettava | HTML, PDF | 4 | **P2** | Valtion avustukset liikuntapaikkoihin |
| STEA – avustustiedot | https://www.stea.fi | Koko Suomi | 50–100 (liikunta) | K | E | O | E | E | E | E | O | Tarkistettava | HTML | 3 | **P4** | Pääasiassa järjestöavustukset |
| Avoindata.fi – kuntien avustusdata | https://www.avoindata.fi | Vaihtelee | Vaihtelee | O | E | O | E | E | E | E | E | Tarkistettava | API, CSV | 2 | **P2** | Rakenteinen data harvassa; etsintä tarpeen |
| Kuntaliitto – avustuskäytännöt | https://www.kuntaliitto.fi | Koko Suomi | – | E | E | E | E | E | E | E | E | Tarkistettava | HTML | 1 | **P4** | Ei seuralistaa; taustatieto |
| Liikuntavälineiden avustuslistat (19 aluetta) | Vaihtelee | Alueellinen | 200–400/alue | K | E | O | E | E | E | E | O | Tarkistettava | PDF, HTML | 4 | **P2** | Päällekkäin aluejärjestöjen kanssa |
| Turku – liikunta-avustukset | https://www.turku.fi | Turku | 80–120 | K | E | K | E | E | E | E | O | Tarkistettava | PDF | 4 | **P3** | |
| Oulu – avustukset | https://www.ouka.fi | Oulu | 80–120 | K | E | K | E | E | E | E | O | Tarkistettava | PDF | 4 | **P3** | |
| Kuntien dynaamiset avustusrekisterit (yhteinen malli) | Vaihtelee | 50+ kuntaa | 1 000–2 000 | K | E | K | E | E | E | E | O | Tarkistettava | PDF, HTML | 4 | **P3** | PDF-parsinta raskasta |

---

## 7. Liikuntatilojen käyttäjärekisterit

Kuntien **liikuntatilojen vuorolistat ja käyttäjät** paljastavat seuroja, joilla on säännöllinen tilariippuvuus.

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| Helsinki – liikuntatilojen vuorolistat | https://www.hel.fi/liikuntavirasto | Helsinki | 200–300 | K | O | K | O | E | E | E | E | Tarkistettava | HTML, PDF | 3 | **P2** | Seuran nimi vuorolistassa |
| Tampere – liikuntatilat | https://www.tampere.fi/liikuntatilat | Tampere | 100–150 | K | O | K | O | E | E | E | E | Tarkistettava | HTML | 3 | **P2** | |
| Espoo – liikuntatilojen käyttö | https://www.espoo.fi/liikuntapalvelut | Espoo | 150–200 | K | O | K | O | E | E | E | E | Tarkistettava | HTML | 3 | **P2** | |
| Vantaa – liikuntatilat | https://www.vantaa.fi/liikunta | Vantaa | 100–150 | K | O | K | O | E | E | E | E | Tarkistettava | HTML | 3 | **P3** | |
| Oulu – liikuntatilat | https://www.ouka.fi/liikuntapalvelut | Oulu | 80–120 | K | O | K | O | E | E | E | E | Tarkistettava | HTML | 3 | **P3** | |
| Turku – liikuntatilat | https://www.turku.fi/liikuntatilat | Turku | 80–120 | K | O | K | O | E | E | E | E | Tarkistettava | HTML | 3 | **P3** | |
| Jyväskylä – liikuntatilat | https://www.jyvaskyla.fi/liikunta | Jyväskylä | 60–90 | K | O | K | O | E | E | E | E | Tarkistettava | HTML | 3 | **P3** | |
| Kuntien liikuntatilakatalogit (yhteinen malli) | Vaihtelee | 30+ kuntaa | 500–1 000 | K | O | K | O | E | E | E | E | Tarkistettava | HTML, PDF | 3 | **P3** | Täydentää seurarekistereitä |
| Liikuntapaikkojen avoin kartta (LIPAS) | https://www.lipas.fi | Koko Suomi | 1 000+ paikkaa | E | E | O | O | O | E | E | E | Tarkistettava | HTML, API | 2 | **P3** | Liikuntapaikat, ei seuroja; taustatieto |
| OKM – liikuntapaikkarekisteri | https://www.lipas.fi | Koko Suomi | – | E | E | O | O | O | E | E | E | Tarkistettava | API | 2 | **P4** | Paikkadata, ei seuroja |

---

## 8. Varausjärjestelmät

Kaupalliset ja kuntien **varausjärjestelmät** sisältävät seurojen nimiä säännöllisinä käyttäjinä.

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| Bookery | https://www.bookery.fi | 100+ kuntaa | 1 500–3 000 | K | O | O | E | E | E | E | E | Rajoitettu | HTML, API | 4 | **P2** | Laajin varausjärjestelmä; API/kumppanuus selvitettävä |
| Tulospalvelu.fi (jääkiekko) | https://tulospalvelu.fi | Koko Suomi | ~400 | K | K | O | E | O | E | E | E | Tarkistettava | HTML, API | 2 | **P2** | Jääkiekkoseurat + sarjat |
| Sotkanet (suunnistus) | https://www.sotkanet.fi | Koko Suomi | ~200 | K | K | O | E | O | E | E | E | Tarkistettava | HTML | 2 | **P3** | Suunnistusseurat |
| Matchi (tennis/padel) | https://www.matchi.se | Koko Suomi | 200–400 | K | K | O | E | O | E | E | E | Rajoitettu | HTML, API | 3 | **P3** | Tennis- ja padelklubit |
| Playtomic (padel) | https://playtomic.io | Kaupungit | 100–200 | K | K | O | E | O | E | E | E | Rajoitettu | HTML, API | 4 | **P3** | Padel; kaupallinen |
| eBall / Tuomasmatrix (jalkapallo) | https://www.eball.fi | Koko Suomi | 500–800 | K | K | O | E | O | E | E | E | Tarkistettava | HTML | 3 | **P2** | Jalkapallokenttien varaukset |
| Reservix | https://www.reservix.fi | Vaihtelee | 200–400 | K | O | O | E | E | E | E | E | Rajoitettu | HTML | 4 | **P3** | Tapahtuma- ja tila varaukset |
| MyClub | https://www.myclub.fi | Vaihtelee | 300–500 | K | K | O | E | O | O | E | O | Rajoitettu | HTML, API | 3 | **P3** | Seuran hallinta; jäsenlistat suljettu |

---

## 9. Muut julkiset seurahakemistot

| Nimi | URL | Kattavuus | Seuroja | Nimi | Laji | Kunta | Osoite | Web | Email | Puh | Yhteys | robots.txt | Muoto | Vaikeus | Prior. | Huomio |
|------|-----|-----------|---------|------|------|-------|--------|-----|-------|-----|--------|------------|-------|---------|--------|--------|
| PRH – Yhdistysrekisteri | https://www.prh.fi/yhdistysrekisteri | Koko Suomi | 15 000+ yhdistystä | K | E | O | O | E | E | E | E | API saatavilla | HTML, API | 2 | **P1** | Kaikki rekisteröidyt yhdistykset; suodatus urheiluun |
| Suomi.fi – yhdistysten haku | https://www.suomi.fi/yhdistys | Koko Suomi | 15 000+ | K | E | O | E | E | E | E | E | Tarkistettava | HTML | 2 | **P2** | PRH-datan päällä |
| Avoindata.fi – liikuntadata | https://www.avoindata.fi | Vaihtelee | Vaihtelee | O | O | O | O | O | O | O | O | Tarkistettava | API, CSV | 2 | **P2** | Kuntien avoin data |
| Finder / Proff (yrityshaku) | https://www.finder.fi | Koko Suomi | 500–1 000 | K | E | O | O | E | E | O | E | Rajoitettu | HTML | 3 | **P3** | Osakeyhtiömuotoiset seurat |
| Facebook – seurasivut | https://www.facebook.com | Koko Suomi | Epävarma | K | O | O | E | O | O | E | O | Rajoitettu | API | 5 | **P4** | API-rajoitukset; epäluotettava |
| Google Maps | https://maps.google.com | Koko Suomi | Epävarma | K | O | O | O | O | O | O | E | Rajoitettu | API | 4 | **P4** | Käyttöehdot rajoittavat |
| Wikipedia – luettelot | https://fi.wikipedia.org | Vaihtelee | 50–100 | K | K | O | E | O | E | E | E | Sallittu | HTML | 1 | **P4** | Epätäydellinen; viite |
| Seuratoiminta.fi (jos aktiivinen) | – | – | – | – | – | – | – | – | – | – | – | – | – | – | **P4** | Selvitettä onko aktiivinen |
| Kuntien avoimen datan portaalit | Vaihtelee | 20+ kuntaa | 500–1 000 | O | O | O | O | O | O | O | O | Tarkistettava | API, CSV | 2 | **P2** | Helsinki, Tampere, Oulu avoimimpia |
| YTJ (Yhteishaku) | https://www.ytj.fi | Koko Suomi | 15 000+ | K | E | O | O | E | E | E | E | API | API | 2 | **P2** | PRH:n API-pohja; parempi automatisointiin |

---

## Päällekkäisyysanalyysi

```
                    Suomisport
                   /    |    \
                  /     |     \
           Lajiliitot  Kunnat  Aluejärj.
              |         |         |
              +----+----+----+----+
                   |
              PRH/YTJ (laajin, ei lajia)
                   |
         Avustusrekisterit (täydentää, ei lajia)
                   |
         Varausjärjestelmät (täydentää, laji osittain)
```

| Lähdepari | Arvioitu päällekkäisyys | Huomio |
|-----------|-------------------------|--------|
| Suomisport ∩ Lajiliitot | 70–85 % | Suomisport laajempi (kaikki lajit) |
| Suomisport ∩ Kunnat | 50–65 % | Kunnat sisältävät pieniä/aktiivisia seuroja |
| Lajiliitot ∩ Lajiliitot | 0 % | Eri lajit (monitoimiseurat duplikaatti) |
| Aluejärjestöt ∩ Kunnat | 60–75 % | Sama seura molemmissa |
| PRH ∩ Kaikki muut | 30–45 % | Laajin; sisältää ei-urheiluyhdistyksiä |
| Avustusrekisterit ∩ Kunnat | 80–90 % | Avustus = aktiiviset paikalliset seurat |
| Varausjärjestelmät ∩ Lajiliitot | 40–60 % | Aktiiviset seurat, joilla on vuoroja |

**Deduplikointistrategia (suunniteltu):**

1. **Tarkka osuma:** normalisoitu nimi + kunta + laji
2. **Epätarkka osuma:** Levenshtein-etäisyys + postinumero
3. **Y-Tunnus / PRH-tunnus:** jos saatavilla
4. **Manuaalinen tarkistus:** `needs_review`-merkintä epävarmoille

---

## Optimaalinen keruujärjestys

Tavoite: **maksimoida kattavuus minimoidulla työmäärällä** ennen kuin siirrytään P3/P4-lähteisiin.

### Vaihe A – Peruskattavuus (P1, arvio ~10 000 seuraa)

| Järjestys | Lähde | Miksi ensin | Arvioitu työmäärä |
|-----------|-------|-------------|-------------------|
| A1 | **PRH/YTJ API** | Rakenteinen, kattava, suodatus urheiluyhdistyksille | 1–2 viikkoa |
| A2 | **Suomisport API** | Laajin seurarekisteri, laji + yhteystiedot | 1–2 viikkoa |
| A3 | **Laji.fi** | Aggregoi lajiliitot yhteen hakuun | 1 viikko |
| A4 | **Olympiakomitea jäsenlista** | Validoi lajiliittojen täydellisyys | 1 päivä |

**Tulos vaiheen A jälkeen:** ~9 000–11 000 seuraa, 70 %+ deduplikoitu.

### Vaihe B – Paikallinen rikastaminen (P1–P2, arvio +2 000–3 000 seuraa)

| Järjestys | Lähde | Miksi | Työmäärä |
|-----------|-------|-------|----------|
| B1 | **Tampere seurarekisteri** | Pilottikunta, selkeä HTML | 3–5 päivää |
| B2 | **Helsinki seurarekisteri** | Suurin volyymi | 1 viikko |
| B3 | **Espoo + Vantaa** | PK-seutu kattava | 1 viikko |
| B4 | **ELSA + Pirkanmaa + Länsi-Uusimaa** | Aluejärjestöt täydentävät | 2 viikkoa |
| B5 | **Palloliitto + Jääkiekkoliitto** | Suurimmat lajit erikseen (validointi) | 1 viikko |

**Tulos vaiheen B jälkeen:** +2 000 uutta/tarkistettua seuraa, kunta- ja yhteystieto paranee.

### Vaihe C – Lajikattavuuden laajennus (P2, arvio +1 000–2 000 seuraa)

| Järjestys | Lähde | Miksi |
|-----------|-------|-------|
| C1 | Top 10 lajiliittoa (salibandy, pesäpallo, koripallo, …) | Suurimmat lajit |
| C2 | Loput 19 liikuntavälinettä | Maakuntakohtainen kattavuus |
| C3 | Top 15 kuntaa (Turku, Oulu, Jyväskylä, …) | Kuntakattavuus 50 %+ väestöstä |

### Vaihe D – Täydentävät lähteet (P2–P3)

| Järjestys | Lähde | Miksi |
|-----------|-------|-------|
| D1 | Avustusrekisterit (Helsinki, Tampere, Espoo) | Aktiiviset seurat, yhteyshenkilö |
| D2 | Tulospalvelu.fi + eBall | Jääkiekko- ja jalkapalloseurat |
| D3 | Bookery (API/kumppanuus) | Laaja varausjärjestelmä |
| D4 | Avoindata.fi -datasetit | Rakenteinen data harvinaisista kunnista |
| D5 | Loput lajiliitot (40+ pienempää) | Lajikattavuus 95 %+ |

### Vaihe E – Viimeistely (P3–P4)

| Järjestys | Lähde | Miksi |
|-----------|-------|-------|
| E1 | Loput 250+ kuntaa (skaalattava malli) | Täydellinen maantieteellinen kattavuus |
| E2 | Liikuntatilojen käyttäjärekisterit | Täydentää puuttuvia seuroja |
| E3 | Matchi, Playtomic, MyClub | Padel, tennis, erikoislajit |
| E4 | Facebook, Google Maps | Viimeinen fallback, epäluotettava |

### Keruujärjestyksen periaate

```
PRH/YTJ + Suomisport  →  peruskattavuus (80 %)
        ↓
Laji.fi + suurimmat lajiliitot  →  lajitarkkuus
        ↓
Kunnat + aluejärjestöt  →  paikallinen tarkkuus + yhteystiedot
        ↓
Avustusrekisterit + varausjärjestelmät  →  aktiivisuus + yhteyshenkilöt
        ↓
Pienet lajiliitot + loput kunnat  →  täydellisyys
```

---

## Seuraavat askeleet

- [ ] Vahvista P1-lähteiden URL-rakenteet manuaalisesti (3–5 lähdettä)
- [ ] Tarkista robots.txt ja käyttöehdot P1-lähteille
- [ ] Selvitä Suomisport API -pääsy ja YTJ API -rajapinta
- [ ] Testaa PRH/YTJ:stä urheiluyhdistysten suodatus (avainsanat, toimialakoodit)
- [ ] Määrittele `Source`-metadatamalli koodissa (synkronoitu tähän dokumenttiin)
- [ ] Täydennä puuttuvat lajiliitot Olympiakomitean jäsenlistalta
- [ ] Kartoita Bookery-kuntien lista ja API-mahdollisuus
- [ ] Laadi deduplikointisäännöt dokumentiksi ennen ingestointia

## Eettiset ja juridiset huomiot

- Noudata lähteiden käyttöehtoja ja `robots.txt`-sääntöjä
- Suosi virallisia API-rajapintoja (PRH/YTJ, Suomisport) scraperin sijaan
- Käytä kohtuullista pyyntöviivettä (oletus 1 s)
- Kerää vain **seuratason** tietoja – ei pelaajia, valmentajia tai jäsenlistoja
- Dokumentoi jokaisen tietueen alkuperä (`source_id`, `source_url`, `collected_at`)
- PRH/YTJ-data on julkista, mutta yhdistysten luokittelu urheiluseuroiksi vaatii suodatuslogiikan
