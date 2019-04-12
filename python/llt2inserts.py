#!/usr/bin/env python
#############################################################################
### llt2inserts.py -- MedDRA raw input; PostgreSQL output.
### 
### Revised for MedDRA 14.0.
### Relies on format of raw ascii files.
### 
### Jeremy Yang
### 29 Mar 2011
#############################################################################
import sys,os,re

PROG=os.path.basename(sys.argv[0])

if len(sys.argv)<3:
  print "syntax: %s <DATAFILE> <INSERTSQL>"%(PROG)
  sys.exit()

fin=file(sys.argv[1])
fout=file(sys.argv[2],"w")

maxlens={'whoart':0,'costart':0,'icd9cm':0,'jart':0}

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

  id=int(fields[0])
  txt=fields[1]
  txt=re.sub(r"'","\\'",txt)
  
  pt,whoart,costart,icd9cm,current,jart = None,None,None,None,None,None

  if len(fields)>2:
    pt=int(fields[2])
  if len(fields)>3:
    whoart=fields[3]
    if len(whoart)>maxlens['whoart']: maxlens['whoart']=len(whoart)
  if len(fields)>5:
    costart=fields[5]
    if len(costart)>maxlens['costart']: maxlens['costart']=len(costart)
  if len(fields)>7:
    icd9cm=fields[7]
    if len(icd9cm)>maxlens['icd9cm']: maxlens['icd9cm']=len(icd9cm)
  if len(fields)>9:
    if fields[9]=='Y': current='TRUE'
    else: current='FALSE'
  if len(fields)>10:
    jart=fields[10]
    if len(jart)>maxlens['jart']: maxlens['jart']=len(jart)
  fout.write("INSERT INTO llt VALUES\n")
  fout.write("\t(%d,\n"%id)
  fout.write("\tE'%s',\n"%txt)
  if pt: fout.write("\t%d,\n"%pt)
  else:  fout.write("\tNULL,\n")
  if whoart: fout.write("\t'%s',\n"%whoart)
  else:     fout.write("\tNULL,\n")
  if costart: fout.write("\t'%s',\n"%costart)
  else:       fout.write("\tNULL,\n")
  if icd9cm: fout.write("\t'%s',\n"%icd9cm)
  else:      fout.write("\tNULL,\n")
  if current: fout.write("\t%s,\n"%current)
  else:       fout.write("\tNULL,\n")
  if jart: fout.write("\t'%s');\n"%jart)
  else:    fout.write("\tNULL);\n")
  if pt:
    fout.write("INSERT INTO pt2llt VALUES (%d,%d);\n"%(pt,id))
  n_lines+=1

fout.close()
for key,maxlen in maxlens.items():
  print >>sys.stderr, "maxlen[%s]: %d"%(key,maxlen)

print >>sys.stderr, "lines converted to inserts: %d"%n_lines
