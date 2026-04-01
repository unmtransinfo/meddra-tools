-- WHODrug Global C3: Full hierarchical export
-- Product -> Ingredients -> Substances -> ATCs with all reference data
--
-- Usage: psql -d whodrug_2603 < sql/whodrug_full_export.sql

SELECT
  mp.record_id,
  mp.drug_name,
  mp.name_specifier,
  mp.drug_rec_no || mp.seq1 || mp.seq2 AS drug_code,
  mp.substance_or_synonym,
  ccode.country_name,
  prt.text AS product_type,
  pf.text AS pharmaceutical_form,
  str.text AS strength,
  org.name AS organization,
  sun.substance_name,
  sun.cas_number,
  ing.quantity,
  ing.quantity_2,
  unit.text AS unit,
  atc.atc_code,
  atc.text AS atc_text,
  atc.level AS atc_level,
  thg.official_atc_code
FROM mp
LEFT JOIN ccode ON mp.country = ccode.country_code
LEFT JOIN prt ON mp.product_type = prt.prodtype_id
LEFT JOIN pf ON mp.seq3 = pf.pharmform_id
LEFT JOIN str ON mp.seq4 = str.strength_id
LEFT JOIN org ON mp.ma_holder = org.organization_id
LEFT JOIN ing ON mp.record_id = ing.record_id
LEFT JOIN sun ON ing.substance_id = sun.substance_id
LEFT JOIN unit ON ing.unit = unit.unit_id
LEFT JOIN thg ON mp.record_id = thg.record_id
LEFT JOIN atc ON thg.atc_code = atc.atc_code
ORDER BY mp.drug_name, mp.record_id;
