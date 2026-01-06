SELECT
    transport_routes.id,
    w_source.id, w_source.name, w_source.location,
    w_target.id, w_target.name, w_target.location,
    transport_routes.start_timestamp,
    transport_routes.arrival_timestamp
FROM transport_routes
JOIN warehouses w_source ON transport_routes.source_warehouse_id = w_source.id
JOIN warehouses w_target ON transport_routes.target_warehouse_id = w_target.id
WHERE transport_routes.transport_id = ?
ORDER BY transport_routes.start_timestamp ASC;