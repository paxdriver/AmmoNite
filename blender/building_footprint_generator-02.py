import bpy
import math
import random
from mathutils import Vector
import csv
from pathlib import Path

"""
The idea behind this script is simple: using the scale models built using the model_primitives_enhanced.py, which are scale meshes of equipment based on the calculations derived from a single input value of 
the plant's anticipated output. Since the ratios of production of adjacent production chains are 
relative, a single input should be able to tell us the size of the equipment we need for this sustainable
production chain.

In this script we take that equipment and place it as logically as possible in floor plans generated 
by cellular automata-like basic rules for clearances, proximity, safety, length of plumbing, etc.

See "Floorplan Generator Notes.txt"
"""

# building_footprint_generator.py
# Phase 1 of procedural plant layout within Blender.
#
# Runs *after* model_primitives_enhanced.py has created all module meshes.
# Will later fetch these objects by name, group them by scale, and lay them out
# inside reasonable building footprints.
#
# Current step: environment initialization and basic project scaffolding.

# ------------------------------------------------------------
# 1. Global parameters and constants
# ------------------------------------------------------------

SEED = 42  # deterministic layout shuffles
random.seed(SEED)

# Expected module suffixes (must match your model_primitives_enhanced.py)
MODULE_TAGS = ["micro", "community", "regional"]

# Root naming hints – these are the subsystem identifiers we expect in scene
SUBSYSTEM_NAMES = [
    "Electrolyzer",
    "HB_Reactor",
    "Ostwald_Absorber",
    "AN_Reactor",
    "MED_Module",
    "Mg_Binder_Tank",
    "Sand_Heat_Storage",
    "Water_Tank",
    "Brine_Tank",
    "Binder_Storage",
    "NaCl_Pile",
    "NH3_Tank",
    "Heat_Exchanger",
    "Solar_Mirror",
]

def log(msg: str) -> None:
    """Simple console logger for clarity."""
    print(f"[building_footprint_generator] {msg}")

def find_objects_by_tag(tag: str):
    """Return all Blender objects whose names end with the given module tag."""
    return [
        obj for obj in bpy.data.objects
        if obj.name.lower().endswith(f"_{tag.lower()}")
    ]

def list_all_module_objects():
    """Dictionary of lists, grouped by module scale."""
    sets = {}
    for tag in MODULE_TAGS:
        sets[tag] = find_objects_by_tag(tag)
        log(f"{tag}: found {len(sets[tag])} objects")
    return sets

# ------------------------------------------------------------
# Analyze dimensions and ground position of detected objects
# ------------------------------------------------------------

def get_object_dimensions_world(obj):
    """
    Return (width, depth, height) of the object's world‑space bounding box,
    and the min_z (bottom elevation) for grounding.
    """
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)
    width  = max_x - min_x
    depth  = max_y - min_y
    height = max_z - min_z
    return width, depth, height, min_z


def describe_module_objects(module_tag="micro"):
    """
    Collects all *_<module_tag> objects, reports sizes, and prepares a data list.
    """
    objs = find_objects_by_tag(module_tag)
    info_list = []

    for obj in objs:
        w, d, h, z = get_object_dimensions_world(obj)
        info = {
            "name": obj.name,
            "width_m": round(w, 3),
            "depth_m": round(d, 3),
            "height_m": round(h, 3),
            "bottom_z_m": round(z, 3),
        }
        info_list.append(info)
        log(
            f"{obj.name:25s} | W={w:4.1f} m D={d:4.1f} m H={h:4.1f} m  "
            f"Zbase={z:5.2f}"
        )
    return info_list

# ------------------------------------------------------------
# Step 3: Grounding and simple grid placement
# ------------------------------------------------------------

START_X = 0.0
START_Y = 0.0
AISLE_X = 3.0  # spacing between columns (m)
AISLE_Y = 3.0  # spacing between rows (m)
MAX_ROW_WIDTH = 20.0  # how far X extends before starting a new row


def ground_object(obj):
    """Translate object vertically so its lowest point rests on Z=0."""
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_z = min(v.z for v in bbox)
    if abs(min_z) > 1e-5:
        obj.location.z -= min_z


