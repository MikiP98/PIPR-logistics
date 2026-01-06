PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON; -- Enable FK enforcement

-- 1. Warehouses
CREATE TABLE warehouses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    capacity_volume_cm INTEGER NOT NULL
) STRICT;

-- 2. Connections
CREATE TABLE connections (
    source_warehouse_id INTEGER NOT NULL,
    target_warehouse_id INTEGER NOT NULL,
    transportation_time_minutes INTEGER NOT NULL,
    is_two_way INTEGER NOT NULL CHECK (is_two_way IN (0, 1)), -- "two_way" enforced as Bool

    PRIMARY KEY (source_warehouse_id, target_warehouse_id, is_two_way),
    FOREIGN KEY (source_warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (target_warehouse_id) REFERENCES warehouses(id),

    -- CHECK 1: Prevent source == target
    CONSTRAINT check_source_not_target CHECK (source_warehouse_id <> target_warehouse_id)
) STRICT;

-- CHECK 2: Trigger to prevent adding (1, 0) if (0, 1) is already Two-Way
CREATE TRIGGER prevent_redundant_reverse_connection
BEFORE INSERT ON connections
BEGIN
    SELECT RAISE(ABORT, 'Cannot add route: A two-way connection already exists in the reverse direction.')
    FROM connections
    WHERE source_warehouse_id = NEW.target_warehouse_id
        AND target_warehouse_id = NEW.source_warehouse_id
        AND is_two_way = 1 AND NEW.is_two_way = 1;
END;

-- 3. Products
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    barcode INTEGER NOT NULL,
    -- mass INTEGER NOT NULL,
    volume_cm INTEGER NOT NULL
) STRICT;

-- 4. Stock
CREATE TABLE stock (
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    count INTEGER NOT NULL CHECK ( count > 0 ),

    PRIMARY KEY (product_id, warehouse_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
) STRICT;

-- Trigger 1 for adding new stock
CREATE TRIGGER prevent_overfill_insert
BEFORE INSERT ON stock
BEGIN
    SELECT RAISE(ABORT, 'Insert failed: Warehouse capacity exceeded.')
    WHERE (
        -- 1. Get the Capacity of the target warehouse
        (SELECT capacity_volume_cm FROM warehouses WHERE id = NEW.warehouse_id)
        <
        -- 2. Calculate the Hypothethical New Total Volume
        (
            -- Volume of the NEW item(s) being added
            (NEW.count * (SELECT volume_cm FROM products WHERE id = NEW.product_id))
            +
            -- Volume of everything ELSE currently in the warehouse
            (
                SELECT TOTAL(s.count * p.volume_cm)
                FROM stock s
                JOIN products p ON s.product_id = p.id
                WHERE s.warehouse_id = NEW.warehouse_id
                AND s.product_id != NEW.product_id
                -- distinct check ensures we don't double count, probably unnecessary
            )
        )
    );
END;

-- Trigger 2 for updating existing stock counts
CREATE TRIGGER prevent_overfill_update
BEFORE UPDATE ON stock
BEGIN
    SELECT RAISE(ABORT, 'Update failed: Warehouse capacity exceeded.')
    WHERE (
        -- 1. Get the Capacity of the target warehouse
        (SELECT capacity_volume_cm FROM warehouses WHERE id = NEW.warehouse_id)
        <
        -- 2. Calculate the Hypothethical New Total Volume
        (
            (NEW.count * (SELECT volume_cm FROM products WHERE id = NEW.product_id))
            +
            (
                SELECT TOTAL(s.count * p.volume_cm)
                FROM stock s
                JOIN products p ON s.product_id = p.id
                WHERE s.warehouse_id = NEW.warehouse_id
                AND s.product_id != NEW.product_id
                -- This excludes the "Old" version of the row
            )
        )
    );
END;

-- 5. Transports
CREATE TABLE transports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_warehouse_id INTEGER NOT NULL,
    target_warehouse_id INTEGER NOT NULL,

    FOREIGN KEY (source_warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (target_warehouse_id) REFERENCES warehouses(id)
) STRICT;

-- 6. Transport Routes
CREATE TABLE transport_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transport_id INTEGER NOT NULL,
    source_warehouse_id INTEGER NOT NULL,
    target_warehouse_id INTEGER NOT NULL,
    start_timestamp INTEGER NOT NULL, -- Store as ~~Unix Epoch~~ minutes from X?
    arrival_timestamp INTEGER,        -- Nullable if not arrived yet

    FOREIGN KEY (transport_id) REFERENCES transports(id),
    FOREIGN KEY (source_warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (target_warehouse_id) REFERENCES warehouses(id)
) STRICT;

-- 7. Transported Stock
CREATE TABLE transported_stock (
    transport_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    count INTEGER NOT NULL,

    PRIMARY KEY (transport_id, product_id),
    FOREIGN KEY (transport_id) REFERENCES transports(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) STRICT;