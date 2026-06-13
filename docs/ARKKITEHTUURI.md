# Arkkitehtuuri – pysyvät suunnitteluperiaatteet

Tämä dokumentti määrittelee UrheiluseuraPro:n **pysyvät arkkitehtuuriset periaatteet**. Ne eivät ole toteutusvaiheen ohjeita vaan sitovia sääntöjä, joita kaikki keruu-, merge- ja tallennuskerrokset noudattavat.

Tekninen toteutus: [architecture.md](architecture.md) (komponentit ja tietovirta) · [data-model.md](data-model.md) (sovelluskerros) · [database-schema.md](database-schema.md) (SQL-skeema)

---

## 1. Peruslupaus: havainnot ovat pyhiä

UrheiluseuraPro ei ole yksinkertainen “viimeisin arvo voittaa” -tietokanta. Se on **master-tietokanta, joka koostuu säilytetyistä lähdehavainnoista**.

```
Lähteet → Havainnot (staging) → Merge → Master-arvot (laskettu näkymä)
              ↑                        |
              └── ei koskaan poisteta ←┘
```

### Periaate 1 – Havaintoja ei poisteta automaattisesti

Lähteistä kerättyjä havaintoja **ei koskaan poisteta automaattisesti**. Vanhentunut, ristiriitainen tai virheellinen havainto säilyy historiassa. Poisto tai arkistointi vaatii erillisen, eksplisiittisen toimen (esim. manuaalinen merkintä, tuleva `rejected`-tila).

**Toteutus:** `FieldObservation`-rivit lisätään append-only -periaatteella (`merge/engine.py` → `append_observation_fields`). Testit varmistavat, ettei havaintojen määrä vähene merge-vaiheessa.

### Periaate 2 – Havaintoja ei ylikirjoiteta automaattisesti

Sama lähde voi tuottaa uuden havainnon myöhemmin, mutta **olemassa olevaa havaintoriviä ei korvata hiljaisesti**. Uusi keruu luo uuden havainnon tai päivittää erillisiä metadata-kenttiä (`last_seen_at`), ei ylikirjoita aiempaa arvoa samalla `(observation_id, field_name, arvo)` -sormenjäljellä.

**Toteutus:** Duplikaattien esto perustuu sormenjälkeen `(observation_id, field_name, normalisoitu_arvo)`. Olemassa oleva havainto jää ennalleen.

### Periaate 3 – Provenance säilytetään aina

Jokaisesta havainnosta säilytetään **alkuperäinen jäljitettävyys**:

| Metatieto | Kenttä (sovelluskerros) | SQL (staging) |
|-----------|-------------------------|---------------|
| Lähde | `source_id` | `observations.source_id` |
| Lähde-URL | `source_url` | `observations.source_url` |
| Lähdeavain | `source_record_key` | `observations.source_record_key` |
| Havainto-ID | `observation_id` | `observations.id` |
| Havaintoaika | `observed_at` | `observations.collected_at` |
| Raaka-arvo | `raw_value` | `observation_*`-taulut |

Lisäksi master-tason provenienssi: `FieldProvenance`, `MasterFieldValue.supporting_sources`, `field_provenance`-taulu.

### Periaate 4 – Master lasketaan, havaintoja ei hävitetä

**Master-arvot ovat johdettuja**, eivät ensisijaisia. `Club.contact.email`, `Club.identity.name` jne. ovat **laskettuja näkymiä** (`MasterFieldValue`), jotka voidaan laskea uudelleen milloin tahansa kaikista säilytetyistä `FieldObservation`-riveistä.

```
field_observations (kaikki)  →  recompute_master_values()  →  master_values + Club-kentät
```

Master-päivitys **ei saa** poistaa, ylikirjoittaa tai piilottaa yhtään alkuperäistä havaintoa.

### Periaate 5 – Ristiriitaiset havainnot voivat olla rinnakkain

Samasta kentästä (osoite, sähköposti, puhelin, verkkosivu, kunta jne.) voi olla **useita ristiriitaisia havaintoja samanaikaisesti**. Ristiriita ei ole virhetila vaan normaali tilanne, kun useat lähteet kertovat eri asioita.

- Kaikki arvot säilyvät `field_observations`-listassa.
- Aktiivinen master-arvo on **yksi valittu näkymä**, ei ainoa totuus.
- Toissijaiset arvot voidaan näyttää esim. `email_secondary`-kentässä tai erillisessä historianäkymässä.

