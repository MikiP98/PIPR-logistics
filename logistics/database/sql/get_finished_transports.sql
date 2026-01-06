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
    -- Aggregates
    COUNT(transport_routes.id) AS "STOP COUNT",
    MIN(transport_routes.start_timestamp) AS "TRANSPORT START TIME",
    MAX(transport_routes.arrival_timestamp) AS "TRANSPORT END TIME",
    (MAX(transport_routes.arrival_timestamp) - MIN(tr.start_timestamp)) AS "TOTAL TRANSPORT TIME"
FROM transports
JOIN warehouses source_warehouse ON transports.source_warehouse_id = source_warehouse.id
JOIN warehouses target_warehouse ON transports.target_warehouse_id = target_warehouse.id
JOIN transport_routes ON transports.id = transport_routes.transport_id
-- Group by the Transport to calculate aggregates
GROUP BY transports.id
-- FILTER: Keep only transports where ALL routes have an arrival time
HAVING COUNT(transport_routes.id) = COUNT(transport_routes.arrival_timestamp);