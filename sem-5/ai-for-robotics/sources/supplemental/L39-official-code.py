"""
GNSS-Based Road Navigation Workflow
-----------------------------------
Lecture: Introduction to Applications of AI in Robotics
Module:  AI for Robot Kinematics / Path Planning

Demonstrates the full pipeline from a raw GNSS fix to a waypoint route:

    Destination Selection
          -> GNSS Localization
          -> Map Matching            (snap fix to nearest road node)
          -> Road Network Graph      (nodes = intersections, edges = roads)
          -> Path Planning (A*)      (same A* students already know)
          -> Waypoint Generation
          -> Waypoint Tracking

This mirrors the road network and A* logic used in the interactive HTML
demo shown in class, so the two can be presented side by side: the HTML
for visualization, this script for the "here's the actual algorithm" slide.

Self-contained, no external dependencies beyond the Python standard library.
"""

import heapq
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. ROAD NETWORK
#    Nodes are intersections (x, y are plotting coordinates, not real GPS).
#    Edges are road segments; weight = travel distance in km.
# ---------------------------------------------------------------------------

NODES: Dict[str, Tuple[float, float]] = {
    "N1":  (90,  110),
    "N2":  (290,  95),
    "N3":  (490,  85),
    "N4":  (700, 105),   # Airport
    "N5":  (110, 270),
    "N6":  (310, 260),
    "N7":  (510, 250),
    "N8":  (700, 280),   # Stadium
    "N9":  (140, 430),   # Hospital
    "N10": (330, 420),
    "N11": (530, 410),
    "N12": (710, 440),   # Mall
}

NODE_LABELS = {"N4": "Airport", "N8": "Stadium", "N9": "Hospital", "N12": "Mall"}

EDGE_DEFS: List[Tuple[str, str]] = [
    ("N1", "N2"), ("N2", "N3"), ("N3", "N4"),
    ("N1", "N5"), ("N2", "N6"), ("N3", "N7"), ("N4", "N8"),
    ("N5", "N6"), ("N6", "N7"), ("N7", "N8"),
    ("N5", "N9"), ("N6", "N10"), ("N7", "N11"), ("N8", "N12"),
    ("N9", "N10"), ("N10", "N11"), ("N11", "N12"),
    ("N2", "N7"), ("N6", "N11"),   # diagonal shortcuts
]

DESTINATIONS = {"Airport": "N4", "Stadium": "N8", "Hospital": "N9", "Mall": "N12"}


def euclidean(a: str, b: str) -> float:
    """Straight-line distance between two nodes, scaled to look like km."""
    ax, ay = NODES[a]
    bx, by = NODES[b]
    return math.hypot(ax - bx, ay - by) / 100.0


def build_adjacency(edge_defs: List[Tuple[str, str]]) -> Dict[str, List[Tuple[str, float]]]:
    """Undirected weighted adjacency list. Weight = edge length in km."""
    adj: Dict[str, List[Tuple[str, float]]] = {n: [] for n in NODES}
    for a, b in edge_defs:
        w = round(euclidean(a, b), 2)
        adj[a].append((b, w))
        adj[b].append((a, w))
    return adj


ADJACENCY = build_adjacency(EDGE_DEFS)


# ---------------------------------------------------------------------------
# 2. GNSS LOCALIZATION
#    Simulates a noisy fix around a fixed true position, the way a real
#    receiver's reported position jitters fix-to-fix (multipath, atmospheric
#    delay, receiver noise, etc).
# ---------------------------------------------------------------------------

LAT0, LON0 = 28.6139, 77.2090   # arbitrary reference origin for fake lat/lon

