#!/usr/bin/env python2
#############################################################################
### pt2inserts.py -- MedDRA raw input; PostgreSQL output.
###
### Relies on raw ascii format.
### OK for MedDRA 13.0 and 14.0.
#############################################################################
import sys,os,re

PROG=os.path.basename(sys.argv[0])

if len(sys.argv)<3:
  print "syntax: %s <DATAFILE> <INSERTSQL>"%(PROG)
  sys.exit()

fin=file(sys.argv[1])
fout=file(sys.argv[2],"w")

maxlens={'whoart':0,'harts':0,'costart':0,'icd9':0,'icd9cm':0,'jart':0}

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
  
  soc,whoart,harts,costart,icd9cm,icd9,jart = None,None,None,None,None,None,None

#   0        1          2  3        4       5      6         7     8     9  10
#   10002512$Anhidrosis$  $10040785$1298004$      $SWEAT DEC$705.0$705.0$  $236603$
#   id       txt           soc      whoart  harts  costart   icd   icdcm    jart

  if len(fields)>3:
    soc=int(fields[3])
  if len(fields)>4:
    whoart=fields[4]
    if len(whoart)>maxlens['whoart']: maxlens['whoart']=len(whoart)
  if len(fields)>5:
    harts=fields[5]
    if len(harts)>maxlens['harts']: maxlens['harts']=len(harts)
  if len(fields)>6:
    costart=fields[6]
    if len(costart)>maxlens['costart']: maxlens['costart']=len(costart)
  if len(fields)>7:
    icd9=fields[7]
    if len(icd9)>maxlens['icd9']: maxlens['icd9']=len(icd9)
  if len(fields)>8:
    icd9cm=fields[8]
    if len(icd9cm)>maxlens['icd9cm']: maxlens['icd9cm']=len(icd9cm)
  if len(fields)>10:
    jart=fields[10]
    if len(jart)>maxlens['jart']: maxlens['jart']=len(jart)
  fout.write("INSERT INTO pt VALUES\n")
  fout.write("\t(%d,\n"%id)
  fout.write("\tE'%s',\n"%txt)
  if soc: fout.write("\t%d,\n"%soc)
  else:  fout.write("\tNULL,\n")
  if whoart: fout.write("\t'%s',\n"%whoart)
  else:     fout.write("\tNULL,\n")
  if harts: fout.write("\t'%s',\n"%harts)
  else:     fout.write("\tNULL,\n")
  if costart: fout.write("\t'%s',\n"%costart)
  else:       fout.write("\tNULL,\n")
  if icd9: fout.write("\t'%s',\n"%icd9)
  else:      fout.write("\tNULL,\n")
  if icd9cm: fout.write("\t'%s',\n"%icd9cm)
  else:      fout.write("\tNULL,\n")
  if jart: fout.write("\t'%s');\n"%jart)
  else:    fout.write("\tNULL);\n")
  n_lines+=1

fout.close()
for key,maxlen in maxlens.items():
  print >>sys.stderr, "maxlen[%s]: %d"%(key,maxlen)

print >>sys.stderr, "lines converted to inserts: %d"%n_lines
