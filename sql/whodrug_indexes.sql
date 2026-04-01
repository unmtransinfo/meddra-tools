-- WHODrug Global C3 Indexes
-- Created AFTER data load for better performance
--
-- Requires: CREATE EXTENSION pg_trgm (done in Go_whodrug_DbCreate.sh)

-- MP: drug name search (primary eCRF use case)
CREATE INDEX idx_mp_drug_name_trgm ON mp USING gin(drug_name gin_trgm_ops);
CREATE INDEX idx_mp_drug_rec_no ON mp(drug_rec_no);
CREATE INDEX idx_mp_drug_rec_no_seq1 ON mp(drug_rec_no, seq1);
CREATE INDEX idx_mp_country ON mp(country);
CREATE INDEX idx_mp_product_type ON mp(product_type);

-- THG: join with mp and atc
CREATE INDEX idx_thg_record_id ON thg(record_id);
CREATE INDEX idx_thg_atc_code ON thg(atc_code);

-- ING: join with mp and sun
CREATE INDEX idx_ing_record_id ON ing(record_id);
CREATE INDEX idx_ing_substance_id ON ing(substance_id);

-- SUN: substance search
CREATE INDEX idx_sun_substance_name_trgm ON sun USING gin(substance_name gin_trgm_ops);
CREATE INDEX idx_sun_cas_number ON sun(cas_number);