# Bounding box of the road network (with a margin), computed from the node
# coordinates -- the GNSS fix is sampled uniformly anywhere inside this box,
# so the vehicle can "start" near any part of the map, not just one fixed
# spot. Mirrors MAP_BOUNDS in the HTML demo.
_MARGIN = 40.0
_xs = [x for x, y in NODES.values()]
_ys = [y for x, y in NODES.values()]
MAP_BOUNDS = {
    "x_min": min(_xs) - _MARGIN, "x_max": max(_xs) + _MARGIN,
    "y_min": min(_ys) - _MARGIN, "y_max": max(_ys) + _MARGIN,
}


def acquire_gnss_fix() -> Tuple[float, float]:

    x = random.uniform(MAP_BOUNDS["x_min"], MAP_BOUNDS["x_max"])
    y = random.uniform(MAP_BOUNDS["y_min"], MAP_BOUNDS["y_max"])
    return x, y


def to_fake_latlon(x: float, y: float) -> Tuple[float, float]:
    """Cosmetic conversion so printed output reads like a real GNSS fix."""
    lat = LAT0 + (300 - y) * 0.00006
    lon = LON0 + (x - 300) * 0.00006
    return round(lat, 5), round(lon, 5)


# ---------------------------------------------------------------------------
# 3. MAP MATCHING
#    Simplification used in this lecture: snap the fix to the nearest road
#    NODE. Production systems instead project the fix onto the nearest road
#    SEGMENT and disambiguate among candidate roads using heading and recent
#    trajectory history -- worth mentioning, not deriving, in class.
# ---------------------------------------------------------------------------

def map_match(fix: Tuple[float, float]) -> str:
    """Return the id of the nearest road node to a raw GNSS fix."""
    fx, fy = fix
    best_node, best_dist = None, math.inf
    for node_id, (nx, ny) in NODES.items():
        d = math.hypot(nx - fx, ny - fy)
        if d < best_dist:
            best_node, best_dist = node_id, d
    return best_node


# ---------------------------------------------------------------------------
# 4. PATH PLANNING -- A*
#    Standard A* over the road graph. Students have already implemented this
#    for grid/config-space search in earlier lectures; here the only change
#    is what the graph represents (intersections and roads, not grid cells).
# ---------------------------------------------------------------------------

@dataclass(order=True)
class _PQItem:
    f: float
    id: str = field(compare=False)
    g: float = field(compare=False)


def heuristic(a: str, b: str) -> float:
    return euclidean(a, b)


def astar(start: str, goal: str, verbose: bool = True) -> Optional[List[str]]:
    """A* search over ADJACENCY. Returns the node sequence start -> goal,
    or None if no path exists."""
    open_heap: List[_PQItem] = [_PQItem(f=heuristic(start, goal), id=start, g=0.0)]
    g_score: Dict[str, float] = {start: 0.0}
    came_from: Dict[str, str] = {}
    closed = set()

    while open_heap:
        current = heapq.heappop(open_heap)
        if current.id in closed:
            continue
        closed.add(current.id)

        if verbose:
            print(f"  expand {current.id:<4} g={current.g:5.2f}  "
                  f"h={heuristic(current.id, goal):5.2f}  f={current.f:5.2f}")

        if current.id == goal:
            path = [goal]
            node = goal
            while node in came_from:
                node = came_from[node]
                path.append(node)
            path.reverse()
            return path

        for neighbor, weight in ADJACENCY[current.id]:
            if neighbor in closed:
                continue
            tentative_g = current.g + weight
            if tentative_g < g_score.get(neighbor, math.inf):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current.id
                f = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, _PQItem(f=f, id=neighbor, g=tentative_g))

    return None  # no path found


# ---------------------------------------------------------------------------
# 5. WAYPOINT GENERATION
#    Convert the A* node sequence into an ordered waypoint list with
#    cumulative distance -- what the controller in Step 7 will actually use.
# ---------------------------------------------------------------------------

@dataclass
class Waypoint:
    index: int
    node_id: str
    label: Optional[str]
    cumulative_km: float


