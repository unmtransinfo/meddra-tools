#!/bin/sh
#############################################################################
### Go_meddra_Dump_LLTs_plus.sh
### Dump all LLTs, one per row, followed by corresponding PT, HLT, HLGT, SOC (hierarchical order).
### Jeremy J Yang
### 21 Mar 2012
#############################################################################
set -e
#
DB="meddra"
#
cat <<__EOF__  |psql -q -F ',' $DB
\a
SELECT
	llt.id AS "llt_id",
	pt2llt.pt_id,
	hlt2pt.hlt_id,
	hlgt2hlt.hlgt_id,
	soc2hlgt.soc_id
FROM
	llt,
	pt2llt,
	hlt2pt,
	hlgt2hlt,
	soc2hlgt
WHERE
	llt.id=pt2llt.llt_id
	AND pt2llt.pt_id=hlt2pt.pt_id
	AND hlt2pt.hlt_id=hlgt2hlt.hlt_id
	AND soc2hlgt.hlgt_id=hlgt2hlt.hlgt_id
	;
__EOF__
#
