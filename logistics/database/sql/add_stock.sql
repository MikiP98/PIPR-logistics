INSERT INTO stock (product_id, warehouse_id, count)
VALUES (?, ?, ?)
ON CONFLICT(product_id, warehouse_id)
DO UPDATE SET count = stock.count + excluded.count;