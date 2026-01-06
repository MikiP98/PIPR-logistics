SELECT
    products.id,
    products.name,
    products.barcode,
    transported_stock.count,
    (transported_stock.count * products.volume_cm) AS total_volume
FROM transported_stock
JOIN products ON transported_stock.product_id = products.id
WHERE transported_stock.transport_id = ?;