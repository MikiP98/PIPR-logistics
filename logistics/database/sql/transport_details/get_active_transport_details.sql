SELECT
    t.id,
    -- Master Source
    w_source.id,
    w_source.name,
    w_source.location,
    -- Master Target
    w_target.id,
    w_target.name,
    w_target.location,
    -- Global Start Time
    (SELECT MIN(start_timestamp) FROM transport_routes WHERE transport_id = t.id),
    -- CURRENT LEG INFO
    cur.source_warehouse_id,
    cur.target_warehouse_id,
    cur.start_timestamp
FROM transports t
JOIN warehouses w_source ON t.source_warehouse_id = w_source.id
JOIN warehouses w_target ON t.target_warehouse_id = w_target.id
JOIN transport_routes cur ON t.id = cur.transport_id
WHERE t.id = ?
AND cur.arrival_timestamp IS NULL;