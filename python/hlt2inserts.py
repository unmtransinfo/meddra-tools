#!/usr/bin/env python2
#############################################################################
### hlt2inserts.py -- MedDRA raw input; PostgreSQL output.
###
### In 14.1 there is one non-compliant line:
###	hlt.asc:10030209$Oesophageal varices$1036001$$HEM ESOPH$$$$$
### What are the 3rd/4th fields?  1036001 not present in any other .asc file.  What is "HEM ESOPH"?
#############################################################################
import sys,os,re

PROG=os.path.basename(sys.argv[0])

if len(sys.argv)<3:
  print "syntax: %s <DATAFILE> <INSERTSQL>"%(PROG)
  sys.exit()

fin=file(sys.argv[1])
fout=file(sys.argv[2],"w")

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

  id=int(fields[0])
  txt=fields[1]
  txt=re.sub(r"'","\\'",txt)

  fout.write("INSERT INTO hlt VALUES\n")
  fout.write("\t(%d,\n"%id)
  fout.write("\tE'%s');\n"%txt)
  n_lines+=1

fout.close()
print >>sys.stderr, "lines converted to inserts: %d"%n_lines

