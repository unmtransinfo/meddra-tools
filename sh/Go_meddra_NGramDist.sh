#!/bin/sh
#
set -e
#
for f in \
	data/meddra_soc_allterms.txt \
	data/meddra_hlgt_allterms.txt \
	data/meddra_pt_allterms.txt \
	data/meddra_llt_allterms.txt \
	; do
	wc -l $f
done
#
cat \
	data/meddra_soc_allterms.txt \
	data/meddra_hlgt_allterms.txt \
	data/meddra_pt_allterms.txt \
	data/meddra_llt_allterms.txt \
	| ./ngram_dist.py
#
