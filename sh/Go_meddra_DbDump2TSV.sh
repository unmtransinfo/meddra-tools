#!/bin/bash
#
set -e
#
DBNAME="meddra"
#
cwd=$(pwd)
DATADIR="${cwd}/data"
#
tables="soc hlgt hlt pt llt soc2hlgt hlgt2hlt hlt2pt pt2llt"
#
for table in $tables ; do
	#
	tsvfile=${DATADIR}/${DBNAME}_${table}_dump.tsv
	echo "$tsvfile"
	#
	psql -d $DBNAME -c "COPY ${table} TO STDOUT WITH (FORMAT CSV, HEADER, DELIMITER E'\t')" \
		>$tsvfile
	#
done
#
###
DBVER=$(psql -q -t -S -d $DBNAME -c "SELECT db_version FROM metadata" |sed -e "s/ //g")
echo "DBVER: \"$DBVER\""
#
