SELECT
    transport_routes.id,
    transport_routes.transport_id,
    transport_routes.start_timestamp,
    connections.transportation_time_minutes,
    connections.target_warehouse_id,
    transports.target_warehouse_id
FROM transport_routes
JOIN connections ON transport_routes.connection_id = connections.id
JOIN transports ON transport_routes.transport_id = transports.id
WHERE transport_routes.arrival_timestamp IS NULL;