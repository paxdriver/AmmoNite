# model_primitives_enhanced.py
# Generate micro / community / regional primitives with grounded bases,
# distinct materials, and labels placed exactly above each object.
# Note: does NOT clear the scene.

import bpy
from math import radians
from mathutils import Vector

# ---------------------- Materials ----------------------
def make_mat(name, color, metallic=0.0, roughness=0.5):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m

MAT_STEEL   = make_mat("Steel_MT",   (0.55, 0.60, 0.80), metallic=0.9, roughness=0.30)
MAT_SAND    = make_mat("Sand_MT",    (0.95, 0.80, 0.40), metallic=0.0, roughness=0.95)
MAT_WATER   = make_mat("Water_MT",   (0.05, 0.35, 1.00), metallic=0.0, roughness=0.05)
MAT_BRINE   = make_mat("Brine_MT",   (0.00, 0.80, 0.60), metallic=0.0, roughness=0.15)
MAT_BINDER  = make_mat("Binder_MT",  (0.90, 0.75, 0.45), metallic=0.0, roughness=0.80)
MAT_SALT    = make_mat("Salt_MT",    (1.00, 1.00, 1.00), metallic=0.0, roughness=0.30)
MAT_AMMONIA = make_mat("Ammonia_MT", (0.80, 0.80, 0.90), metallic=0.9, roughness=0.25)
MAT_MIRROR  = make_mat("Mirror_MT",  (0.98, 0.98, 1.00), metallic=1.0, roughness=0.02)
MAT_DEFAULT = make_mat("IndGrey_MT", (0.50, 0.50, 0.50), metallic=0.4, roughness=0.60)

# ---------------------- Layout -------------------------
X_SPACING = 40.0
Y_STEP    = 8.0
Z_BASE    = 0.0
GROUPS = {
    "micro": 0.0,
    "community": X_SPACING,
    "regional": X_SPACING * 2.0,
}

# ---------------------- Label helper -------------------
def add_text_label(obj, label_text, z_offset=0.2):
    """
    Place label at same X/Y as obj, at top_z + z_offset in WORLD space.
    Parent label to obj while preserving world transform.
    """
    bpy.context.view_layer.update()

    # Highest vertex in WORLD space
    top_z = max((obj.matrix_world @ v.co).z for v in obj.data.vertices)

    # Create text object
    txt_data = bpy.data.curves.new(f"{obj.name}_LabelData", type="FONT")
    txt_data.body = label_text
    txt_data.size = 0.8
    txt_data.align_x = "CENTER"
    txt_data.align_y = "CENTER"

    txt_obj = bpy.data.objects.new(f"{obj.name}_Label", txt_data)
    bpy.context.collection.objects.link(txt_obj)

    # World placement exactly above the object
    txt_obj.location = Vector((obj.location.x, obj.location.y, top_z + z_offset))
    txt_obj.rotation_euler = (radians(90.0), 0.0, radians(180.0))  # upright, readable

    # Parent and KEEP world transform
    txt_obj.parent = obj
    txt_obj.matrix_parent_inverse = obj.matrix_world.inverted()

    return txt_obj

# --------------- Mesh + grounding + label ---------------
def add_mesh_with_label(obj, name, mat, base_loc, label_text=None):
    if name in bpy.data.objects:
        print(f"Skipped duplicate: {name}")
        return bpy.data.objects[name]

    obj.name = name
    obj.location = base_loc

    # Material
    if obj.data and hasattr(obj.data, "materials"):
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
    if obj.active_material and obj.active_material.use_nodes:
        bsdf = obj.active_material.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            obj.color = bsdf.inputs["Base Color"].default_value

    # Ground the mesh (origin to bounds, base at Z=0)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    try:
        min_z = min(v.co.z for v in obj.data.vertices)
        obj.location.z -= min_z
    except Exception as e:
        print(f"Could not ground {name}: {e}")

    if label_text:
        add_text_label(obj, label_text)
    return obj

