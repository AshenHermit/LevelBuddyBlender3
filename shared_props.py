import argparse
from functools import partial
import os
import traceback
import bpy
import bmesh
import addon_utils
from bpy_extras.io_utils import ImportHelper

recursion_locked = False
def anti_recursive_set(obj, key, value, add=False):
    global recursion_locked
    if not recursion_locked:
        recursion_locked = True
        if add: value = getattr(obj, key) + value
        if type(key) is str:
            setattr(obj, key, value)
        elif type(key) is int: obj[key] = value
        recursion_locked = False
        return True
    return False

def share_var_with_objects(actobj=None, selected=None, var_key=None, relative=False):
    
    if actobj is None or selected is None or var_key is None: return
    if not hasattr(actobj, var_key): return

    value = getattr(actobj, var_key)
    if relative:
        prev_key = "_previous_"+var_key
        if not hasattr(actobj, prev_key):
            anti_recursive_set(actobj, prev_key, value)

    for obj in selected:
        try:
            if obj is not actobj and hasattr(obj, var_key):
                if type(value) is str or not hasattr(value, "__getitem__"):
                    if relative: apply_value = value - getattr(actobj, prev_key)
                    else: apply_value = value
                    anti_recursive_set(obj, var_key, apply_value, relative)
                else:
                    for i in range(len(value)):
                        if relative: apply_value = value[i] - getattr(actobj, prev_key)[i]
                        else: apply_value = value[i]
                        anti_recursive_set(getattr(obj, var_key), i, apply_value, relative)
        except:
            traceback.print_exc()

    if relative:
        anti_recursive_set(actobj, prev_key, value)


def _share_var_update(context, var_key=None, relative=False):
    try:
        actobj = context.active_object
        selected = context.selected_objects
        share_var_with_objects(actobj=actobj, selected=selected, var_key=var_key, relative=relative)
    except:
        traceback.print_exc()
        return

def add_sharing_property(bpy_type, key, relative=False, prop_type=None, add_func=None, **prop_kwargs):
    def _on_update_share(self, context):
        nonlocal key, relative, add_func
        _share_var_update(context, key, relative=relative)
        selected = context.selected_objects
        if add_func is not None:
            for obj in selected:
                ctx = context.copy()
                ctx['active_object'] = obj
                ctx['copy'] = lambda x: ctx
                ctx = argparse.Namespace(**ctx)
                add_func(self, ctx)
    
    name = key.replace("_", " ").title()
    prop_kwargs['name'] = name
    prop = prop_type(
        update = _on_update_share,
        **prop_kwargs
    )
    setattr(bpy_type, key, prop)

def add_levelbuddy_sharing_props(_update_sector_solidify):
    add_sharing_property(
        bpy.types.Object, "texture_tillings", False,
        bpy.props.FloatVectorProperty, None,
        default=(1, 1, 1),
        min=0,
        step=10,
        precision=3,
    )
    add_sharing_property(
        bpy.types.Object, "ceiling_texture_offset", False,
        bpy.props.FloatVectorProperty, None,
        default=(0, 0),
        min=0,
        step=10,
        precision=3,
        size=2
    )
    add_sharing_property(
        bpy.types.Object, "wall_texture_offset", False,
        bpy.props.FloatVectorProperty, None,
        default=(0, 0),
        min=0,
        step=10,
        precision=3,
        size=2
    )

    add_sharing_property(
        bpy.types.Object, "floor_texture_offset", False,
        bpy.props.FloatVectorProperty, None,
        default=(0, 0),
        min=0,
        step=10,
        precision=3,
        size=2,
    )
    add_sharing_property(
        bpy.types.Object, "ceiling_height", False,
        bpy.props.FloatProperty, _update_sector_solidify,
        default=4,
        step=10,
        precision=3
    )
    add_sharing_property(
        bpy.types.Object, "floor_height", False,
        bpy.props.FloatProperty, _update_sector_solidify,
        default=0,
        step=10,
        precision=3
    )

    add_sharing_property(
        bpy.types.Object, "floor_texture", False,
        bpy.props.StringProperty, None,
    )
    add_sharing_property(
        bpy.types.Object, "wall_texture", False,
        bpy.props.StringProperty, None,
    )
    add_sharing_property(
        bpy.types.Object, "ceiling_texture", False,
        bpy.props.StringProperty, None,
    )

    add_sharing_property(
        bpy.types.Object, "brush_type", False,
        bpy.props.EnumProperty, None,
        items=[
            ("BRUSH", "Brush", "is a brush"),
            ("SECTOR", "Sector", "is a sector"),
            ("NONE", "None", "none"),
        ],
        description="the brush type",
        default='NONE'
    )
    add_sharing_property(
        bpy.types.Object, "csg_operation", False,
        bpy.props.EnumProperty, None,
        items=[
            ("ADD", "Add", "add/union geometry to output"),
            ("SUBTRACT", "Subtract", "subtract/remove geometry from output"),
        ],
        name="CSG Operation",
        description="the CSG operation",
        default='ADD'
    )

    add_sharing_property(
        bpy.types.Object, "csg_order", False,
        bpy.props.IntProperty, None,
        name="CSG Order",
        default=0,
        description='Controls the order of CSG operation of the object'
    )
    add_sharing_property(
        bpy.types.Object, "brush_auto_texture", False,
        bpy.props.BoolProperty, None,
        default=True,
        description='Auto Texture on or off'
    )
    add_sharing_property(
        bpy.types.Object, "flip_normals", False,
        bpy.props.BoolProperty, None,
        default=True,
        description='Flip output normals'
    )
