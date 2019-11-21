#!/bin/bash
#
set -e
#
cwd=$(pwd)
DATADIR="${cwd}/data"
#
DBNAME="meddra"
#
echo 'SELECT soc.text FROM soc' \
	|psql -q -S -t -d $DBNAME >$DATADIR/meddra_soc_allterms.txt
#
echo 'SELECT hlgt.text FROM hlgt' \
	|psql -q -S -t -d $DBNAME >$DATADIR/meddra_hlgt_allterms.txt
#
echo 'SELECT pt.text FROM pt' \
	|psql -q -S -t -d $DBNAME >$DATADIR/meddra_pt_allterms.txt
#
echo 'SELECT llt.text FROM llt' \
	|psql -q -S -t -d $DBNAME >$DATADIR/meddra_llt_allterms.txt
#
${cwd}/sh/GoMedDRA_NGramDist.sh
#