# ----------------- Build one group column ----------------
def build_group(tag, x_base):
    y = 0.0
    def next_loc():
        nonlocal y
        loc = Vector((x_base, y, Z_BASE))
        y += Y_STEP
        return loc

    def make_cylinder(local, r, h, mat, label=None):
        obj_name = f"{local}_{tag}"
        if obj_name in bpy.data.objects:
            print(f"Skipping existing {obj_name}")
            return bpy.data.objects[obj_name]
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h)
        return add_mesh_with_label(bpy.context.active_object, obj_name, mat, next_loc(), label or obj_name)

    def make_box(local, sx, sy, sz, mat, label=None):
        obj_name = f"{local}_{tag}"
        if obj_name in bpy.data.objects:
            print(f"Skipping existing {obj_name}")
            return bpy.data.objects[obj_name]
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        obj = bpy.context.active_object
        obj.scale = (sx/2.0, sy/2.0, sz/2.0)
        return add_mesh_with_label(obj, obj_name, mat, next_loc(), label or obj_name)

    def make_plane(local, sx, sy, mat, label=None):
        obj_name = f"{local}_{tag}"
        if obj_name in bpy.data.objects:
            print(f"Skipping existing {obj_name}")
            return bpy.data.objects[obj_name]
        bpy.ops.mesh.primitive_plane_add(size=1.0)
        obj = bpy.context.active_object
        obj.scale = (sx/2.0, sy/2.0, 1.0)
        return add_mesh_with_label(obj, obj_name, mat, next_loc(), label or obj_name)

    def make_cone(local, r, h, mat, label=None):
        obj_name = f"{local}_{tag}"
        if obj_name in bpy.data.objects:
            print(f"Skipping existing {obj_name}")
            return bpy.data.objects[obj_name]
        bpy.ops.mesh.primitive_cone_add(radius1=r, depth=h)
        return add_mesh_with_label(bpy.context.active_object, obj_name, mat, next_loc(), label or obj_name)

    is_micro     = (tag == "micro")
    is_community = (tag == "community")
    is_regional  = (tag == "regional")

    make_box("Electrolyzer_Skid", 4.0 if is_micro else 6.0, 2.0, 2.5, MAT_DEFAULT, "Electrolyzer")
    make_cylinder("HB_Reactor", 0.6 if is_micro else 1.0 if is_community else 1.6,
                  3.0 if is_micro else 5.0 if is_community else 6.0, MAT_STEEL, "Haber-Bosch")
    make_cylinder("Ostwald_Absorber", 1.0 if is_micro else 1.5 if is_community else 2.5,
                  5.0 if is_micro else 8.0 if is_community else 10.0, MAT_STEEL, "Ostwald")
    make_cylinder("AN_Reactor", 0.8 if is_micro else 1.2 if is_community else 1.8,
                  3.0 if is_micro else 6.0 if is_community else 7.0, MAT_STEEL, "AN Neutralizer")
    make_box("MED_Module", 3.0 if is_micro else 6.0, 1.0 if is_micro else 2.0, 1.0, MAT_DEFAULT, "MED Desal")
    make_cylinder("Mg_Binder_Tank", 0.8 if is_micro else 1.5 if is_community else 2.0,
                  2.5 if is_micro else 4.0 if is_community else 5.0, MAT_BINDER, "Mg Binder")

    make_cylinder("Sand_Heat_Storage", 1.0 if is_micro else 2.0 if is_community else 3.0,
                  5.0 if is_micro else 9.0 if is_community else 10.0, MAT_SAND, "Thermal Store")
    make_cylinder("Water_Tank", 1.5 if is_micro else 4.0 if is_community else 6.0,
                  3.0 if is_micro else 4.0 if is_community else 5.0, MAT_WATER, "Fresh Water")
    make_cylinder("Brine_Tank", 2.0 if is_micro else 5.0 if is_community else 7.0,
                  3.0 if is_micro else 3.0 if is_community else 5.0, MAT_BRINE, "Brine")
    make_cylinder("Binder_Storage", 0.8 if is_micro else 1.0 if is_community else 2.0,
                  2.0 if is_micro else 3.5 if is_community else 4.0, MAT_BINDER, "Binder Storage")
    make_cone("NaCl_Pile", 2.5 if is_micro else 5.0 if is_community else 12.5,
              2.0 if is_micro else 3.0 if is_community else 5.0, MAT_SALT, "NaCl Stock")
    make_cylinder("NH3_Tank", 0.5 if is_micro else 0.75 if is_community else 1.0,
                  2.0 if is_micro else 3.7 if is_community else 6.0, MAT_AMMONIA, "NH3 Backup")
    make_plane("Solar_Mirror", 2.5 if is_micro else 5.0,
               1.0 if is_micro else 2.5, MAT_MIRROR, "Solar Mirror")
    make_cylinder("Heat_Exchanger", 0.4 if is_micro else 0.8,
                  1.2 if is_micro else 2.0, MAT_STEEL, "Heat Exchanger")

# ------------------ Build all groups -------------------
for tag, x in GROUPS.items():
    build_group(tag, x)

print("✔ Objects created with labels placed exactly above each mesh.")