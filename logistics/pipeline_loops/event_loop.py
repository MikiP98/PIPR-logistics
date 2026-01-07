import heapq
import math
import time
from pathlib import Path
from typing import NamedTuple

from logistics.database.database import Database
from logistics.io_utils import error
from logistics.pipeline_loops.virtual_clock import VirtualClock


def run_event_loop(db_path: Path, clock: VirtualClock) -> None:
    database = Database(db_path)

    # 0. Calculate the NEXT distinct minute index
    start_time = clock.get_time()
    next_virtual_minute = math.floor(start_time / 60) + 1

    while True:
        current_virtual = clock.get_time()

        # 1. Convert current time to a "minute progress"
        # We process while the current time is past our target minute mark
        while current_virtual >= (next_virtual_minute * 60):
            # Pass the precise timestamp (minute * 60) to the update
            _run_update(database, next_virtual_minute)

            # Increment by exactly 1 minute
            next_virtual_minute += 1

        # 3. Drift-Correcting Sleep
        # Recalculate time because run_update took execution time
        current_virtual = clock.get_time()

        # Target time in seconds is simply the minute integer * 60
        target_seconds = next_virtual_minute * 60
        virtual_seconds_until_next = target_seconds - current_virtual

        if virtual_seconds_until_next > 0:
            scale = clock.get_scale()
            # Avoid division by zero if scale is somehow 0
            if scale > 0:
                time.sleep(min(virtual_seconds_until_next / scale, 5))
                # Cap the sleep to 5s to make the app more responsive to time scale changes and time jumps
            else:
                time.sleep(5)
        # Else we are behind schedule (lagging)! Loop immediately to catch up.


class ActiveTransport(NamedTuple):
    transport_route_id: int
    transport_id: int
    start_timestamp: int
    transportation_time_minutes: int
    current_target_warehouse_id: int
    final_target_warehouse_id: int


def _run_update(database: Database, timestamp_minute: int) -> None:
    # Get all the transport routes with a null arrival time
    # Get the final destination of those transports
    # Somewhere along the line update those to have an arrival time
    # Find the shortest path and start the next transport route

    routing_graph = None

    active_transports = database.get_active_transports_event()
    for transport in active_transports:
        transport = ActiveTransport(*transport)
        if timestamp_minute - transport.start_timestamp >= transport.transportation_time_minutes:
            if routing_graph is None and transport.current_target_warehouse_id != transport.final_target_warehouse_id:
                raw_connections = database.get_routing_graph()
                routing_graph = _build_adjacency_map(raw_connections)
            _update_transport(database, timestamp_minute, transport, routing_graph)


def _update_transport(database: Database, timestamp_minute: int, transport: ActiveTransport, routing_graph) -> None:
    database.change_transport_route_arrival(transport.transport_route_id, timestamp_minute)

    if transport.current_target_warehouse_id == transport.final_target_warehouse_id:
        _unload_cargo(database, transport.final_target_warehouse_id, transport.transport_id)
    else:
        _next_transport_step(
            database,
            transport.transport_id,
            transport.current_target_warehouse_id,
            transport.final_target_warehouse_id,
            timestamp_minute,
            routing_graph
        )


def _unload_cargo(database: Database, warehouse_id: int, transport_id: int) -> None:
    cargo: list[tuple[int, int]] = database.get_cargo(transport_id)
    database.upsert_cargo(warehouse_id, cargo)


def _next_transport_step(
        database: Database,
        transport_id: int,
        current_node: int,
        target_node: int,
        current_time: int,
        routing_graph
) -> None:
    # 3. Dijkstra's Algorithm
    # Priority Queue: (accumulated_cost, current_node_id)
    pq = [(0, current_node)]

    # Track minimum cost to reach a node
    min_costs = {current_node: 0}

    # Track the path: predecessor[node] = (previous_node, connection_id_used)
    predecessors = {}

    path_found = False

    while pq:
        cost, u = heapq.heappop(pq)

        if u == target_node:
            path_found = True
            break

        if cost > min_costs.get(u, float('inf')):
            continue

        if u in routing_graph:
            for edge_cost, v, conn_id in routing_graph[u]:
                new_cost = cost + edge_cost
                if new_cost < min_costs.get(v, float('inf')):
                    min_costs[v] = new_cost
                    predecessors[v] = (u, conn_id)
                    heapq.heappush(pq, (new_cost, v))

    if not path_found:
        # Handle error: No path exists (Road deleted? Island warehouse?)
        error(f"CRITICAL: No path found for Transport {transport_id} from {current_node} to {target_node}")
        return

    # 4. Backtrack to find the IMMEDIATE next step
    # We want the connection that starts at 'current_node' and leads towards target.
    # Since 'predecessors' maps Target -> Source, we trace back from target_node.

    curr = target_node
    next_hop_connection_id = None

    while curr != current_node:
        parent, used_conn_id = predecessors[curr]
        if parent == current_node:
            # We found the first step!
            next_hop_connection_id = used_conn_id
            break
        curr = parent

    # 5. Execute the move
    if next_hop_connection_id:
        database.add_next_transport_leg(transport_id, next_hop_connection_id, current_time)


def _build_adjacency_map(connections: list[tuple[int, int, int, int]]) -> dict:
    """
    Transforms DB rows (id, source, target, time) into an adjacency dict.
    Returns: {source_id: [(cost, target_id, connection_id), ...]}
    """
    graph = {}
    for conn_id, src, tgt, cost in connections:
        if src not in graph:
            graph[src] = []
        graph[src].append((cost, tgt, conn_id))
    return graph
