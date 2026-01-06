-- Returns 1 if Active (on the road), 0 if Finished (or not started/error)
SELECT EXISTS (
    SELECT 1
    FROM transport_routes
    WHERE transport_id = ? AND arrival_timestamp IS NULL
);