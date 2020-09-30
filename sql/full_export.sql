SELECT
	soc.id soc_id,
	soc.text soc_text,
	hlgt.id hlgt_id,
	hlgt.text hlgt_text,
	hlt.id hlt_id,
	hlt.text hlt_text,
	pt.id pt_id,
	pt.text pt_text,
	llt.id llt_id,
	llt.text llt_text
FROM
	soc
	JOIN soc2hlgt ON soc.id = soc2hlgt.soc_id
	JOIN hlgt ON soc2hlgt.hlgt_id = hlgt.id
	JOIN hlgt2hlt ON hlgt.id = hlgt2hlt.hlgt_id
	JOIN hlt ON hlgt2hlt.hlt_id = hlt.id
	JOIN hlt2pt ON hlt.id = hlt2pt.hlt_id 
	JOIN pt ON hlt2pt.pt_id = pt.id
	JOIN pt2llt ON pt2llt.pt_id = pt.id
	JOIN llt ON pt2llt.llt_id = llt.id
ORDER BY
	soc_id, hlgt_id, hlt_id, pt_id, llt_id  
;
