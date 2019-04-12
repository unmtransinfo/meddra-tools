#!/bin/sh
#
set -e
#
DB="meddra"
#
echo 'SELECT soc.text FROM soc' \
	|psql -q -S -t $DB >data/meddra_soc_allterms.txt
#
echo 'SELECT hlgt.text FROM hlgt ' \
	|psql -q -S -t $DB >data/meddra_hlgt_allterms.txt
#
echo 'SELECT pt.text FROM pt' \
	|psql -q -S -t $DB >data/meddra_pt_allterms.txt
#
echo 'SELECT llt.text FROM llt ' \
	|psql -q -S -t $DB >data/meddra_llt_allterms.txt
#
./GoMedDRA_NGramDist.sh
#
