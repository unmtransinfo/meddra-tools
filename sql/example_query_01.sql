SELECT 
        soc.id AS soc_id, soc.text AS soc_text,
        hlgt.id AS hlgt_id, hlgt.text AS hlgt_text,
        hlt.id AS hlt_id, hlt.text AS hlt_text,
        pt.id AS pt_id, pt.text AS pt_text, pt.soc,
        llt.id AS llt_id, llt.text AS llt_text
FROM
        pt
        JOIN hlt2pt ON hlt2pt.pt_id = pt.id
        JOIN hlt ON hlt.id = hlt2pt.hlt_id
        JOIN hlgt2hlt ON hlgt2hlt.hlt_id = hlt.id
        JOIN hlgt ON hlgt.id = hlgt2hlt.hlgt_id
        JOIN llt2pt ON llt2pt.pt_id = pt.id
        JOIN llt ON llt.id = llt2pt.llt_id
        JOIN soc2hlgt ON soc2hlgt.hlgt_id = hlgt.id
        JOIN soc ON soc.id = soc2hlgt.soc_id
WHERE
        hlgt.text ILIKE 'Psychiatri%'
ORDER BY
        soc_id, hlgt_id, hlt_id, pt_id, llt_id
        ;        