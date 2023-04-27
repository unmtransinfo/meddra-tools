#!/bin/bash
#############################################################################
#
set -e
#
T0=$(date +%s)
#
cwd=$(pwd)
#
if [ ! -f ${cwd}/LATEST_RELEASE.txt ]; then
	printf "ERROR: not found: ${cwd}/LATEST_RELEASE.txt\n"
	exit
fi
DBVERSION=$(cat ${cwd}/LATEST_RELEASE.txt)
printf "From ${cwd}/LATEST_RELEASE.txt: ${DBVERSION}\n"
DBNAME="meddra_$(echo $DBVERSION |sed 's/\.//g')"
DATADIR="${cwd}/data"
#
if [ ! -e "$DATADIR" ]; then
	mkdir $DATADIR
fi
#
DBDIR=$(cd $HOME/../data/MedDRA/${DBVERSION}; pwd)
#
if [ ! -e "${DBDIR}" ]; then
	printf "ERROR: DBDIR not found: ${DBDIR}\n"
	exit 1
fi
#
printf "CONVERTING RAW FILES TO TSVS.\n"
${cwd}/python/meddra_utils.py convert_soc --i ${DBDIR}/MedAscii/soc.asc --o $DATADIR/meddra_soc.tsv
${cwd}/python/meddra_utils.py convert_hlt --i ${DBDIR}/MedAscii/hlt.asc --o $DATADIR/meddra_hlt.tsv
${cwd}/python/meddra_utils.py convert_hlgt --i ${DBDIR}/MedAscii/hlgt.asc --o $DATADIR/meddra_hlgt.tsv
${cwd}/python/meddra_utils.py convert_pt --i ${DBDIR}/MedAscii/pt.asc --o $DATADIR/meddra_pt.tsv
${cwd}/python/meddra_utils.py convert_llt --i ${DBDIR}/MedAscii/llt.asc --o $DATADIR/meddra_llt.tsv
${cwd}/python/meddra_utils.py convert_llt2pt --i ${DBDIR}/MedAscii/llt.asc --o $DATADIR/meddra_llt2pt.tsv
${cwd}/python/meddra_utils.py convert_soc2hlgt --i ${DBDIR}/MedAscii/soc_hlgt.asc --o $DATADIR/meddra_soc2hlgt.tsv
${cwd}/python/meddra_utils.py convert_hlgt2hlt --i ${DBDIR}/MedAscii/hlgt_hlt.asc --o $DATADIR/meddra_hlgt2hlt.tsv
${cwd}/python/meddra_utils.py convert_hlt2pt --i ${DBDIR}/MedAscii/hlt_pt.asc --o $DATADIR/meddra_hlt2pt.tsv
${cwd}/python/meddra_utils.py convert_soc2intl --i ${DBDIR}/MedAscii/intl_ord.asc --o $DATADIR/meddra_intl.tsv
${cwd}/python/meddra_utils.py convert_smq_list --i ${DBDIR}/MedAscii/smq_list.asc --o $DATADIR/meddra_smq_list.tsv
${cwd}/python/meddra_utils.py convert_smq_content --i ${DBDIR}/MedAscii/smq_content.asc --o $DATADIR/meddra_smq_content.tsv
#
#
tsvfiles="\
$DATADIR/meddra_soc.tsv \
$DATADIR/meddra_hlgt.tsv \
$DATADIR/meddra_soc2hlgt.tsv \
$DATADIR/meddra_hlt.tsv \
$DATADIR/meddra_hlgt2hlt.tsv \
$DATADIR/meddra_pt.tsv \
$DATADIR/meddra_hlt2pt.tsv \
$DATADIR/meddra_llt.tsv \
$DATADIR/meddra_llt2pt.tsv \
$DATADIR/meddra_intl.tsv \
$DATADIR/meddra_smq_list.tsv \
$DATADIR/meddra_smq_content.tsv \
"
#
psql -c "DROP DATABASE IF EXISTS $DBNAME"
psql -c "CREATE DATABASE $DBNAME"
#
psql -d $DBNAME -c "COMMENT ON DATABASE $DBNAME IS 'MedDRA: Medical Dictionary for Regulatory Activities (v${DBVERSION})'";
#
i_table="0"
for tsvfile in $tsvfiles ; do
	i_table=$[$i + 1]
	n_lines=$(cat $tsvfile |wc -l)
	tname=$(echo $tsvfile |perl -pe 's/^.*meddra_(\S+)\.tsv/$1/;')
	printf "${i_table}. CREATING AND LOADING TABLE: ${tname} FROM INPUT FILE: ${tsvfile} (${n_lines} lines)\n"
	#
	${cwd}/python/csv2sql.py create --fixtags --nullify --maxchar 2000 \
		--i $tsvfile --tsv --tablename "$tname" \
		|psql -d $DBNAME
	#
	${cwd}/python/csv2sql.py insert --fixtags --nullify --maxchar 2000 \
		--i $tsvfile --tsv --tablename "$tname" \
		|psql -q -d $DBNAME
	#
done
printf "TABLES CREATED AND LOADED: ${i_table}\n"
#
#psql -d $DBNAME -c "UPDATE soc SET text = NULL WHERE text = ''";
###
psql -d $DBNAME -c "COMMENT ON TABLE soc IS 'MedDRA: System Organ Class (SOC)'";
psql -d $DBNAME -c "COMMENT ON TABLE hlt IS 'MedDRA: High Level Term (HLT)'";
psql -d $DBNAME -c "COMMENT ON TABLE hlgt IS 'MedDRA: High Level Group Term (HLGT)'";
psql -d $DBNAME -c "COMMENT ON TABLE llt IS 'MedDRA: Low Level Term (LLT)'";
psql -d $DBNAME -c "COMMENT ON TABLE pt IS 'MedDRA: Preferred Term (PT)'";
#
#
###
# How to dump and restore:
# pg_dump --no-privileges -Fc -d ${DBNAME} >${DBNAME}.pgdump
# createdb ${DBNAME} ; pg_restore -e -O -x -d ${DBNAME} ${DBNAME}.pgdump
###
printf "Elapsed: %ds\n" "$[$(date +%s) - $T0]"
#
