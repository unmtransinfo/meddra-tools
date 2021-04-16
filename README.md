# MedDRA Tools

Includes scripts and code to build local PostgreSql db from raw MedDRA files.

* <https://meddra.com/>
* MedDRA is regularly updated, &gt;1/year.
* Latest at time of this writing: v24.0 (March 2021).

(Download credentials required, via MedDRA subscription.)

MedDRA = Medical Dictionary for Regulatory Activities
MSSO = Maintenance and Support Services Organization
COSTAR(T) = Computer-Stored Ambulatory Record (Term)

Hierarchy of terms (descending order):

	SOC = System Organ Class
	HLGT = High Level Group Term
	HLT = High Level Term
	PT = Preferred Term
	LLT = Lowest Level Term

System Organ Classes:

	Blood and lymphatic system disorders
	Cardiac disorders
	Congenital, familial and genetic disorders
	Ear and labyrinth disorders
	Endocrine disorders
	Eye disorders
	Gastrointestinal disorders
	General disorders and administration site conditions
	Hepatobiliary disorders
	Immune system disorders
	Infections and infestations
	Injury, poisoning and procedural complications
	Investigations
	Metabolism and nutrition disorders
	Musculoskeletal and connective tissue disorders
	Neoplasms benign, malignant and unspecified (incl cysts and polyps)
	Nervous system disorders
	Pregnancy, puerperium and perinatal conditions
	Psychiatric disorders
	Renal and urinary disorders
	Reproductive system and breast disorders
	Respiratory, thoracic and mediastinal disorders
	Skin and subcutaneous tissue disorders
	Social circumstances
	Surgical and medical procedures
	Vascular disorders
	Product issues


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
