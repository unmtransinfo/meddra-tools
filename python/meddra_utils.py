#!/usr/bin/env python
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
###
#############################################################################
### Legacy fields removed from v15.0+: costart, who-art, icd-9, icd-0-cm,
### icd-10, harts, j-art.
#############################################################################
### Jeremy Yang
###  9 May 2016
#############################################################################
import os,sys,re,getopt
import pgdb

#############################################################################
def ConvertSoc(fin,fout,verbose):
  '''input: soc.asc, table: soc'''
  fout.write("id\ttext\tabbr\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)!=3:
      print >>sys.stderr, "Bad line: %s"%line
      continue
    soc_id=int(fields[0])
    txt=fields[1]
    txt=re.sub(r'\t',' ',txt)
    abr=fields[2]
    fout.write("%d"%soc_id)
    fout.write("\t%s"%txt)
    fout.write("\t%s\n"%abr)
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertHlt(fin,fout,verbose):
  '''input: hlt.asc, table: hlt'''
  fout.write('id\ttext\n')
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)<2:
      print >>sys.stderr, "ERROR: Bad line: %s"%line
      continue
    elif len(fields)>2:
      print >>sys.stderr, "Warning: Non-compliant line: %s"%line

    hlt_id=int(fields[0])
    txt=fields[1]
    txt=re.sub(r'\t',' ',txt)
    fout.write("%d\t%s\n"%(hlt_id,txt))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertHlgt(fin,fout,verbose):
  '''input: hlgt.asc, table: hlgt'''
  fout.write("id\ttext\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)!=2:
      print >>sys.stderr, "Bad line: %s"%line
      continue
    soc_id=int(fields[0])
    txt=fields[1]
    txt=re.sub(r'\t',' ',txt)
    fout.write('%d\t%s\n'%(soc_id,txt))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertPt(fin,fout,verbose):
  '''input: pt.asc, table: pt'''
  fout.write("id\ttext\tsoc\twhoart\thart\tcostart\ticd9\ticd9cm\tjart\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)<2:
      print >>sys.stderr, "Bad line: %s"%line
      continue
    pt_id=int(fields[0])
    txt=fields[1]
    txt=re.sub(r'\t',' ',txt)
    soc=int(fields[3]) if len(fields)>3 else None
    whoart=fields[4] if len(fields)>4 else None
    harts=fields[5] if len(fields)>5 else None
    costart=fields[6] if len(fields)>6 else None
    icd9=fields[7] if len(fields)>7 else None
    icd9cm=fields[8] if len(fields)>8 else None
    jart=fields[10] if len(fields)>10 else None
    fout.write("%d"%pt_id)
    fout.write("\t%s"%txt)
    fout.write("\t%d"%(soc if soc else ''))
    fout.write("\t%s"%(whoart if whoart else ''))
    fout.write("\t%s"%(harts if harts else ''))
    fout.write("\t%s"%(costart if costart else ''))
    fout.write("\t%s"%(icd9 if icd9 else ''))
    fout.write("\t%s"%(icd9cm if icd9cm else ''))
    fout.write("\t%s\n"%(jart if jart else ''))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertLlt(fin,fout,verbose):
  '''input: llt.asc, table: llt'''
  fout.write("id\ttext\tpt\twhoart\tcostart\ticd9cm\tcurrent\tjart\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)<2:
      print >>sys.stderr, "Bad line: %s"%line
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
    fout.write("%d"%llt_id)
    fout.write("\t%s"%txt)
    fout.write("\t%s"%(str(pt) if pt else ''))
    fout.write("\t%s"%(whoart if whoart else ''))
    fout.write("\t%s"%(costart if costart else ''))
    fout.write("\t%s"%(icd9cm if icd9cm else ''))
    fout.write("\t%s"%(current if current else ''))
    fout.write("\t%s\n"%(jart if jart else ''))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertLlt2pt(fin,fout,verbose):
  '''input: llt.asc, table: pt2llt'''
  fout.write("pt_id\tllt_id\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)<2:
      print >>sys.stderr, "Bad line: %s"%line
      continue
    llt_id=int(fields[0])
    pt=int(fields[2]) if len(fields)>2 else None
    if pt:
      fout.write("%d\t%d\n"%(pt,llt_id))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertSoc2hlgt(fin,fout,verbose):
  '''input: soc_hlgt.asc, table:soc2hlgt'''
  fout.write("soc_id\thlgt_id\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)<2:
      print >>sys.stderr, "Bad line: %s"%line
      continue
    fout.write("%s\t%s\n"%(fields[0],fields[1]))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertHlgt2Hlt(fin,fout,verbose):
  '''input: hlgt_hlt.asc, table:hlgt2hlt'''
  fout.write("hlgt_id\thlt_id\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)<2:
      print >>sys.stderr, "Bad line: %s"%line
      continue
    fout.write("%s\t%s\n"%(fields[0],fields[1]))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertHlt2Pt(fin,fout,verbose):
  '''input: hlt_pt.asc, table:hlt2pt'''
  fout.write("hlt_id\tpt_id\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)<2:
      print >>sys.stderr, "Bad line: %s"%line
      continue
    fout.write("%s\t%s\n"%(fields[0],fields[1]))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertSoc2intl(fin,fout,verbose):
  '''input: intl_ord.asc, table: soc2intl'''
  fout.write("intl_ord_code\tsoc_code\n")
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    fields=re.split('\$',line)
    if len(fields)<2:
      print >>sys.stderr, "Bad line: %s"%line
      continue
    fout.write("%s\t%s\n"%(fields[0],fields[1]))
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertSmqlist(fin,fout,verbose):
  tags=['smq_code', 'smq_name', 'smq_level', 'smq_description', 'smq_source',
	'smq_note', 'meddra_version', 'status', 'smq_algorithm']
  fout.write('\t'.join(tags)+'\n')
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    line=re.sub('\t',' ',line)
    fields=re.split('\$',line)
    fout.write('\t'.join(fields)+'\n')
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines

#############################################################################
def ConvertSmqcontent(fin,fout,verbose):
  tags=['smq_code','term_code','term_level','term_scope','term_category',
	'term_weight','term_status','term_addition_version','term_last_modified_version']
  fout.write('\t'.join(tags)+'\n')
  n_lines=0
  while True:
    line=fin.readline()
    if not line: break
    line=line.strip()
    if not line or line[0]=='#': continue
    line=re.sub('\$+$','',line)
    line=re.sub('\t',' ',line)
    fields=re.split('\$',line)
    fout.write('\t'.join(fields)+'\n')
    n_lines+=1
  print >>sys.stderr, "lines: %d"%n_lines


#############################################################################
###
#Db functions:
###
#############################################################################
def Connect():
  db=pgdb.connect(dsn='localhost:meddra:www:foobar')
  cur=db.cursor()
  return db,cur

#############################################################################
def DescribeCounts():
  outtxt=""
  db,cur = Connect()
  sql=("select table_name from information_schema.tables where table_schema='public'")
  cur.execute(sql)
  rows=cur.fetchall()
  outtxt+=("tables:\n")
  for row in rows:
    tablename=row[0]
    sql=("select count(*) from %s"%tablename)
    cur.execute(sql)
    rows=cur.fetchall()
    outtxt+="count(%s): %d\n"%(tablename,rows[0][0])
  cur.close()
  db.close()
  return outtxt
  
#############################################################################
def DescribeDB():
  outtxt=DescribeCounts()
  db,cur = Connect()
  sql=("select table_name from information_schema.tables where table_schema='public'")
  cur.execute(sql)
  rows=cur.fetchall()
  for row in rows:
    tablename=row[0]
    sql=("select column_name,data_type from information_schema.columns where table_name = '%s'"%tablename)
    cur.execute(sql)
    rows=cur.fetchall()
    outtxt+=("table: %s\n"%tablename)
    for row in rows:
      outtxt+=("\t%s\n"%str(row))
  cur.close()
  db.close()
  return outtxt

#############################################################################
def GetMetadata():
  ver,desc,ts =( None,None,None)
  db,cur = Connect()
  sql=("select db_version,db_description,db_date_built from metadata")
  cur.execute(sql)
  rows=cur.fetchall()
  if rows and len(rows[0])>2:
    ver=rows[0][0]
    desc=rows[0][1]
    ts=rows[0][2]
  cur.close()
  db.close()
  return ver,desc,ts

#############################################################################
def SocID2HlgtIDs(socid):
  hlgtids=[]
  db,cur = Connect()
  sql=("SELECT hlgt_id FROM soc2hlgt WHERE soc_id='%s'"%socid)
  cur.execute(sql)
  rows=cur.fetchall()
  cur.close()
  db.close()
  for row in rows:
    hlgtids.append(row[0])
  return hlgtids

#############################################################################
def Lltsearch(qtxt):
  id,text,pt,whoart,costart,icd9cm,current,jart = \
  	None,None,None,None,None,None,None,None 
  db,cur = Connect()
  sql=("SELECT id,text,pt,whoart,costart,icd9cm,current,jart FROM llt WHERE text ILIKE '%s'"%qtxt)
  cur.execute(sql)
  rows=cur.fetchall()
  cur.close()
  db.close()
  return rows

#############################################################################
if __name__=='__main__':

  PROG=os.path.basename(sys.argv[0])
  usage='''\
%(PROG)s - 

operations:
	--dbdescribe ................ 
	--convert_soc ............... from soc.asc
	--convert_hlt ............... from hlt.asc
	--convert_hlgt .............. from hlgt.asc
	--convert_pt ................ from pt.asc
	--convert_llt ............... from llt.asc
	--convert_llt2pt ............ from llt.asc
	--convert_soc2hlgt ..........
	--convert_hlgt2hlt ..........
	--convert_hlt2pt ............
	--convert_soc2intl .......... from intl_ord.asc
	--convert_smq_list .......... from smq_list.asc
	--convert_smq_content ....... from smq_content.asc
I/O:
	--i IFILE ................... input file (*.asc)
	--o OFILE ................... output file
options:
	--v[v[v]] ................... verbose [very [very]]
	--h ......................... this help
'''%{	'PROG':PROG
	}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  ifile=None;
  ofile=None;
  dbdescribe=False; 
  convert_soc=False;
  convert_hlt=False;
  convert_hlgt=False;
  convert_pt=False;
  convert_llt=False;
  convert_llt2pt=False;
  convert_soc2hlgt=False;
  convert_hlgt2hlt=False;
  convert_hlt2pt=False;
  convert_soc2intl=False;
  convert_intl=False;
  convert_smq_list=False;
  convert_smq_content=False;
  verbose=0;
  opts,pargs=getopt.getopt(sys.argv[1:],'',[
	'i=','o=',
	'dbdescribe',
	'convert_soc',
	'convert_hlt',
	'convert_hlgt',
	'convert_pt',
	'convert_llt',
	'convert_llt2pt',
	'convert_soc2hlgt',
	'convert_hlgt2hlt',
	'convert_hlt2pt',
	'convert_soc2intl',
	'convert_intl',
	'convert_smq_list',
	'convert_smq_content',
	'v','vv','vvv','help'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--help': ErrorExit(usage)
    elif opt=='--dbdescribe': dbdescribe=True
    elif opt=='--convert_soc': convert_soc=True
    elif opt=='--convert_hlt': convert_hlt=True
    elif opt=='--convert_hlgt': convert_hlgt=True
    elif opt=='--convert_pt': convert_pt=True
    elif opt=='--convert_llt': convert_llt=True
    elif opt=='--convert_llt2pt': convert_llt2pt=True
    elif opt=='--convert_soc2hlgt': convert_soc2hlgt=True
    elif opt=='--convert_hlgt2hlt': convert_hlgt2hlt=True
    elif opt=='--convert_hlt2pt': convert_hlt2pt=True
    elif opt=='--convert_soc2intl': convert_soc2intl=True
    elif opt=='--convert_intl': convert_intl=True
    elif opt=='--convert_smq_list': convert_smq_list=True
    elif opt=='--convert_smq_content': convert_smq_content=True
    elif opt=='--i': ifile=val
    elif opt=='--o': ofile=val
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s\n%s'%(opt,usage))

  fin=open(ifile) if ifile else None

  if ofile:
    fout=fout=open(ofile,"w")
    if not fout: ErrorExit('ERROR: cannot open outfile: %s'%ofile)
  else:
    fout=sys.stdout

  if convert_soc:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertSoc(fin,fout,verbose)
  elif convert_hlt:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertHlt(fin,fout,verbose)
  elif convert_hlgt:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertHlgt(fin,fout,verbose)
  elif convert_pt:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertPt(fin,fout,verbose)
  elif convert_llt:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertLlt(fin,fout,verbose)
  elif convert_llt2pt:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertLlt2pt(fin,fout,verbose)
  elif convert_soc2hlgt:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertSoc2hlgt(fin,fout,verbose)
  elif convert_hlgt2hlt:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertHlgt2Hlt(fin,fout,verbose)
  elif convert_hlt2pt:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertHlt2Pt(fin,fout,verbose)

  elif convert_soc2intl:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertSoc2intl(fin,fout,verbose)

  elif convert_smq_list:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertSmqlist(fin,fout,verbose)

  elif convert_smq_content:
    if not fin: ErrorExit('ERROR: input file required.')
    ConvertSmqcontent(fin,fout,verbose)


  elif dbdescribe:
    print DescribeDB()
    ver,desc,ts = GetMetadata()
    print "Version:",ver
    print "Description:",desc
    print "Timestamp:",ts

  else:
    ErrorExit('No operation specified.')

  fout.close()

