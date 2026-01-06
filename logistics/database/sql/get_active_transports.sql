SELECT
    transports.id,
    -- Master Source (Original Origin)
    source_warehouse.id,
    source_warehouse.name,
    source_warehouse.location,
    -- Master Target (Final Destination)
    target_warehouse.id,
    target_warehouse.name,
    target_warehouse.location,
    -- Overall Start Time
    (
        SELECT MIN(all_routes.start_timestamp)
        FROM transport_routes
        WHERE transport_routes.transport_id = transports.id
    ) AS start_time,
    -- Last Stop (Where the truck is coming FROM on the current leg)
    last_stop_warehouse.id,
    last_stop_warehouse.name,
    last_stop_warehouse.location,
    last_route.start_timestamp,
    -- Next Stop (Where the truck is going TO on the current leg)
    next_stop_warehouse.id,
    next_stop_warehouse.name,
    next_stop_warehouse.location
FROM transports
JOIN warehouses source_warehouse ON transports.source_warehouse_id = source_warehouse.id
JOIN warehouses target_warehouse ON transports.target_warehouse_id = target_warehouse.id
JOIN transport_routes last_route ON transports.id = last_route.transport_id
JOIN warehouses last_stop_warehouse ON last_route.source_warehouse_id = last_stop_warehouse.id
JOIN warehouses next_stop_warehouse ON last_route.target_warehouse_id = next_stop_warehouse.id
WHERE last_route.arrival_timestamp IS NULL;