def layout_module_objects(module_tag="micro"):
    """Arrange all *_module_tag objects in a simple visible grid."""
    objs = find_objects_by_tag(module_tag)
    random.shuffle(objs)

    cursor_x = START_X
    cursor_y = START_Y
    max_depth_this_row = 0.0

    for obj in objs:
        # skip non‑equipment objects
        if obj.name in {"GROUND", "Camera", "Sun"}:
            continue

        w, d, h, _ = get_object_dimensions_world(obj)
        ground_object(obj)

        obj.location.x = cursor_x + w / 2.0
        obj.location.y = cursor_y + d / 2.0

        cursor_x += w + AISLE_X
        max_depth_this_row = max(max_depth_this_row, d)

        # new row if line exceeds allowed width
        if cursor_x > MAX_ROW_WIDTH:
            cursor_x = START_X
            cursor_y += max_depth_this_row + AISLE_Y
            max_depth_this_row = 0.0

    log(f"Layout complete for '{module_tag}' group.")


# ------------------------------------------------------------
# Step 4: Zone-based placement
# ------------------------------------------------------------

ZONE_GAP_Y = 10.0  # spacing between zones (in metres)
ZONE_OFFSET_X = 0.0
ZONE_AISLE_X = 2.5
ZONE_AISLE_Y = 2.5

ZONE_MAP = {
    # Process Core
    "Zone_A_Process": [
        "HB_Reactor",
        "Ostwald_Absorber",
        "AN_Reactor",
    ],
    # Utilities (heat, water, binder)
    "Zone_B_Utilities": [
        "Electrolyzer",
        "Heat_Exchanger",
        "MED_Module",
        "Mg_Binder_Tank",
        "Sand_Heat_Storage",
    ],
    # Storage and Yard
    "Zone_C_Storage": [
        "Water_Tank",
        "Brine_Tank",
        "Binder_Storage",
        "NaCl_Pile",
        "NH3_Tank",
    ],
    # Solar Field / External
    "Zone_D_Solar": [
        "Solar_Mirror",
    ],
}


def assign_zone(obj_name: str) -> str:
    """Return which zone this object name belongs to."""
    for zone, patterns in ZONE_MAP.items():
        for p in patterns:
            if p.lower() in obj_name.lower():
                return zone
    return "Zone_Unassigned"


def layout_by_zones(module_tag="micro"):
    """Lay out each *_module_tag object within its zone band."""
    objs = find_objects_by_tag(module_tag)
    zones = {}

    # Group objects by zone
    for obj in objs:
        z_name = assign_zone(obj.name)
        if z_name not in zones:
            zones[z_name] = []
        zones[z_name].append(obj)

    # Arrange each zone separately
    current_y = 0.0
    for z_name, group in zones.items():
        cursor_x = ZONE_OFFSET_X
        max_depth = 0.0
        log(f"Laying out {z_name}: {len(group)} items")
        for obj in group:
            w, d, h, _ = get_object_dimensions_world(obj)
            ground_object(obj)
            obj.location.x = cursor_x + w / 2.0
            obj.location.y = current_y + d / 2.0
            cursor_x += w + ZONE_AISLE_X
            max_depth = max(max_depth, d)
        current_y += max_depth + ZONE_GAP_Y
    log("Zone-based layout complete.")
    

# ------------------------------------------------------------
# Step 5: Visualize zone footprints and clearances
# ------------------------------------------------------------

CLEARANCE_MARGIN = 1.5  # metres around objects
FLOOR_Z_OFFSET = -0.02  # push slightly below GROUND so it doesn’t flicker

def get_zone_bounds(obj_list):
    """Return (min_x, max_x, min_y, max_y) in world space for a list of objects."""
    if not obj_list:
        return (0, 0, 0, 0)
    xs, ys = [], []
    for obj in obj_list:
        for v in (obj.matrix_world @ Vector(corner) for corner in obj.bound_box):
            xs.append(v.x)
            ys.append(v.y)
    return min(xs), max(xs), min(ys), max(ys)


def make_zone_floor(name, bounds, color=(0.6, 0.6, 0.6, 0.3)):
    """Create a semi‑transparent plane covering the zone bounds."""
    min_x, max_x, min_y, max_y = bounds
    width = max_x - min_x
    depth = max_y - min_y
    cx = (max_x + min_x) / 2.0
    cy = (max_y + min_y) / 2.0

    bpy.ops.mesh.primitive_plane_add(size=1)
    floor = bpy.context.active_object
    floor.name = name
    floor.scale = (width / 2.0, depth / 2.0, 1)
    floor.location = Vector((cx, cy, FLOOR_Z_OFFSET))

    # Transparent material
    mat = bpy.data.materials.new(name=f"{name}_MAT")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Alpha"].default_value = color[3]
    mat.blend_method = 'BLEND'
    floor.data.materials.append(mat)
    return floor