### Periaate 6 – Havainnon minimimetadata

Jokaisesta havainnosta tulee säilyttää vähintään:

| Vaatimus | Toteutus nyt | Huomio |
|----------|--------------|--------|
| **source** | `FieldObservation.source_id` | Pakollinen |
| **source_url** | `FieldObservation.source_url` | Kun lähteessä saatavilla |
| **first_seen_at** | `FieldObservation.observed_at` / `ClubSourceLink.first_seen_at` | Erillinen `first_seen_at` havaintokohtaisesti tulevaisuudessa |
| **last_seen_at** | `ClubSourceLink.last_seen_at` | Päivittyy uudelleenkeruussa samasta lähteestä |
| **confidence** | `FieldObservation.observation_confidence` / `MasterFieldValue.confidence_score` | Havainnon ja master-valinnan luottamus erikseen |

Master-valinnan luottamus (`confidence_score`) lasketaan lähteen prioriteetista, yksimielisyydestä ja konfliktitilanteesta.

### Periaate 7 – Deterministinen ja toistettava merge

Merge-prosessin tulee olla **deterministinen**: samat havainnot + samat lähdeprioriteetit → aina sama master-tulos.

Determinismi varmistetaan:

1. **Kiinteä prioriteettijärjestys** (`merge/priorities.py`) – ei satunnaisuutta
2. **Selkeä vertailujärjestys** – prioriteetti → tuoreus → yksimielisyys
3. **Normalisoidut vertailuavaimet** – sama sähköposti eri kirjoitusasuilla ryhmittyy oikein
4. **Uudelleenlaskenta** – `recompute_master_values()` tuottaa tuloksen alusta, ei inkrementaalista sääntösekamelskaa

```python
# Sama syöte → sama tulos
masters_a = recompute_master_values(club, sources)
masters_b = recompute_master_values(club, sources)
assert masters_a == masters_b
```

### Periaate 8 – Kaikkien päätösten jäljitettävyys

Jokainen master-kentän valinta on **auditoitavissa**:

| Päätös | Jälki |
|--------|-------|
| Miksi tämä sähköposti on master? | `MasterFieldValue.primary_source_id`, `primary_observation_id` |
| Mitkä lähteet tukivat valintaa? | `MasterFieldValue.supporting_sources` |
| Mitä muita arvoja hylättiin? | `MasterFieldValue.conflicting_values`, `has_conflict` |
| Milloin valinta tehtiin? | `MasterFieldValue.selected_at` |
| Historiallinen provenienssi | `FieldProvenance`, `field_observations` |

Konfliktit merkitään `needs_review = True` master-tietueessa, jos ristiriitoja on.

---

## 2. Ristiriitatilanteiden käsittely

Seuraavat säännöt ovat **sitovia** kaikissa merge-skenaarioissa.

### Sähköposti

**Tilanne:** Lähde A: `info@seura.fi`, lähde B: `yhteys@seura.fi`

| Toimenpide | Sallittu | Kielletty |
|------------|----------|-----------|
| Säilytä molemmat havainnot | ✅ | |
| Valitse master prioriteetin perusteella | ✅ | |
| Poista heikomman lähteen havainto | | ❌ |
| Ylikirjoita A:n havainto B:llä | | ❌ |

### Puhelinnumero

**Tilanne:** Lähde A: `+358 40 111 1111`, lähde B: `+358 50 222 2222`

Sama logiikka kuin sähköpostissa. Molemmat `FieldObservation`-rivit (`field_name = "phone"`) säilyvät. Master-valinta käyttää lähdeprioriteettia (esim. seuran oma sivu > Suomisport > kunta).

### Osoite

**Tilanne:** Lähde A: `Katu 1, Tampere`, lähde B: `Katu 2, Tampere`

Molemmat osoitehavainnot säilyvät (`field_name = "address_full"`). Master osoittaa parhaan arvioitua osoitetta; historialliset osoitteet ovat edelleen haettavissa havainnoista.

### Verkkosivu

**Tilanne:** Lähde A: `https://vanha.seura.fi`, lähde B: `https://uusi.seura.fi`

Molemmat URL-havainnot säilyvät. Seuran oma verkkosivu (prioriteetti 100) voittaa tyypillisesti master-valinnassa, mutta vanha URL ei katoa.

### Yhteinen kaava

