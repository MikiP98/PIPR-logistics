SELECT
    t.id AS transport_id,
    source_w.id AS original_source_id,
    source_w.name AS original_source_name,
    source_w.location AS original_source_location,
    final_w.id AS final_destination_id,
    final_w.name AS final_destination_name,
    final_w.location AS final_destinatio_location
FROM transport_routes tr
JOIN transports t ON tr.transport_id = t.id
JOIN warehouses final_w ON t.target_warehouse_id = final_w.id
JOIN warehouses source_w ON t.source_warehouse_id = source_w.id
WHERE tr.target_warehouse_id = ?   -- The route leg is coming HERE
AND t.target_warehouse_id != ?   -- But the final destination is NOT here
AND tr.arrival_timestamp IS NULL; -- And it hasn't arrived yet (optional check)