def build_waypoints(path: List[str]) -> List[Waypoint]:
    waypoints = []
    cumulative = 0.0
    for i, node_id in enumerate(path):
        if i > 0:
            cumulative += euclidean(path[i - 1], node_id)
        waypoints.append(Waypoint(
            index=i + 1,
            node_id=node_id,
            label=NODE_LABELS.get(node_id),
            cumulative_km=round(cumulative, 2),
        ))
    return waypoints


# ---------------------------------------------------------------------------
# 6. WAYPOINT TRACKING (minimal illustration)
#    A full controller belongs in the control-systems lecture; here we just
#    show how the current waypoint index advances as the vehicle progresses,
#    to close the loop back to GNSS.
# ---------------------------------------------------------------------------

def current_waypoint(waypoints: List[Waypoint], distance_travelled_km: float) -> Waypoint:
    """Return the next not-yet-reached waypoint given distance travelled."""
    for wp in waypoints:
        if wp.cumulative_km >= distance_travelled_km - 1e-6:
            return wp
    return waypoints[-1]


# ---------------------------------------------------------------------------
# EXAMPLE USAGE
# ---------------------------------------------------------------------------

def run_pipeline(destination_name: str = "Airport", verbose_astar: bool = True) -> None:
    """Run all 7 steps once, end to end, printing each stage's output.
    Each call samples a fresh, randomly located GNSS fix -- run this cell
    multiple times in Colab and watch Step 3 resolve to a different start
    node each time."""

    # Step 1: Destination Selection
    goal_node = DESTINATIONS[destination_name]
    print(f"Step 1 - Destination Selection: '{destination_name}' -> node {goal_node}")

    # Step 2: GNSS Localization

    fix = acquire_gnss_fix()

    lat, lon = to_fake_latlon(*fix)

    print(f"\nStep 2 - GNSS Localization: fix=({fix[0]:.1f}, {fix[1]:.1f})  "
          f"lat={lat}  lon={lon}")

    # Step 3: Map Matching

    start_node = map_match(fix)

    print(f"\nStep 3 - Map Matching: nearest road node = {start_node}")

    # Step 4: Road Network Graph (just report its size here; the HTML demo
    # renders it visually)

    print(f"\nStep 4 - Road Network Graph: {len(NODES)} nodes, {len(EDGE_DEFS)} edges")

    # Step 5: Path Planning (A*)

    print(f"\nStep 5 - Path Planning (A*): searching {start_node} -> {goal_node}")

    path = astar(start_node, goal_node, verbose=verbose_astar)

    if path is None:
        raise RuntimeError("No path found between start and goal nodes.")
    print(f"  shortest path: {' -> '.join(path)}")

    # Step 6: Waypoint Generation

    waypoints = build_waypoints(path)

    print("\nStep 6 - Waypoint Generation:")

    for wp in waypoints:
        label = f" ({wp.label})" if wp.label else ""
        print(f"  WP{wp.index}: {wp.node_id}{label}  -- {wp.cumulative_km} km")

    # Step 7: Waypoint Tracking (illustrative snapshot at 60% of the route)
    total_km = waypoints[-1].cumulative_km
    travelled = 0.6 * total_km
    active = current_waypoint(waypoints, travelled)
    print(f"\nStep 7 - Waypoint Tracking: after {travelled:.2f} km travelled, "
          f"current target is WP{active.index} ({active.node_id})")


if __name__ == "__main__":
    # Single full run, with the A* expansion log printed step by step.
    run_pipeline("Airport")

    # Bonus: run the pipeline a few more times with no A* log, to show the
    # GNSS fix (and therefore the start node and route) changing each time
    # this cell is re-run -- paste this loop in its own Colab cell to
    # demonstrate randomness quickly.
    print("\n" + "=" * 60)
    print("Three more random fixes -> three different starting nodes:")
    print("=" * 60)
    for i in range(3):
        fix = acquire_gnss_fix()
        start_node = map_match(fix)
        print(f"  run {i+1}: fix=({fix[0]:.1f}, {fix[1]:.1f})  -> matched node {start_node}")