def visualize_zone_clearances(module_tag="micro"):
    """Generate floor planes showing each zone’s footprint + clearance."""
    objs = find_objects_by_tag(module_tag)

    # Group by previously defined zones
    zone_groups = {}
    for o in objs:
        z = assign_zone(o.name)
        zone_groups.setdefault(z, []).append(o)

    palette = {
        "Zone_A_Process": (0.9, 0.4, 0.4, 0.3),
        "Zone_B_Utilities": (0.4, 0.6, 0.9, 0.3),
        "Zone_C_Storage": (0.4, 0.9, 0.6, 0.3),
        "Zone_D_Solar": (0.95, 0.95, 0.45, 0.25),
        "Zone_Unassigned": (0.8, 0.8, 0.8, 0.3),
    }

    for zone_name, group in zone_groups.items():
        if not group:
            continue
        min_x, max_x, min_y, max_y = get_zone_bounds(group)
        bounds_expanded = (
            min_x - CLEARANCE_MARGIN,
            max_x + CLEARANCE_MARGIN,
            min_y - CLEARANCE_MARGIN,
            max_y + CLEARANCE_MARGIN,
        )
        color = palette.get(zone_name, (0.5, 0.5, 0.5, 0.3))
        make_zone_floor(f"ZoneFloor_{zone_name}", bounds_expanded, color)

    log("Zone‑footprint floors generated.")


# ------------------------------------------------------------
# Step 6: Generate inter-zone aisles and walkways
# ------------------------------------------------------------

AISLE_COLOR = (0.9, 0.9, 0.3, 0.35)  # pale yellow
AISLE_Z_OFFSET = -0.01               # slightly above zone floor
WALKWAY_WIDTH_M = 2.0
ROAD_WIDTH_M = 4.0

def make_aisle_plane(name, x_min, x_max, y_min, y_max, color=AISLE_COLOR):
    """Create a rectangular mesh for aisles/walkways."""
    bpy.ops.mesh.primitive_plane_add(size=1)
    obj = bpy.context.active_object
    obj.name = name
    w = x_max - x_min
    d = y_max - y_min
    cx = (x_max + x_min) / 2.0
    cy = (y_max + y_min) / 2.0
    obj.scale = (w / 2.0, d / 2.0, 1.0)
    obj.location = Vector((cx, cy, AISLE_Z_OFFSET))

    mat = bpy.data.materials.new(name=f"{name}_MAT")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Alpha"].default_value = color[3]
    mat.blend_method = 'BLEND'
    obj.data.materials.append(mat)
    return obj


def add_inter_zone_walkways(module_tag="micro"):
    """Generate walkway / road rectangles between each pair of zones."""
    objs = find_objects_by_tag(module_tag)
    zone_groups = {}
    for o in objs:
        z = assign_zone(o.name)
        zone_groups.setdefault(z, []).append(o)

    # compute bounding boxes per zone
    zone_ranges = []
    for z, g in zone_groups.items():
        if not g:
            continue
        min_x, max_x, min_y, max_y = get_zone_bounds(g)
        zone_ranges.append((z, min_x, max_x, min_y, max_y))

    # sort by Y coordinate (top to bottom)
    zone_ranges.sort(key=lambda r: r[3])  # sort by min_y

    # create vertical gaps
    for i in range(len(zone_ranges) - 1):
        upper = zone_ranges[i]
        lower = zone_ranges[i + 1]
        y_top = upper[4]   # max_y of upper zone
        y_bot = lower[3]   # min_y of next zone
        gap_height = y_bot - y_top
        if gap_height < 0.5:
            continue  # overlap or negligible
        # determine width across both zones
        x_min = min(upper[1], lower[1]) - 1.0
        x_max = max(upper[2], lower[2]) + 1.0
        y_min = y_top + gap_height / 2.0 - (WALKWAY_WIDTH_M / 2.0)
        y_max = y_min + WALKWAY_WIDTH_M
        name = f"Aisle_{upper[0]}_to_{lower[0]}"
        make_aisle_plane(name, x_min, x_max, y_min, y_max)

    log("Inter‑zone walkway planes created.")
    
    
 # ------------------------------------------------------------
# Step 7: Equipment adjacency and proximity graph
# ------------------------------------------------------------

# Basic adjacency preferences (seed list, tune later)
ADJACENCY_RULES = [
    ("HB_Reactor", "Ostwald_Absorber", 3.0, 2.0, 2.0),  # near
    ("Ostwald_Absorber", "AN_Reactor", 4.0, 2.0, 2.0),  # near
    ("Electrolyzer", "HB_Reactor", 5.0, 3.0, 1.5),      # moderately near
    ("MED_Module", "Brine_Tank", 3.0, 2.0, 1.0),
    ("Water_Tank", "Brine_Tank", 4.0, 2.0, 1.0),
    ("NaCl_Pile", "Brine_Tank", 6.0, 3.0, 0.8),
    ("NH3_Tank", "AN_Reactor", 8.0, 3.0, 1.2),
]

