#!/bin/bash
#############################################################################
# Go_whodrug_DbCreate.sh - Create and load WHODrug Global C3 database
#
# Usage: ./sh/Go_whodrug_DbCreate.sh
#
# Expects WHODrug C3 CSV files in data/WHODrugC3/
# Reads version from LATEST_WHODRUG_RELEASE.txt
# Creates database whodrug_{version} (e.g., whodrug_2603)
#############################################################################
set -e
#
T0=$(date +%s)
#
cwd=$(pwd)
#
# PostgreSQL connection parameters
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5433}"
export PGUSER="${PGUSER:-meddict}"
export PGPASSWORD="${PGPASSWORD:-meddict}"
#
if [ ! -f ${cwd}/LATEST_WHODRUG_RELEASE.txt ]; then
  printf "ERROR: not found: ${cwd}/LATEST_WHODRUG_RELEASE.txt\n"
  exit 1
fi
DBVERSION=$(cat ${cwd}/LATEST_WHODRUG_RELEASE.txt | tr -d '[:space:]')
printf "From ${cwd}/LATEST_WHODRUG_RELEASE.txt: ${DBVERSION}\n"
DBNAME="whodrug_${DBVERSION}"
DATADIR="${cwd}/data"
CSVDIR="${DATADIR}/WHODrugC3"
#
if [ ! -e "$DATADIR" ]; then
  mkdir $DATADIR
fi
#
# Validate CSV directory
if [ ! -f "${CSVDIR}/MP.csv" ]; then
  printf "ERROR: WHODrug C3 CSV files not found in ${CSVDIR}/\n"
  printf "Expected files: MP.csv, ThG.csv, ING.csv, SUN.csv, ATC.csv, PF.csv, STR.csv, ORG.csv, SRCE.csv, CCODE.csv, PRT.csv, UNIT.csv, Version.csv\n"
  exit 1
fi
#
printf "=== CONVERTING CSV FILES TO TSVS ===\n"
${cwd}/python/whodrug_utils.py convert_ccode --i ${CSVDIR}/CCODE.csv --o $DATADIR/whodrug_ccode.tsv
${cwd}/python/whodrug_utils.py convert_srce --i ${CSVDIR}/SRCE.csv --o $DATADIR/whodrug_srce.tsv
${cwd}/python/whodrug_utils.py convert_prt --i ${CSVDIR}/PRT.csv --o $DATADIR/whodrug_prt.tsv
${cwd}/python/whodrug_utils.py convert_unit --i ${CSVDIR}/UNIT.csv --o $DATADIR/whodrug_unit.tsv
${cwd}/python/whodrug_utils.py convert_pf --i ${CSVDIR}/PF.csv --o $DATADIR/whodrug_pf.tsv
${cwd}/python/whodrug_utils.py convert_str --i ${CSVDIR}/STR.csv --o $DATADIR/whodrug_str.tsv
${cwd}/python/whodrug_utils.py convert_org --i ${CSVDIR}/ORG.csv --o $DATADIR/whodrug_org.tsv
${cwd}/python/whodrug_utils.py convert_atc --i ${CSVDIR}/ATC.csv --o $DATADIR/whodrug_atc.tsv
${cwd}/python/whodrug_utils.py convert_sun --i ${CSVDIR}/SUN.csv --o $DATADIR/whodrug_sun.tsv
${cwd}/python/whodrug_utils.py convert_mp --i ${CSVDIR}/MP.csv --o $DATADIR/whodrug_mp.tsv
${cwd}/python/whodrug_utils.py convert_thg --i ${CSVDIR}/ThG.csv --o $DATADIR/whodrug_thg.tsv
${cwd}/python/whodrug_utils.py convert_ing --i ${CSVDIR}/ING.csv --o $DATADIR/whodrug_ing.tsv
${cwd}/python/whodrug_utils.py convert_version --i ${CSVDIR}/Version.csv --o $DATADIR/whodrug_version.tsv
#
printf "=== CREATING DATABASE: ${DBNAME} ===\n"
psql -c "DROP DATABASE IF EXISTS $DBNAME"
psql -c "CREATE DATABASE $DBNAME"
psql -d $DBNAME -c "COMMENT ON DATABASE $DBNAME IS 'WHODrug Global C3 (v${DBVERSION})'"
#
# pg_trgm extension for performant ILIKE search on ~5.6M rows
psql -d $DBNAME -c "CREATE EXTENSION IF NOT EXISTS pg_trgm"
#
printf "=== CREATING TABLES ===\n"
psql -d $DBNAME < ${cwd}/sql/whodrug_schema.sql
#
# Load order: reference tables first, then main, then dependent
# Using COPY FROM STDIN (50x faster than INSERT for ~20M rows)
printf "=== LOADING DATA VIA COPY ===\n"
#
tables="ccode srce prt unit pf str org atc sun mp thg ing version"
i_table=0
for tname in $tables; do
  i_table=$((i_table + 1))
  f="$DATADIR/whodrug_${tname}.tsv"
  n_lines=$(($(wc -l < "$f") - 1))  # subtract header line
  printf "${i_table}. LOADING TABLE: ${tname} (${n_lines} rows)\n"
  # Skip header (line 1) and use COPY for fast bulk load
  tail -n +2 "$f" | psql -q -d $DBNAME -c "COPY ${tname} FROM STDIN WITH (FORMAT text, NULL '')"
