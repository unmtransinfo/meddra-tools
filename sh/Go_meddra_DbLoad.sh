#!/bin/sh
#############################################################################
### Go_meddra_Load.sh
###
### Jeremy J Yang
### 27 Jun 2012
#############################################################################
set -e
#
DB="meddra"
MEDDRAVERSION="15.0"
SCRATCHDIR="data"
#
DBDIR=/home/data/MedDRA/MedAscii
#
set -x
#
./soc2inserts.py $DBDIR/soc.asc $SCRATCHDIR/soc_inserts.sql
./hlgt2inserts.py $DBDIR/hlgt.asc $SCRATCHDIR/hlgt_inserts.sql
./hlt2inserts.py $DBDIR/hlt.asc $SCRATCHDIR/hlt_inserts.sql
./pt2inserts.py $DBDIR/pt.asc $SCRATCHDIR/pt_inserts.sql
./llt2inserts.py $DBDIR/llt.asc $SCRATCHDIR/llt_inserts.sql
#
#exit	#DEBUG
#
psql -q $DB < $SCRATCHDIR/soc_inserts.sql
psql -q $DB < $SCRATCHDIR/hlgt_inserts.sql
psql -q $DB < $SCRATCHDIR/hlt_inserts.sql
psql -q $DB < $SCRATCHDIR/pt_inserts.sql
psql -q $DB < $SCRATCHDIR/llt_inserts.sql
#
cat $DBDIR/soc_hlgt.asc \
	| sed -e 's/\$\s*$/\);/' \
	| sed -e 's/\$/,/' \
	| sed -e 's/^/INSERT INTO soc2hlgt VALUES (/' \
	|psql -q $DB
#
cat $DBDIR/hlgt_hlt.asc \
	| sed -e 's/\$\s*$/\);/' \
	| sed -e 's/\$/,/' \
	| sed -e 's/^/INSERT INTO hlgt2hlt VALUES (/' \
	|psql -q $DB
#
cat $DBDIR/hlt_pt.asc \
	| sed -e 's/\$\s*$/\);/' \
	| sed -e 's/\$/,/' \
	| sed -e 's/^/INSERT INTO hlt2pt VALUES (/' \
	|psql -q $DB
#
psql $DB <<__EOF__
INSERT INTO metadata
	(db_version,db_description,db_date_built)
	VALUES (
	'$MEDDRAVERSION',
        'MSSO MedDRA (UNM Translational Informatics Divison edition)',
        CURRENT_TIMESTAMP
	);
__EOF__
#