def get_center_xy(obj):
    """Return world‑space (x,y) center coordinate."""
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    cx = sum(v.x for v in bbox) / 8.0
    cy = sum(v.y for v in bbox) / 8.0
    return cx, cy


def build_adjacency_graph(module_tag="micro", export_csv=True):
    """Build a proximity graph between relevant equipment pairs."""
    objs = find_objects_by_tag(module_tag)
    name_lookup = {o.name: o for o in objs}

    results = []
    for eq_a, eq_b, pref, tol, w in ADJACENCY_RULES:
        a_obj = next((o for o in objs if eq_a.lower() in o.name.lower()), None)
        b_obj = next((o for o in objs if eq_b.lower() in o.name.lower()), None)
        if not a_obj or not b_obj:
            continue
        xa, ya = get_center_xy(a_obj)
        xb, yb = get_center_xy(b_obj)
        dist = ((xa - xb) ** 2 + (ya - yb) ** 2) ** 0.5
        deviation = abs(dist - pref)
        penalty = max(0.0, deviation - tol) * w
        results.append(
            {
                "Equipment_A": a_obj.name,
                "Equipment_B": b_obj.name,
                "Distance_m": round(dist, 2),
                "Preferred_m": pref,
                "Tolerance_m": tol,
                "Weight": w,
                "Penalty": round(penalty, 3),
            }
        )

    total_penalty = sum(r["Penalty"] for r in results)
    log(f"Adjacency graph built for {len(results)} pairs. Total penalty = {total_penalty:.3f}")

    if export_csv:
        fname = Path(bpy.path.abspath("//")) / f"adjacency_report_{module_tag}.csv"
        with open(fname, "w", newline="") as f:
            wtr = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            wtr.writeheader()
            wtr.writerows(results)
        log(f"CSV written: {fname}")

    return results

# ------------------------------------------------------------
# Step 8.1 (refined): Safe duplicate handling for AutoLayout collection
# ------------------------------------------------------------

def duplicate_for_autolayout(module_tag="micro", reset_existing_layout=True):
    """
    Prepare the working duplicates inside 'AutoLayout_<tag>' collection.

    Logic:
      - If collection doesn't exist → create it.
      - If it exists and already has objects → remove and rebuild (reset).
      - If it exists but is empty → fill it.
    Pass reset_existing_layout=False to keep the existing duplicates.
    """
    src_objs = find_objects_by_tag(module_tag)
    if not src_objs:
        log(f"No source objects found for {module_tag}.")
        return []

    coll_name = f"AutoLayout_{module_tag}"

    # Check for existing collection
    if coll_name in bpy.data.collections:
        coll = bpy.data.collections[coll_name]
        has_contents = len(coll.objects) > 0
        if has_contents and reset_existing_layout:
            log(f"Resetting existing '{coll_name}' duplicates.")
            for o in list(coll.objects):
                coll.objects.unlink(o)
                bpy.data.objects.remove(o, do_unlink=True)
        elif has_contents and not reset_existing_layout:
            log(f"Reusing existing '{coll_name}' with {len(coll.objects)} objects.")
            return list(coll.objects)
    else:
        coll = bpy.data.collections.new(coll_name)
        bpy.context.scene.collection.children.link(coll)
        log(f"Created new collection '{coll_name}'.")

    # Create new duplicates
    dupes = []
    for obj in src_objs:
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.name = f"{obj.name}_AL"
        coll.objects.link(new_obj)
        dupes.append(new_obj)

    log(f"Duplicated {len(dupes)} objects into '{coll_name}'.")
    return dupes

# ------------------------------------------------------------
# HIDE ORIGINAL MESHES FROM OUTPUT SO THEY'RE NOT BEING DESTROYED OR OBSTRUCTING THE VIEW
def hide_original_meshes(module_tag="micro"):
    """Hide the base *_<tag> objects (viewport + render)."""
    for obj in find_objects_by_tag(module_tag):
        obj.hide_viewport = True
        obj.hide_render = True
    log(f"Hidden originals for {module_tag}")
# ------------------------------------------------------------

# ------------------------------------------------------------
# Step 8.2: Perform one optimization pass
# ------------------------------------------------------------

NUDGE_LIMIT_M = 0.5   # max move per iteration
ITER_LIMIT = 10       # overall iteration cap

