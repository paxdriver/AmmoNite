# model_primitives.py
# Run inside Blender's scripting workspace (uses bpy) to jumpstart the 3D modelling process of optional plant scales
# Phase 3 of AmmoNite project is visualizing and organizing the same for containers and vessels for sense of scale

import bpy
from math import radians

# --- Clear existing demo objects (optional)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Simple material helper ---------------------------------------------
def make_mat(name, color):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    return m

# color palette
MAT_STEEL = make_mat("Steel", (0.6, 0.6, 0.65))
MAT_SAND = make_mat("Sand", (0.9, 0.8, 0.5))
MAT_WATER = make_mat("Water", (0.4, 0.6, 1.0))
MAT_BRINE = make_mat("Brine", (0.3, 0.7, 0.7))
MAT_BINDER = make_mat("Binder", (0.8, 0.7, 0.5))
MAT_SALT = make_mat("Salt", (1.0, 1.0, 1.0))
MAT_AMMONIA = make_mat("Ammonia", (0.8, 0.8, 0.9))
MAT_MIRROR = make_mat("Mirror", (0.9, 0.9, 0.95))
MAT_DEFAULT = make_mat("DefaultGrey", (0.5, 0.5, 0.5))

# --- placement offsets --------------------------------------------------
X_SPACING = 40.0   # between micro / community / regional groups
Y_STEP = 8.0       # vertical placement spacing inside each group
Z_BASE = 0.0

GROUPS = {
    "micro": 0.0,
    "community": X_SPACING,
    "regional": X_SPACING * 2.0,
}

# --- convenience --------------------------------------------------------
def add(obj, name, mat, dx=0, dy=0, dz=0):
    obj.name = name
    bpy.context.collection.objects.link(obj)
    obj.location = (dx, dy, dz)
    if obj.data and hasattr(obj.data, "materials"):
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
    return obj


# --- create one representative of each major item -----------------------
def build_group(tag, x_base):

    y = 0.0   # start row counter per group

    def add_cylinder(name, r, h, mat):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h)
        obj = bpy.context.active_object
        obj.rotation_euler[0] = radians(0)
        add(obj, f"{name}_{tag}", mat, x_base, y, Z_BASE)
        nonlocal y
        y += Y_STEP
        return obj

    def add_box(name, sx, sy, sz, mat):
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        obj.scale = (sx / 2, sy / 2, sz / 2)
        add(obj, f"{name}_{tag}", mat, x_base, y, Z_BASE)
        nonlocal y
        y += Y_STEP
        return obj

    def add_plane(name, sx, sy, mat):
        bpy.ops.mesh.primitive_plane_add(size=1)
        obj = bpy.context.active_object
        obj.scale = (sx / 2, sy / 2, 1)
        add(obj, f"{name}_{tag}", mat, x_base, y, Z_BASE)
        nonlocal y
        y += Y_STEP
        return obj

    def add_cone(name, r, h, mat):
        bpy.ops.mesh.primitive_cone_add(radius1=r, depth=h)
        obj = bpy.context.active_object
        add(obj, f"{name}_{tag}", mat, x_base, y, Z_BASE)
        nonlocal y
        y += Y_STEP
        return obj

    # ---- major process components ----
    add_box("Electrolyzer_Skid", 6, 2, 2.5, MAT_DEFAULT)
    add_cylinder("HB_Reactor", 0.6 if tag=="micro" else 1.0 if tag=="community" else 1.6,
                 3 if tag=="micro" else 5 if tag=="community" else 6, MAT_STEEL)
    add_cylinder("Ostwald_Absorber", 1 if tag=="micro" else 1.5 if tag=="community" else 2.5,
                 5 if tag=="micro" else 8 if tag=="community" else 10, MAT_STEEL)
    add_cylinder("AN_Reactor", 0.8 if tag=="micro" else 1.2 if tag=="community" else 1.8,
                 3 if tag=="micro" else 6 if tag=="community" else 7, MAT_STEEL)
    add_box("MED_Module", 3 if tag=="micro" else 6, 1 if tag=="micro" else 2, 1.0, MAT_DEFAULT)
    add_cylinder("Mg_Binder_Tank", 0.8 if tag=="micro" else 1.5 if tag=="community" else 2.0,
                 2.5 if tag=="micro" else 4.0 if tag=="community" else 5.0, MAT_BINDER)

    # ---- storage and ancillary ----
    add_cylinder("Sand_Heat_Storage", 1.0 if tag=="micro" else 2.0 if tag=="community" else 3.0,
                 5 if tag=="micro" else 9 if tag=="community" else 10, MAT_SAND)
    add_cylinder("Water_Tank", 1.5 if tag=="micro" else 4.0 if tag=="community" else 6.0,
                 3 if tag=="micro" else 4.0 if tag=="community" else 5.0, MAT_WATER)
    add_cylinder("Brine_Tank", 2.0 if tag=="micro" else 5.0 if tag=="community" else 7.0,
                 3 if tag=="micro" else 3.0 if tag=="community" else 5.0, MAT_BRINE)
    add_cylinder("Binder_Storage", 0.8 if tag=="micro" else 1.0 if tag=="community" else 2.0,
                 2 if tag=="micro" else 3.5 if tag=="community" else 4.0, MAT_BINDER)
    add_cone("NaCl_Pile", 2.5 if tag=="micro" else 5.0 if tag=="community" else 12.5,
             2 if tag=="micro" else 3 if tag=="community" else 5, MAT_SALT)
    add_cylinder("NH3_Tank", 0.5 if tag=="micro" else 0.75 if tag=="community" else 1.0,
                 2 if tag=="micro" else 3.7 if tag=="community" else 6.0, MAT_AMMONIA)
    add_plane("Solar_Mirror", 2.5 if tag=="micro" else 5.0, 1 if tag=="micro" else 2.5, MAT_MIRROR)
    add_cylinder("Heat_Exchanger", 0.4 if tag=="micro" else 0.8,
                 1.2 if tag=="micro" else 2.0, MAT_STEEL)

# --- Create all three groups ------------------------------------------------
for tag, xoffset in GROUPS.items():
    build_group(tag, xoffset)

print("✔ Facility primitives created.  Objects grouped at X offsets:", GROUPS)