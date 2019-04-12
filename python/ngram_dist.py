#!/usr/bin/env python
#############################################################################
# ngram_dist.py - word count distribution
# Jeremy J Yang
#  8 Apr 2011
#############################################################################
import os,sys,re

NMAX=20
n_dist={}
for i in range(NMAX):
  n_dist[i]=0

n_lines=0
while True:
  line=sys.stdin.readline()
  if not line: break
  n_lines+=1
  line=line.strip()
  fields=re.split(r'\s',line)
  n=len(fields)
  n_dist[min(n-1,NMAX-1)]+=1

print 'N-gram word count distribution:'
n=0
for i in range(NMAX-1):
  n+=n_dist[i]
  print '%3d: %5d %5d%% %5d%%'%(i+1,n_dist[i],100.0*n_dist[i]/n_lines,100.0*n/n_lines)
n+=n_dist[NMAX-1]
print '%2d+: %5d %5d%% %5d%%'%(NMAX,n_dist[NMAX-1],100.0*n_dist[i]/n_lines,100.0*n/n_lines)
print 'total ngrams (terms): %d'%n_lines