def get_distance_and_vector(a, b):
    """Return planar distance and normalized (x,y) direction vector A->B."""
    xa, ya = get_center_xy(a)
    xb, yb = get_center_xy(b)
    dx, dy = xb - xa, yb - ya
    dist = (dx**2 + dy**2)**0.5
    if dist < 1e-6:
        return 0.0, (0.0, 0.0)
    return dist, (dx / dist, dy / dist)

def nudge_objects_toward_targets(objs, adjacency):
    """One iteration of adjustment according to adjacency rules."""
    moved = {}
    for rule in adjacency:
        a_name, b_name = rule["Equipment_A"], rule["Equipment_B"]
        pref = rule["Preferred_m"]
        tol = rule["Tolerance_m"]

        a = next((o for o in objs if a_name in o.name), None)
        b = next((o for o in objs if b_name in o.name), None)
        if not a or not b:
            continue

        dist, (dx, dy) = get_distance_and_vector(a, b)
        delta = 0.0
        if dist > pref + tol:
            delta = -min(NUDGE_LIMIT_M, (dist - (pref + tol)) * 0.5)
        elif dist < pref - tol:
            delta = min(NUDGE_LIMIT_M, ((pref - tol) - dist) * 0.5)
        else:
            continue  # within tolerance

        # apply half movement to each, opposite directions
        a.location.x += dx * delta
        a.location.y += dy * delta
        b.location.x -= dx * delta
        b.location.y -= dy * delta

        moved[(a_name, b_name)] = round(delta, 3)

    return moved

# ------------------------------------------------------------
# Step 8.3: Iterative optimization loop
# ------------------------------------------------------------

def optimize_layout(module_tag="micro", max_iter=ITER_LIMIT, reset_existing_layout=True):
    """Run iterative optimization to reduce adjacency penalty."""
    
    log(f"Starting optimization for {module_tag} (max {max_iter} iterations)")
    dupes = duplicate_for_autolayout(module_tag, reset_existing_layout)
    hide_original_meshes(module_tag)

    # initial score
    base_graph = build_adjacency_graph(module_tag, export_csv=False)
    best_penalty = sum(r["Penalty"] for r in base_graph)

    for iteration in range(1, max_iter + 1):
        adjacency = build_adjacency_graph(module_tag, export_csv=False)
        moved = nudge_objects_toward_targets(dupes, adjacency)
        new_graph = build_adjacency_graph(module_tag, export_csv=False)
        new_penalty = sum(r["Penalty"] for r in new_graph)
        log(f"Iter {iteration}: penalty {best_penalty:.3f} -> {new_penalty:.3f} | moves={len(moved)}")

        if new_penalty < best_penalty - 1e-3:
            best_penalty = new_penalty
        else:
            log("No improvement beyond threshold. Stopping.")
            break

    log(f"Final optimized penalty: {best_penalty:.3f}")
    return best_penalty


# ------------------------------------------------------------
# 
# ------------------------------------------------------------

if __name__ == "__main__":
    log("Initialization check starting...")
    all_sets = list_all_module_objects()
    total = sum(len(v) for v in all_sets.values())
    log(f"Total objects detected: {total}")
    log("Initialization complete.")
    
    log("Step 2: Collecting and analyzing object geometry...")
    objs_info = describe_module_objects("micro")
    log(f"Analyzed {len(objs_info)} objects.")
    log("Geometry analysis complete.")
    
    log("Step 3: Grounding and grid placement...")
    layout_module_objects("micro")
    log("Step 3 complete.  Inspect layout in top/side views.")

    log("Step 4: Zone-based placement...")
    layout_by_zones("micro")
    log("Step 4 complete. Inspect layout zones in top view.")

    log("Step 5: Visualizing zone clearances...")
    visualize_zone_clearances("micro")
    log("Step 5 complete.  Top‑down view now shows colored zone areas.")
    
    log("Step 6: Adding inter-zone walkways...")
    add_inter_zone_walkways("micro")
    log("Step 6 complete. Inspect top view for aisle bands.")
    
    #Each piece of equipment is a node.
    #Each relationship (e.g., “HB_Reactor ↔ Ostwald_Absorber”) is an edge with:
    #- preferred_distance_m
    #- tolerance_m
    #- weight (penalty for deviation).
    log("Step 7: Building adjacency graph...")
    build_adjacency_graph("micro")
    log("Pipeline complete.")
    
    log("Step 8: Optimization pass...")
    # First run reset_existing_layout=False, 
    # subsequent runs reset_existing_layout=True to avoid duplication of collection
    #    NOTE: reset_existing_layout can be omitted if no override is required
    optimize_layout("micro", max_iter=10, reset_existing_layout=False) 
    log("Step 8 complete.")