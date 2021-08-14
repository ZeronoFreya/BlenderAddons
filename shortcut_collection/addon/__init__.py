import bpy
from . import icons
from . import ui
from . import utils
from . import preferences

from .modules import modules


baseModules = (
    icons,
    ui,
    utils,
    preferences,
)



# class ShortcutCollectionStore(bpy.types.PropertyGroup):
#     Object_List = {}
#     Theme_Opt = {}

def register():
    # bpy.utils.register_class(ShortcutCollectionStore)
    # bpy.types.WindowManager.ShortcutCollectionStore = bpy.props.PointerProperty(type=ShortcutCollectionStore)
    for module in baseModules:
        module.register()
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()
    for module in reversed(baseModules):
        module.unregister()
    # del bpy.types.WindowManager.ShortcutCollectionStore
    # bpy.utils.unregister_class(ShortcutCollectionStore)
