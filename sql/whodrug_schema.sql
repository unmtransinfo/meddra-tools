-- WHODrug Global C3 Schema
-- 13 tables based on WHODrug C3 CSV format documentation
--
-- Reference tables (lookup, small):
--   ccode, srce, prt, unit, pf, str, org, atc, sun
-- Main table:
--   mp (Medicinal Products - ~5.6M rows)
-- Dependent tables (large, logical FK to mp):
--   thg (Therapeutic Groups - ~6M rows)
--   ing (Ingredients - ~9M rows)
-- Metadata:
--   version

-- === Reference tables ===

CREATE TABLE ccode (
  country_code VARCHAR(10) PRIMARY KEY,
  country_name VARCHAR(80) NOT NULL
);

CREATE TABLE srce (
  reference_code VARCHAR(10) PRIMARY KEY,
  reference VARCHAR(80) NOT NULL,
  country_code VARCHAR(10)
);

CREATE TABLE prt (
  prodtype_id VARCHAR(10) PRIMARY KEY,
  text VARCHAR(80) NOT NULL
);

CREATE TABLE unit (
  unit_id VARCHAR(10) PRIMARY KEY,
  text VARCHAR(40) NOT NULL
);

CREATE TABLE pf (
  pharmform_id VARCHAR(10) PRIMARY KEY,
  text VARCHAR(80) NOT NULL
);

CREATE TABLE str (
  strength_id VARCHAR(10) PRIMARY KEY,
  text VARCHAR(500) NOT NULL
);

CREATE TABLE org (
  organization_id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  country_code VARCHAR(10)
);

CREATE TABLE atc (
  atc_code VARCHAR(10) PRIMARY KEY,
  level VARCHAR(1) NOT NULL,
  text VARCHAR(110) NOT NULL
);

CREATE TABLE sun (
  substance_id VARCHAR(10) PRIMARY KEY,
  cas_number VARCHAR(10),
  language_code VARCHAR(10),
  substance_name VARCHAR(250) NOT NULL,
  year_of_reference VARCHAR(3),
  reference_code VARCHAR(10)
);

-- === Main table ===

CREATE TABLE mp (
  record_id VARCHAR(10) PRIMARY KEY,
  umc_product_id VARCHAR(22),
  drug_rec_no VARCHAR(6) NOT NULL,
  seq1 VARCHAR(2) NOT NULL,
  seq2 VARCHAR(3) NOT NULL,
  seq3 VARCHAR(10),
  seq4 VARCHAR(10),
  substance_or_synonym VARCHAR(1),
  drug_name VARCHAR(1500) NOT NULL,
  name_specifier VARCHAR(30),
  ma_number VARCHAR(30),
  ma_date VARCHAR(8),
  ma_withdrawal_date VARCHAR(8),
  country VARCHAR(10),
  company VARCHAR(10),
  ma_holder VARCHAR(10),
  reference_code VARCHAR(10),
  source_country VARCHAR(10),
  year_of_reference VARCHAR(3),
  product_type VARCHAR(10),
  create_date VARCHAR(8),
  date_changed VARCHAR(8)
);

-- === Dependent tables (no explicit FK for import performance) ===

CREATE TABLE thg (
  therapgroup_id VARCHAR(10) PRIMARY KEY,
  atc_code VARCHAR(10) NOT NULL,
  create_date VARCHAR(8),
  official_atc_code VARCHAR(1),
  record_id VARCHAR(10) NOT NULL
);

CREATE TABLE ing (
  ingredient_id VARCHAR(10) PRIMARY KEY,
  create_date VARCHAR(8),
  substance_id VARCHAR(10) NOT NULL,
  quantity VARCHAR(15),
  quantity_2 VARCHAR(15),
  unit VARCHAR(10),
  record_id VARCHAR(10) NOT NULL
);

-- === Metadata ===

CREATE TABLE version (
  description VARCHAR(255) NOT NULL,
  short_name VARCHAR(50) NOT NULL
);
