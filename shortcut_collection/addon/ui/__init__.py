import bpy
from . import panel

classes = (
    panel.MainPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_editor_menus.append(panel.popover)


def unregister():
    bpy.types.VIEW3D_MT_editor_menus.remove(panel.popover)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
