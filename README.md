# MedDRA Tools

Includes scripts and code to build local PostgreSql db from raw MedDRA files.

* <https://meddra.com/>
* MedDRA is regularly updated, &gt;1/year.
* Latest at time of this writing: v28.0 (March 2025).

(Download credentials required, via MedDRA subscription.)

## Dependencies

 * [BioClients](https://github.com/jeremyjyang/BioClients) for use of Csv2Sql.

## Introduction

MedDRA = Medical Dictionary for Regulatory Activities
MSSO = Maintenance and Support Services Organization
COSTAR(T) = Computer-Stored Ambulatory Record (Term)

### Hierarchy of terms (descending order):

	SOC = System Organ Class
	HLGT = High Level Group Term
	HLT = High Level Term
	PT = Preferred Term
	LLT = Lowest Level Term

### System Organ Classes:

|id 	|text 	|abbr |
|:---:|:---|:---|
|10005329	|Blood and lymphatic system disorders	|Blood |
|10007541	|Cardiac disorders	Card |
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

Each term has a code, which are specified in the files hlgt.asc, hlt.asc,
llt.asc, pt.asc, and soc.asc, for example from hlgt.asc:

> 10012272$Dementia and amnestic conditions$$$$$$$$
> 10012303$Demyelinating disorders$$$$$$$$
> 10012375$Depressed mood disorders and disturbances$$$$$$$$
> 10012562$Developmental disorders NEC$$$$$$$$
> 10012653$Diabetic complications$$$$$$$$
> 10013296$Bone, calcium, magnesium and phosphorus metabolism disorders$$$$$$$$
> 10013317$Lipid metabolism disorders$$$$$$$$
> 10013326$Menstrual cycle and uterine bleeding disorders$$$$$$$$
> 10013355$Penile and scrotal disorders (excl infections and
> inflammations)$$$$$$$$

And the hierarchy is described in mdhier.asc, for example:


> 10027730$10027723$10046973$10007541$Mitral valve prolapse$Mitral valvular
> disorders$Cardiac valve disorders$Cardiac disorders$Card$$10007541$Y$

I.e. the code for LLT  "Mitral valve prolapse" is 10027730, the code for HLT
"Mitral valvular disorders" is 10027730, the code for HGLT "Cardiac valve
disorders" is 10046973 and the code for SOC "Cardiac disorders" is 10007541.
There seems to be an SOC abbreviation specified also, "Card".
