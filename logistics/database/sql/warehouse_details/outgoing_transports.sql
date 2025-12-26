SELECT
    t.id AS transport_id,
    w.id AS target_warehouse_id,
    w.name AS target_warehouse_name,
    w.location AS target_warehouse_location
FROM transports t
JOIN warehouses w ON t.target_warehouse_id = w.id
WHERE t.source_warehouse_id = ?; -- Input: {warehouse_id}