#!/bin/sh
#
set -e
set -x
#
DB="meddra"
#
DATADIR="data"
#
tables="soc hlgt hlt pt llt soc2hlgt hlgt2hlt hlt2pt pt2llt"
#
#for table in $tables ; do
#	echo $table
#	cat <<__EOF__ |psql -q -F ',' $DB >data/meddra_${table}_dump.csv
#\a
#SELECT $table.* FROM $table;
#__EOF__
#done
#
#
for table in $tables ; do
	#
	csvfile=${DATADIR}/${DB}_${table}_dump.csv
	echo "$csvfile"
	#
	psql -d $DB -c "COPY ${table} TO STDOUT WITH (FORMAT CSV, DELIMITER ',', QUOTE '\"', FORCE_QUOTE *)" \
		>$csvfile
	#
done
#
#
#
#
#
DBVER=`echo "SELECT db_version from metadata" |psql -q -t -S $DB |sed -e 's/ //g'`
echo "DBVER = \"$DBVER\""
#
#thisdir=`pwd`
#cd ..
#tar czvf $thisdir/data/meddra-${DBVER}_dump_csv.tgz \
#	$thisdir/data/meddra_*_dump.csv \
#	$thisdir/GoMedDRACreate.sh
#
