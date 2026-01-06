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
    -- Times
    MIN(tr.start_timestamp),
    MAX(tr.arrival_timestamp)
FROM transports t
JOIN warehouses w_source ON t.source_warehouse_id = w_source.id
JOIN warehouses w_target ON t.target_warehouse_id = w_target.id
JOIN transport_routes ON t.id = transport_routes.transport_id
WHERE t.id = ?
GROUP BY t.id;