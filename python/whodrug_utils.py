#!/usr/bin/env python3
#############################################################################
### whodrug_utils.py - WHODrug C3 utility functions
###
### CSV to TSV converters for WHODrug Global C3 format.
###
### MP = Medicinal Products (main table)
### ThG = Therapeutic Groups (ATC assignments)
### ING = Ingredients
### SUN = Substances
### ATC = Anatomical Therapeutic Chemical classification
### PF = Pharmaceutical Forms
### STR = Strengths
### ORG = Organizations
### SRCE = Sources/References
### CCODE = Country Codes
### PRT = Product Types
### UNIT = Units of measurement
#############################################################################
import sys,re,csv,argparse,logging

#############################################################################
def _convert_csv(fin, fout, tags, expected_cols, table_name, progress_every=0):
  '''Generic CSV to TSV converter for WHODrug C3 files.'''
  fout.write('\t'.join(tags)+'\n')
  reader = csv.reader(fin)
  n_lines=0
  n_errors=0
  for row in reader:
    if len(row)!=expected_cols:
      logging.error(f"[{table_name}] Bad line ({len(row)} fields, expected {expected_cols}): {str(row[:3])[:80]}...")
      n_errors+=1
      continue
    cleaned = [re.sub(r'\t', ' ', f) for f in row]
    fout.write('\t'.join(cleaned)+'\n')
    n_lines+=1
    if progress_every and n_lines % progress_every == 0:
      logging.info(f"[{table_name}] {n_lines:,} lines processed")
  logging.info(f"[{table_name}] total: {n_lines:,} lines ({n_errors} errors)")

#############################################################################
def ConvertMP(fin, fout):
  '''input: MP.csv (22 fields), table: mp'''
  tags = ['record_id', 'umc_product_id', 'drug_rec_no', 'seq1', 'seq2',
          'seq3', 'seq4', 'substance_or_synonym', 'drug_name', 'name_specifier',
          'ma_number', 'ma_date', 'ma_withdrawal_date', 'country', 'company',
          'ma_holder', 'reference_code', 'source_country', 'year_of_reference',
          'product_type', 'create_date', 'date_changed']
  _convert_csv(fin, fout, tags, 22, 'mp', progress_every=1000000)

#############################################################################
def ConvertThG(fin, fout):
  '''input: ThG.csv (5 fields), table: thg'''
  tags = ['therapgroup_id', 'atc_code', 'create_date', 'official_atc_code', 'record_id']
  _convert_csv(fin, fout, tags, 5, 'thg', progress_every=1000000)

#############################################################################
def ConvertING(fin, fout):
  '''input: ING.csv (7 fields), table: ing'''
  tags = ['ingredient_id', 'create_date', 'substance_id', 'quantity', 'quantity_2', 'unit', 'record_id']
  _convert_csv(fin, fout, tags, 7, 'ing', progress_every=1000000)

#############################################################################
def ConvertSUN(fin, fout):
  '''input: SUN.csv (6 fields), table: sun'''
  tags = ['substance_id', 'cas_number', 'language_code', 'substance_name', 'year_of_reference', 'reference_code']
  _convert_csv(fin, fout, tags, 6, 'sun')

#############################################################################
def ConvertATC(fin, fout):
  '''input: ATC.csv (3 fields), table: atc'''
  tags = ['atc_code', 'level', 'text']
  _convert_csv(fin, fout, tags, 3, 'atc')

#############################################################################
def ConvertPF(fin, fout):
  '''input: PF.csv (2 fields), table: pf'''
  tags = ['pharmform_id', 'text']
  _convert_csv(fin, fout, tags, 2, 'pf')

#############################################################################
def ConvertSTR(fin, fout):
  '''input: STR.csv (2 fields), table: str'''
  tags = ['strength_id', 'text']
  _convert_csv(fin, fout, tags, 2, 'str')

#############################################################################
def ConvertORG(fin, fout):
  '''input: ORG.csv (3 fields), table: org'''
  tags = ['organization_id', 'name', 'country_code']
  _convert_csv(fin, fout, tags, 3, 'org')

#############################################################################
def ConvertSRCE(fin, fout):
  '''input: SRCE.csv (3 fields), table: srce'''
  tags = ['reference_code', 'reference', 'country_code']
  _convert_csv(fin, fout, tags, 3, 'srce')

#############################################################################
def ConvertCCODE(fin, fout):
  '''input: CCODE.csv (2 fields), table: ccode'''
  tags = ['country_code', 'country_name']
  _convert_csv(fin, fout, tags, 2, 'ccode')

#############################################################################
def ConvertPRT(fin, fout):
  '''input: PRT.csv (2 fields), table: prt'''
  tags = ['prodtype_id', 'text']
  _convert_csv(fin, fout, tags, 2, 'prt')

#############################################################################
def ConvertUNIT(fin, fout):
  '''input: UNIT.csv (2 fields), table: unit'''
  tags = ['unit_id', 'text']
  _convert_csv(fin, fout, tags, 2, 'unit')

#############################################################################
def ConvertVersion(fin, fout):
  '''input: Version.csv (2 fields), table: version'''
  tags = ['description', 'short_name']
  _convert_csv(fin, fout, tags, 2, 'version')

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(
    description="WHODrug C3 CSV to TSV converters",
    epilog="Example: whodrug_utils.py convert_mp --i data/WHODrugC3/MP.csv --o data/whodrug_mp.tsv")
  ops = [
    "convert_mp",
    "convert_thg",
    "convert_ing",
    "convert_sun",
    "convert_atc",
    "convert_pf",
    "convert_str",
    "convert_org",
    "convert_srce",
    "convert_ccode",
    "convert_prt",
    "convert_unit",
    "convert_version",
  ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input CSV file")
  parser.add_argument("--o", dest="ofile", help="output TSV file")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s: %(message)s',
    level=logging.DEBUG if args.verbose > 0 else logging.INFO)

  fin = open(args.ifile, encoding='utf-8') if args.ifile else None
  fout = open(args.ofile, "w", encoding='utf-8') if args.ofile else sys.stdout

  if not fin: parser.error('Input file required.')

  logging.info(f"CONVERTING INPUT: {args.ifile}; OUTPUT: {args.ofile if args.ofile else 'STDOUT'}")

  op_map = {
    "convert_mp": ConvertMP,
    "convert_thg": ConvertThG,
    "convert_ing": ConvertING,
    "convert_sun": ConvertSUN,
    "convert_atc": ConvertATC,
    "convert_pf": ConvertPF,
    "convert_str": ConvertSTR,
    "convert_org": ConvertORG,
    "convert_srce": ConvertSRCE,
    "convert_ccode": ConvertCCODE,
    "convert_prt": ConvertPRT,
    "convert_unit": ConvertUNIT,
    "convert_version": ConvertVersion,
  }
  op_map[args.op](fin, fout)
