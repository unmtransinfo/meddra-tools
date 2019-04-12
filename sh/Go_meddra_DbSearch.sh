#!/bin/sh
#
set -e
#
DB="meddra"
#
psql $DB <<__EOF__
\timing on
SELECT
	llt.id as "llt_id",
	llt.pt,
	pt2llt.pt_id,
	llt.text
FROM
	llt,
	pt2llt
WHERE
	llt.text ILIKE '%glucose%urine%'
	AND llt.id=pt2llt.pt_id
	LIMIT 10
	;
--
--
SELECT
	soc.id as "soc_id",
	soc.text as "soc",
	hlgt.id as "hlgt_id",
	hlgt.text as "hlgt",
	hlt.id as "hlt_id",
	hlt.text as "hlt",
	pt.id as "pt_id",
	pt.text as "pt",
	llt.id as "llt_id",
	llt.text as "llt"
FROM
	soc,
	hlgt,
	hlt,
	pt,
	llt,
	soc2hlgt,
	hlgt2hlt,
	hlt2pt,
	pt2llt
WHERE
	llt.text ILIKE '%glucose%urine%'
	AND soc.id=soc2hlgt.soc_id
	AND hlgt.id=soc2hlgt.hlgt_id
	AND hlgt.id=hlgt2hlt.hlgt_id
	AND hlt.id=hlgt2hlt.hlt_id
	AND hlt.id=hlt2pt.hlt_id
	AND pt.id=hlt2pt.pt_id
	AND pt.id=pt2llt.pt_id
	AND llt.id=pt2llt.llt_id
	;
__EOF__
#
