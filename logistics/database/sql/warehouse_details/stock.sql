SELECT
    p.id,
    p.name,
    p.barcode,
    s.count,
    (s.count * p.volume_cm) AS total_volume
FROM stock s
INNER JOIN products p ON s.product_id = p.id
WHERE s.warehouse_id = ?; -- Input: {warehouse_id}"