import bpy, os

# Python doesn't reload package sub-modules at the same time as __init__.py!
import importlib, sys
for filename in [ f for f in os.listdir(os.path.dirname(os.path.realpath(__file__))) if f.endswith(".py") ]:
	if filename == os.path.basename(__file__): continue
	module = sys.modules.get("{}.{}".format(__name__,filename[:-3]))
	if module: importlib.reload(module)

# clear out any scene update funcs hanging around, e.g. after a script reload
for collection in [bpy.app.handlers.depsgraph_update_post, bpy.app.handlers.load_post]:
	for func in collection:
		if func.__module__.startswith(__name__):
			collection.remove(func)

from . import LevelBuddy

bl_info = {
    "name": "Level Buddy",
    "author": "Matt Lucas, HickVieira (Blender 3.0 version)",
    "version": (1, 5),
    "blender": (3, 0, 0),
    "location": "View3D > Tools > Level Buddy",
    "description": "A set of workflow tools based on concepts from Doom and Unreal level mapping.",
    "warning": "WIP",
    "wiki_url": "https://github.com/hickVieira/LevelBuddyBlender3",
    "category": "Object"
}

classes = [
    LevelBuddy.LevelBuddyPanel,
    LevelBuddy.LevelBuddyBuildMap,
    LevelBuddy.LevelBuddyNewGeometry,
    LevelBuddy.LevelBuddyRipGeometry,
    LevelBuddy.LevelBuddyOpenMaterial,
    LevelBuddy.LevelBuddyShareMatWithSelected
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()