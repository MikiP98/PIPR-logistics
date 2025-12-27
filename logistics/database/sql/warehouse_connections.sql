SELECT
    source.id, source.name, source.location,
    target.id, target.name, target.location,
    connections.transportation_time_minutes,
    connections.is_two_way
FROM connections
JOIN warehouses source ON connections.source_warehouse_id = source.id
JOIN warehouses target ON connections.target_warehouse_id = target.id;