# Medical Dictionary Tools

Scripts and code to build local PostgreSQL databases from raw MedDRA and WHODrug files.

* MedDRA: <https://meddra.com/>
* WHODrug: <https://who-umc.org/whodrug/>

Both dictionaries are regularly updated and require subscription credentials to download.

## Dependencies

* Python 3 packages (see below)
* Docker and Docker Compose (for running PostgreSQL locally)

## Quick Start

### 1. Start PostgreSQL

```bash
docker compose up -d
```

The database will be available at:
- **Host**: localhost
- **Port**: 5433
- **Default Database**: meddict
- **Username**: meddict
- **Password**: meddict

Connection string: `postgresql://meddict:meddict@localhost:5433/meddict`

The container hosts multiple databases (one per dictionary version):
- `meddra_281` — MedDRA v28.1
- `whodrug_2603` — WHODrug Global C3 March 2026
- etc.

### 2. Install Python packages

```sh
python3 -m pip install BioClients
python3 -m pip install psycopg2
```

(`BioClients` is only needed for MedDRA import)

---

## MedDRA

### Import MedDRA

1. Locate the `.asc` files from MedDRA (subscription required) and paste them inside `data/MedAscii/`
2. Update `LATEST_RELEASE.txt` with the version (e.g., `28.1`)
3. Run:

```sh
./sh/Go_meddra_DbCreate.sh
```

The script creates a database named `meddra_281` (version without dots) with all MedDRA terms.

### MedDRA Hierarchy (descending order)

```
SOC  = System Organ Class
HLGT = High Level Group Term
HLT  = High Level Term
PT   = Preferred Term
LLT  = Lowest Level Term
```

### System Organ Classes

|id 	|text 	|abbr |
|:---:|:---|:---|
|10005329	|Blood and lymphatic system disorders	|Blood |
|10007541	|Cardiac disorders	|Card |
|10010331	|Congenital, familial and genetic disorders	|Cong |
|10013993	|Ear and labyrinth disorders	|Ear |
|10014698	|Endocrine disorders	|Endo |
|10015919	|Eye disorders	|Eye |
|10017947	|Gastrointestinal disorders	|Gastr |
|10018065	|General disorders and administration site conditions	|Genrl |
|10019805	|Hepatobiliary disorders	|Hepat |
|10021428	|Immune system disorders	|Immun |
|10021881	|Infections and infestations	|Infec |
|10022117	|Injury, poisoning and procedural complications	|Inj&P |
|10022891	|Investigations	|Inv |
|10027433	|Metabolism and nutrition disorders	|Metab |
|10028395	|Musculoskeletal and connective tissue disorders	|Musc |
|10029104	|Neoplasms benign, malignant and unspecified (incl...	|Neopl |
|10029205	|Nervous system disorders	|Nerv |
|10036585	|Pregnancy, puerperium and perinatal conditions	|Preg |
|10037175	|Psychiatric disorders	|Psych |
|10038359	|Renal and urinary disorders	|Renal |
|10038604	|Reproductive system and breast disorders	|Repro |
|10038738	|Respiratory, thoracic and mediastinal disorders	|Resp |
|10040785	|Skin and subcutaneous tissue disorders	|Skin |
|10041244	|Social circumstances	|SocCi |
|10042613	|Surgical and medical procedures	|Surg |
|10047065	|Vascular disorders	|Vasc |
|10077536	|Product issues	|Prod |

---

## WHODrug C3

### Import WHODrug

1. Copy WHODrug Global C3 CSV files to `data/WHODrugC3/`:
   - `MP.csv`, `ThG.csv`, `ING.csv`, `SUN.csv`, `ATC.csv`, `PF.csv`, `STR.csv`,
     `ORG.csv`, `SRCE.csv`, `CCODE.csv`, `PRT.csv`, `UNIT.csv`, `Version.csv`

2. Update `LATEST_WHODRUG_RELEASE.txt` with the version code (e.g., `2603`)

3. Run:

```sh
./sh/Go_whodrug_DbCreate.sh
```

The script creates a database named `whodrug_2603` with all 13 WHODrug C3 tables.

### Version Naming

WHODrug releases twice per year (March and September). Version code format: `YYMM`.

| Release | Code | Database |
|---------|------|----------|
| March 2026 | `2603` | `whodrug_2603` |
| September 2026 | `2609` | `whodrug_2609` |
| March 2027 | `2703` | `whodrug_2703` |

Multiple versions can coexist in the same PostgreSQL container.

### WHODrug C3 Tables

| Table | Description | Rows |
|-------|-------------|------|
| `mp` | Medicinal Products (main table) | ~5.6M |
| `thg` | Therapeutic Groups (ATC assignments) | ~6.0M |
| `ing` | Ingredients | ~9.0M |
| `sun` | Substances | ~28K |
| `atc` | ATC Classification (5 levels) | ~1.4K |
| `pf` | Pharmaceutical Forms | ~226 |
| `str` | Strengths/Dosages | ~18K |
| `org` | Organizations (manufacturers) | ~92K |
| `srce` | Sources/References | ~508 |
| `ccode` | Country Codes (ISO 3166-1) | ~250 |
| `prt` | Product Types | ~10 |
| `unit` | Units of Measurement | ~84 |
| `version` | Dataset version info | 1 |

### WHODrug C3 Hierarchy

```
MP (Medicinal Products)
  --> THG (Therapeutic Groups) --> ATC (Classification, 5 levels)
  --> ING (Ingredients) --> SUN (Substances)
  --> PF (Pharmaceutical Forms)
  --> STR (Strengths)
  --> ORG (Organizations)
  --> CCODE (Countries)
  --> PRT (Product Types)
```

### Example Queries

```sql
-- Search for a drug by name
SELECT record_id, drug_name, drug_rec_no || seq1 || seq2 AS drug_code
FROM mp
WHERE drug_name ILIKE '%paracetamol%'
ORDER BY drug_name
LIMIT 20;

-- Full hierarchy: drug with ingredients, ATC codes, and references
SELECT mp.drug_name, sun.substance_name, atc.atc_code, atc.text AS atc_text,
       pf.text AS form, str.text AS strength, ccode.country_name
FROM mp
LEFT JOIN ing ON mp.record_id = ing.record_id
LEFT JOIN sun ON ing.substance_id = sun.substance_id
LEFT JOIN thg ON mp.record_id = thg.record_id
LEFT JOIN atc ON thg.atc_code = atc.atc_code
LEFT JOIN pf ON mp.seq3 = pf.pharmform_id
LEFT JOIN str ON mp.seq4 = str.strength_id
LEFT JOIN ccode ON mp.country = ccode.country_code
WHERE mp.drug_name ILIKE '%aspirin%'
LIMIT 20;
```

---

## Configuration

### Environment Variables

You can override connection defaults via environment variables or a `.env` file:

```env
PGHOST=localhost
PGPORT=5433
PGUSER=meddict
PGPASSWORD=meddict
```

### Legacy Configuration

If you need to use the old MedDRA credentials (`meddra/meddra` on port `5432`), create a `.env` file:

```env
POSTGRES_USER=meddra
POSTGRES_PASSWORD=meddra
POSTGRES_DB=meddra
POSTGRES_PORT=5432
```

### Dump and Restore

```sh
# Dump
pg_dump --no-privileges -Fc -d whodrug_2603 > whodrug_2603.pgdump

# Restore
createdb whodrug_2603
pg_restore -e -O -x -d whodrug_2603 whodrug_2603.pgdump
```

### Stop PostgreSQL

```bash
docker compose down
```
