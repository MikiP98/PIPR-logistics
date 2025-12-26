SELECT
    w.id,
    w.name,
    w.location,
    w.capacity_volume_cm,
    -- Calculate Current Filled Capacity
    (
        SELECT IFNULL(SUM(s.count * p.volume_cm), 0)
        FROM stock s
        JOIN products p ON s.product_id = p.id
        WHERE s.warehouse_id = w.id
    ) AS current_filled_capacity,
    -- Calculate Reserved Capacity (Incoming Transports)
    (
        SELECT IFNULL(SUM(ts.count * p.volume_cm), 0)
        FROM transported_stock ts
        JOIN products p ON ts.product_id = p.id
        JOIN transports t ON ts.transport_id = t.id
        WHERE t.target_warehouse_id = w.id
    ) AS reserved_capacity
FROM warehouses w;