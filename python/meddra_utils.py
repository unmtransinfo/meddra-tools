#!/usr/bin/env python3
#############################################################################
### meddra_utils.py - meddra utility functions
###
### (1) Raw ascii file to CSV converters.
### (2) Db access utils (local Pg edition).
###
### SOC = System Organ Class
### LLT = Low Level Term
### HLT = High Level Term
### HLGT = High Level Group Term
### PT = Preferred Term
### SMQ = Standard Meddra Query
#############################################################################
### Legacy fields removed from v15.0+: costart, who-art, icd-9, icd-0-cm,
### icd-10, harts, j-art.
#############################################################################
import os,sys,re,argparse,logging

import psycopg2 as pg

#############################################################################
def ConvertSoc(fin, fout):
  '''input: soc.asc, table: soc'''
  fout.write("id\ttext\tabbr\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$','', line)
    fields=re.split(r'\$', line)
    if len(fields)!=3:
      logging.error(f"Bad line: {line}")
      continue
    soc_id=int(fields[0])
    txt=fields[1]
    txt=re.sub(r'\t', ' ', txt)
    abr=fields[2]
    fout.write(f"{soc_id}")
    fout.write(f"\t{txt}")
    fout.write(f"\t{abr}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertHlt(fin, fout):
  '''input: hlt.asc, table: hlt'''
  fout.write('id\ttext\n')
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)<2:
      logging.error(f"Bad line: {line}")
      continue
    elif len(fields)>2:
      logging.warning(f"Non-compliant line: {line}")
    hlt_id=int(fields[0])
    txt=fields[1]
    txt=re.sub(r'\t', ' ', txt)
    fout.write(f"{hlt_id}\t{txt}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertHlgt(fin, fout):
  '''input: hlgt.asc, table: hlgt'''
  fout.write("id\ttext\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)!=2:
      logging.error(f"Bad line: {line}")
      continue
    soc_id=int(fields[0])
    txt=fields[1]
    txt=re.sub(r'\t', ' ', txt)
    fout.write(f'{soc_id}\t{txt}\n')
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertPt(fin, fout):
  '''input: pt.asc, table: pt'''
  fout.write("id\ttext\tsoc\twhoart\thart\tcostart\ticd9\ticd9cm\tjart\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)<2:
      logging.error(f"Bad line: {line}")
      continue
    pt_id=int(fields[0])
    txt=fields[1]
    txt=re.sub(r'\t', ' ', txt)
    soc=int(fields[3]) if len(fields)>3 else None
    whoart=fields[4] if len(fields)>4 else None
    harts=fields[5] if len(fields)>5 else None
    costart=fields[6] if len(fields)>6 else None
    icd9=fields[7] if len(fields)>7 else None
    icd9cm=fields[8] if len(fields)>8 else None
    jart=fields[10] if len(fields)>10 else None
    fout.write(f"{pt_id}")
    fout.write(f"\t{txt}")
    fout.write(f"\t{soc if soc else ''}")
    fout.write(f"\t{whoart if whoart else ''}")
    fout.write(f"\t{harts if harts else ''}")
    fout.write(f"\t{costart if costart else ''}")
    fout.write(f"\t{icd9 if icd9 else ''}")
    fout.write(f"\t{icd9cm if icd9cm else ''}")
    fout.write(f"\t{jart if jart else ''}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertLlt(fin, fout):
  '''input: llt.asc, table: llt'''
  fout.write("id\ttext\tpt\twhoart\tcostart\ticd9cm\tcurrent\tjart\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)<2:
      logging.error(f"Bad line: {line}")
      continue
    llt_id=int(fields[0])
    txt=fields[1]
    current = None
    pt=int(fields[2]) if len(fields)>2 else None
    whoart=fields[3] if len(fields)>3 else None
    costart=fields[5] if len(fields)>5 else None
    icd9cm=fields[7] if len(fields)>7 else None
    if len(fields)>9:
      current='TRUE' if fields[9]=='Y' else 'FALSE'
    jart=fields[10] if len(fields)>10 else None
    fout.write(f"{llt_id}")
    fout.write(f"\t{txt}")
    fout.write(f"\t{str(pt) if pt else ''}")
    fout.write(f"\t{whoart if whoart else ''}")
    fout.write(f"\t{costart if costart else ''}")
    fout.write(f"\t{icd9cm if icd9cm else ''}")
    fout.write(f"\t{current if current else ''}")
    fout.write(f"\t{jart if jart else ''}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertLlt2pt(fin, fout):
  '''input: llt.asc, table: pt2llt'''
  fout.write("pt_id\tllt_id\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)<2:
      logging.error(f"Bad line: {line}")
      continue
    llt_id=int(fields[0])
    pt=int(fields[2]) if len(fields)>2 else None
    if pt:
      fout.write(f"{pt}\t{llt_id}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertSoc2hlgt(fin, fout):
  '''input: soc_hlgt.asc, table:soc2hlgt'''
  fout.write("soc_id\thlgt_id\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)<2:
      logging.error(f"Bad line: {line}")
      continue
    fout.write(f"{fields[0]}\t{fields[1]}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertHlgt2Hlt(fin, fout):
  '''input: hlgt_hlt.asc, table:hlgt2hlt'''
  fout.write("hlgt_id\thlt_id\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)<2:
      logging.error(f"Bad line: {line}")
      continue
    fout.write(f"{fields[0]}\t{fields[1]}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertHlt2Pt(fin, fout):
  '''input: hlt_pt.asc, table:hlt2pt'''
  fout.write("hlt_id\tpt_id\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)<2:
      logging.error(f"Bad line: {line}")
      continue
    fout.write(f"{fields[0]}\t{fields[1]}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertSoc2intl(fin, fout):
  '''input: intl_ord.asc, table: soc2intl'''
  fout.write("intl_ord_code\tsoc_code\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    fields=re.split(r'\$', line)
    if len(fields)<2:
      logging.error(f"Bad line: {line}")
      continue
    fout.write(f"{fields[0]}\t{fields[1]}\n")
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertSmqlist(fin, fout):
  tags=['smq_code', 'smq_name', 'smq_level', 'smq_description', 'smq_source',
	'smq_note', 'meddra_version', 'status', 'smq_algorithm']
  fout.write('\t'.join(tags)+'\n')
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    line=re.sub('\t', ' ', line)
    fields=re.split(r'\$', line)
    fout.write('\t'.join(fields)+'\n')
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
def ConvertSmqcontent(fin, fout):
  tags=['smq_code','term_code','term_level','term_scope','term_category',
	'term_weight','term_status','term_addition_version','term_last_modified_version']
  fout.write('\t'.join(tags)+'\n')
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub(r'\$+$', '', line)
    line=re.sub('\t', ' ', line)
    fields=re.split(r'\$', line)
    fout.write('\t'.join(fields)+'\n')
    n_lines+=1
  logging.info(f"lines: {n_lines}")

#############################################################################
### Db functions:
#############################################################################
def Connect():
  db = pg.connect(dbname='meddra', user='www', password='foobar')
  cur = db.cursor()
  return db,cur

#############################################################################
def DescribeDB():
  outtxt="";
  db,cur = Connect()
  sql = ("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
  cur.execute(sql)
  rows = cur.fetchall()
  for row in rows:
    tablename = row[0]
    sql = (f"SELECT COUNT(*) FROM {tablename}")
    cur.execute(sql)
    rows = cur.fetchall()
    outtxt += (f"table: {tablename}\n")
    outtxt += f"\tROWCOUNT: {rows[0][0]:6d}\n"
    sql = (f"SELECT column_name,data_type FROM information_schema.columns WHERE table_name = '{tablename}'")
    cur.execute(sql)
    rows = cur.fetchall()
    for j,row in enumerate(rows):
      outtxt += (f"\t{j+1}. {row[0]:<12} ({row[1]})\n")
  cur.close()
  db.close()
  return outtxt

#############################################################################
def SocID2HlgtIDs(socid):
  hlgtids=[]
  db,cur = Connect()
  sql=(f"SELECT hlgt_id FROM soc2hlgt WHERE soc_id='{socid}'")
  cur.execute(sql)
  rows=cur.fetchall()
  cur.close()
  db.close()
  for row in rows:
    hlgtids.append(row[0])
  return hlgtids

#############################################################################
def Lltsearch(qtxt):
  db,cur = Connect()
  sql=(f"SELECT id,text,pt,whoart,costart,icd9cm,current,jart FROM llt WHERE text ILIKE '{qtxt}'")
  cur.execute(sql)
  rows=cur.fetchall()
  cur.close()
  db.close()
  return rows

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="MedDRA file and db utilites", epilog='')
  ops = [
	"dbdescribe", # 
	"convert_soc", # from soc.asc
	"convert_hlt", # from hlt.asc
	"convert_hlgt", # from hlgt.asc
	"convert_pt", # from pt.asc
	"convert_llt", # from llt.asc
	"convert_llt2pt", # from llt.asc
	"convert_soc2hlgt", #
	"convert_hlgt2hlt", #
	"convert_hlt2pt", #
	"convert_soc2intl", # from intl_ord.asc
	"convert_smq_list", # from smq_list.asc
	"convert_smq_content" # from smq_content.asc
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", help="input file (.asc)")
  parser.add_argument("--o", dest="ofile", help="output")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  fin = open(args.ifile) if args.ifile else None
  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  if args.op=="dbdescribe":
    print(DescribeDB())
    sys.exit()

  if not fin: parser.error('Input file required.')

  logging.info(f"CONVERTING INPUT: {args.ifile}; OUTPUT: {args.ofile if args.ofile else 'STDOUT'}")

  if args.op=="convert_soc":
    ConvertSoc(fin, fout)
  elif args.op=="convert_hlt":
    ConvertHlt(fin, fout)
  elif args.op=="convert_hlgt":
    ConvertHlgt(fin, fout)
  elif args.op=="convert_pt":
    ConvertPt(fin, fout)
  elif args.op=="convert_llt":
    ConvertLlt(fin, fout)
  elif args.op=="convert_llt2pt":
    ConvertLlt2pt(fin, fout)
  elif args.op=="convert_soc2hlgt":
    ConvertSoc2hlgt(fin, fout)
  elif args.op=="convert_hlgt2hlt":
    ConvertHlgt2Hlt(fin, fout)
  elif args.op=="convert_hlt2pt":
    ConvertHlt2Pt(fin, fout)
  elif args.op=="convert_soc2intl":
    ConvertSoc2intl(fin, fout)
  elif args.op=="convert_smq_list":
    ConvertSmqlist(fin, fout)
  elif args.op=="convert_smq_content":
    ConvertSmqcontent(fin, fout)
  else:
    parser.error(f"Invalid operation: {args.op}")