```
Konflikti havaittu
    │
    ├─→ Kaikki havainnot säilyvät (field_observations)
    │
    ├─→ Master valitaan: prioriteetti → tuoreus → yksimielisyys
    │
    ├─→ confidence_score lasketaan (alempi jos ristiriita)
    │
    └─→ needs_review = True (jos useita eri arvoja)
```

---

## 3. Lähdeprioriteetit (master-valinta)

Master-arvo valitaan **havainnoista**, ei suoraan lähteestä. Prioriteetti vaikuttaa valintaan, kun arvot eroavat:

| Järjestys | Lähde | Prioriteetti |
|----------|-------|--------------|
| 1 | Seuran oma verkkosivu | 100 |
| 2 | Suomisport | 90 |
| 3 | Olympiakomitea | 85 |
| 4 | Lajiliitto | 80 |
| 5 | Kunnan sivut | 70 |
| 6 | PRH / YTJ | 65 |
| 7 | Muu lähde | 40 |

Täysi prioriteettilista: `merge/priorities.py`

**Tärkeää:** Korkea prioriteetti valitsee **master-näkymän**, ei poista muita havaintoja.

---

## 4. Kerrosmalli

```
┌─────────────────────────────────────────────────────────────┐
│ KERUU          ClubObservation (yksi lähde, yksi hetki)    │
├─────────────────────────────────────────────────────────────┤
│ NORMALISOINTI  normalisoidut kentät (vertailua varten)      │
├─────────────────────────────────────────────────────────────┤
│ DEDUP          match_observation_to_club() → master-org      │
├─────────────────────────────────────────────────────────────┤
│ MERGE          append_observation_fields()  ← append-only    │
│                recompute_master_values()    ← deterministinen│
├─────────────────────────────────────────────────────────────┤
│ MASTER         Club + MasterFieldValue (laskettu näkymä)     │
├─────────────────────────────────────────────────────────────┤
│ SQL            observations*, organizations*, field_provenance│
└─────────────────────────────────────────────────────────────┘
```

**Totuuden lähde:** kaikki `FieldObservation`-rivit (sovelluskerros) ja `observation_*`-taulut (SQL).

**Master on näkymä:** `organizations`-taulun aktiiviset arvot + `organization_profile` -hakukiihdytin.

---

## 5. Mitä merge EI saa tehdä

Seuraavat toimenpiteet ovat **arkkitehtuurin vastaisia** ja kiellettyjä automaattisessa prosessissa:

- Poistaa vanhaa `FieldObservation`-riviä uuden tullen
- Korvata havainnon arvoa ilman uutta havaintoriviä
- Kirjoittaa master-kenttää suoraan ilman provenience-jälkeä
- Piilottaa ristiriitaista dataa “siivoamalla” duplikaatteja pois
- Käyttää satunnaisuutta tai aikaleimaa ilman dokumentoituja sääntöjä

---

## 6. Testaus ja validointi

Periaatteet on lukittu testeihin:

| Testi | Periaate |
|-------|----------|
| `test_all_observations_preserved_after_multiple_merges` | 1, 2, 5 |
| `test_conflicting_emails_higher_priority_wins` | 4, 5, ristiriidat |
| `test_master_updates_without_losing_history` | 1, 4 |
| `test_supporting_sources_when_sources_agree` | 7, 8 |
| `test_duplicate_observation_not_appended_twice` | 2 (idempotenssi) |

Aja: `pytest tests/test_merge_engine.py`

---

## 7. Liittyvät tiedostot

| Tiedosto | Rooli |
|----------|-------|
| `src/urheiluseurapro/merge/engine.py` | Merge-logiikka |
| `src/urheiluseurapro/merge/priorities.py` | Lähdeprioriteetit |
| `src/urheiluseurapro/models/merge_state.py` | `FieldObservation`, `MasterFieldValue` |
| `src/urheiluseurapro/models/provenance.py` | `FieldProvenance`, `ClubSourceLink` |
| `db/schema.sql` | Staging + provenance -taulut |
| `tests/test_merge_engine.py` | Periaatteiden regressiotestit |

---

## 8. Muutokset tähän dokumenttiin

Tämä on **normatiivinen** dokumentti. Jos toteutus poikkeaa periaatteista, **toteutus on väärin** – ei periaatteet.

Poikkeukset (manuaalinen korjaus, admin-toiminnot) dokumentoidaan erikseen eivätkä saa muuttaa automaattisen merge-polun käytöstä.

*Viimeksi päivitetty: projektin merge-engine -vaihe*
