#!/bin/bash
#############################################################################
#
set -e
#
cwd=$(pwd)
#
DBNAME="meddra"
DBVERSION="21.1"
DATADIR="${cwd}/data"
#
if [ ! -e "$DATADIR" ]; then
	mkdir $DATADIR
fi
#
DBDIR=/home/data/MedDRA/${DBVERSION}/MedAscii
#
#
${cwd}/python/meddra_utils.py \
	--convert_soc \
	--i $DBDIR/soc.asc --o $DATADIR/meddra_soc.tsv
${cwd}/python/meddra_utils.py \
	--convert_hlt \
	--i $DBDIR/hlt.asc --o $DATADIR/meddra_hlt.tsv
${cwd}/python/meddra_utils.py \
	--convert_hlgt \
	--i $DBDIR/hlgt.asc --o $DATADIR/meddra_hlgt.tsv
${cwd}/python/meddra_utils.py \
	--convert_pt \
	--i $DBDIR/pt.asc --o $DATADIR/meddra_pt.tsv
${cwd}/python/meddra_utils.py \
	--convert_llt \
	--i $DBDIR/llt.asc --o $DATADIR/meddra_llt.tsv
${cwd}/python/meddra_utils.py \
	--convert_llt2pt \
	--i $DBDIR/llt.asc --o $DATADIR/meddra_pt2llt.tsv
${cwd}/python/meddra_utils.py \
	--convert_soc2hlgt \
	--i $DBDIR/soc_hlgt.asc --o $DATADIR/meddra_soc2hlgt.tsv
${cwd}/python/meddra_utils.py \
	--convert_hlgt2hlt \
	--i $DBDIR/hlgt_hlt.asc --o $DATADIR/meddra_hlgt2hlt.tsv
${cwd}/python/meddra_utils.py \
	--convert_hlt2pt \
	--i $DBDIR/hlt_pt.asc --o $DATADIR/meddra_hlt2pt.tsv
${cwd}/python/meddra_utils.py \
	--convert_soc2intl \
	--i $DBDIR/intl_ord.asc --o $DATADIR/meddra_intl.tsv
${cwd}/python/meddra_utils.py \
	--convert_smq_list \
	--i $DBDIR/smq_list.asc --o $DATADIR/meddra_smq_list.tsv
${cwd}/python/meddra_utils.py \
	--convert_smq_content \
	--i $DBDIR/smq_content.asc --o $DATADIR/meddra_smq_content.tsv
#
#
tsvfiles="\
$DATADIR/meddra_soc.tsv \
$DATADIR/meddra_hlgt.tsv \
$DATADIR/meddra_hlt.tsv \
$DATADIR/meddra_pt.tsv \
$DATADIR/meddra_llt.tsv \
$DATADIR/meddra_pt2llt.tsv \
$DATADIR/meddra_soc2hlgt.tsv \
$DATADIR/meddra_hlgt2hlt.tsv \
$DATADIR/meddra_hlt2pt.tsv \
$DATADIR/meddra_intl.tsv \
$DATADIR/meddra_smq_list.tsv \
$DATADIR/meddra_smq_content.tsv \
"
#
psql -c "CREATE DATABASE $DBNAME"
#
psql -d $DBNAME -c "COMMENT ON DATABASE $DBNAME IS 'MedDRA: Medical Dictionary for Regulatory Activities (v${DBVERSION})'";
#
for tsvfile in $tsvfiles ; do
	#
	tname=`echo $tsvfile |perl -pe 's/^.*meddra_(\S+)\.tsv/$1/;'`
	printf "%s\n" $tname
	#
	${cwd}/python/csv2sql.py \
		--i $tsvfile \
		--tsv \
		--create \
		--tablename "$tname" \
		--fixtags \
		--maxchar 2000 \
		|psql -d $DBNAME
	#
	${cwd}/python/csv2sql.py \
		--i $tsvfile \
		--tsv \
		--tablename "$tname" \
		--insert \
		--fixtags \
		--maxchar 2000 \
		|psql -q -d $DBNAME
	#
done
#
###
psql -d $DBNAME -c "COMMENT ON TABLE soc IS 'MedDRA: System Organ Class (SOC)'";
psql -d $DBNAME -c "COMMENT ON TABLE hlt IS 'MedDRA: High Level Term (HLT)'";
psql -d $DBNAME -c "COMMENT ON TABLE hlgt IS 'MedDRA: High Level Group Term (HLGT)'";
psql -d $DBNAME -c "COMMENT ON TABLE llt IS 'MedDRA: Low Level Term (LLT)'";
psql -d $DBNAME -c "COMMENT ON TABLE pt IS 'MedDRA: Preferred Term (PT)'";
#
psql -d $DBNAME -c "UPDATE soc SET text = NULL WHERE text = ''";
#
