SELECT
    t.id AS transport_id,
    w.id AS source_warehouse_id,
    w.name AS source_warehouse_name,
    w.location AS source_warehouse_location
FROM transports t
JOIN warehouses w ON t.source_warehouse_id = w.id
WHERE t.target_warehouse_id = ?; -- Input: {warehouse_id}"