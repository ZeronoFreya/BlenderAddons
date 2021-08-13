import bpy
from .. import icons

from ..modules import modules

class MainPanel(bpy.types.Panel):
    bl_idname = 'SHORTCUT_COLLECTION_PT_MainPanel'
    bl_label = 'Shortcut_Collection'
    bl_category = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'

    def draw(self, context: bpy.types.Context):
        act = context.active_object
        layout = self.layout

        for module in modules:
            if hasattr(module, 'panelDraw'):
                module.panelDraw(context, act, layout)

def popover(self, context: bpy.types.Context):
    layout = self.layout
    panel = MainPanel.bl_idname
    icon = icons.id('shortcut_collection')
    layout.popover(panel, text='', icon_value=icon)
