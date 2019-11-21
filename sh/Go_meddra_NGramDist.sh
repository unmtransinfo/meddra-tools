#!/bin/bash
#
set -e
#
cwd=$(pwd)
#
DATADIR="${cwd}/data"
#
for f in \
	$DATADIR/meddra_soc_allterms.txt \
	$DATADIR/meddra_hlgt_allterms.txt \
	$DATADIR/meddra_pt_allterms.txt \
	$DATADIR/meddra_llt_allterms.txt \
	; do
	wc -l $f
done
#
cat \
	$DATADIR/meddra_soc_allterms.txt \
	$DATADIR/meddra_hlgt_allterms.txt \
	$DATADIR/meddra_pt_allterms.txt \
	$DATADIR/meddra_llt_allterms.txt \
	| ${cwd}/python/ngram_dist.py
#