done
printf "TABLES LOADED: ${i_table}\n"
#
printf "=== CREATING INDEXES ===\n"
psql -d $DBNAME < ${cwd}/sql/whodrug_indexes.sql
#
# Table comments
psql -d $DBNAME -c "COMMENT ON TABLE mp IS 'WHODrug C3: Medicinal Products (main table, ~5.6M rows)'"
psql -d $DBNAME -c "COMMENT ON TABLE thg IS 'WHODrug C3: Therapeutic Groups / ATC assignments (~6M rows)'"
psql -d $DBNAME -c "COMMENT ON TABLE ing IS 'WHODrug C3: Ingredients (~9M rows)'"
psql -d $DBNAME -c "COMMENT ON TABLE sun IS 'WHODrug C3: Substances (~28K rows)'"
psql -d $DBNAME -c "COMMENT ON TABLE atc IS 'WHODrug C3: ATC Classification (~1.4K rows)'"
psql -d $DBNAME -c "COMMENT ON TABLE pf IS 'WHODrug C3: Pharmaceutical Forms'"
psql -d $DBNAME -c "COMMENT ON TABLE str IS 'WHODrug C3: Strengths'"
psql -d $DBNAME -c "COMMENT ON TABLE org IS 'WHODrug C3: Organizations (~92K rows)'"
psql -d $DBNAME -c "COMMENT ON TABLE srce IS 'WHODrug C3: Sources/References'"
psql -d $DBNAME -c "COMMENT ON TABLE ccode IS 'WHODrug C3: Country Codes (ISO 3166-1 alpha-3)'"
psql -d $DBNAME -c "COMMENT ON TABLE prt IS 'WHODrug C3: Product Types'"
psql -d $DBNAME -c "COMMENT ON TABLE unit IS 'WHODrug C3: Units of measurement'"
psql -d $DBNAME -c "COMMENT ON TABLE version IS 'WHODrug C3: Dataset version info'"
#
printf "=== DONE ===\n"
printf "Database: ${DBNAME}\n"
printf "Elapsed: %ds\n" "$(($(date +%s) - $T0))"
#
# How to dump and restore:
# pg_dump --no-privileges -Fc -d ${DBNAME} >${DBNAME}.pgdump
# createdb ${DBNAME} ; pg_restore -e -O -x -d ${DBNAME} ${DBNAME}.pgdump
#
