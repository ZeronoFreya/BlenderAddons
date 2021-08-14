import bpy
from bpy.props import (
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    BoolProperty,
    EnumProperty,
    StringProperty,
)
from bpy.types import AddonPreferences



# def draw_tool_keymap( layout ,keyconfing,keymapname ) :
#     keymap = keyconfing.keymaps[keymapname]            
#     layout.context_pointer_set('keymap', keymap)
#     cnt = 0

#     for item in reversed(keymap.keymap_items) :
#         cnt = max( cnt , (item.oskey,item.shift,item.ctrl,item.alt).count(True) )
    
#     for item in reversed(keymap.keymap_items) :
#         if True in (item.oskey,item.shift,item.ctrl,item.alt) :
#             it = layout.row( )
#             if item.idname == 'mesh.poly_quilt' :
#                 ic = it.row(align = True)
#                 ic.ui_units_x = cnt + 2
#                 ic.prop(item , "active" , text = "" , emboss = True )
#                 ic.template_event_from_keymap_item(item)

#                 ic = it.row(align = True)
#                 ic.prop(item.properties , "tool_mode" , text = "" , emboss = True )

#                 if( item.properties.tool_mode == 'LOWPOLY' ) :
#                     im = ic.row()
#                     im.active = item.properties.is_property_set("geometry_type")
#                     im.prop(item.properties, "geometry_type" , text = "" , emboss = True , expand = False , icon_only = False )

#     layout.operator(SC_OT_DirtyKeymap.bl_idname)


# class SC_OT_DirtyKeymap(bpy.types.Operator) :
#     bl_idname = "addon.shortcut_collection_dirty_keymap"
#     bl_label = "Save Keymap"

#     def execute(self, context):
#         for keymap in [ k for k in context.window_manager.keyconfigs.user.keymaps if "ShortcutCollection" in k.name ] :
#             keymap.show_expanded_items = keymap.show_expanded_items
#             # for item in reversed(keymap.keymap_items) :
#             #     if True in (item.oskey,item.shift,item.ctrl,item.alt) :
#             #         if item.idname == 'mesh.poly_quilt' :
#             #             item.active = item.active

#         context.preferences.is_dirty = True
# #       bpy.ops.wm.save_userpref()
#         return {'FINISHED'}

class ShortcutCollectionPreferences(AddonPreferences):
    bl_idname = "shortcut_collection"

    # 拓扑设置
    topo_setting_expanded : BoolProperty(
        name="TopoSettingExpanded",
        description="TopoSettingExpanded",
        default=False
    )
    topo_vertex_size: IntProperty(
        name="Vertex Size",
        description="顶点尺寸",
        min = 1,
        max = 10,
        default=4,
    )
    topo_vertex_color : FloatVectorProperty(
        name="Vertex Color",
        description="顶点颜色",
        default=(1.0, 0.0, 0.98),
        min=0.0,
        max=1.0,
        size=3,
        subtype='COLOR'
    )
    topo_vertex_select_color : FloatVectorProperty(
        name="Vertex Color",
        description="选择顶点颜色",
        default=(1.0, 0.918, 0.0),
        min=0.0,
        max=1.0,
        size=3,
        subtype='COLOR'
    )
    topo_wire_color : FloatVectorProperty(
        name="Vertex Color",
        description="边颜色",
        default=(0.475, 0.992, 1.0),
        min=0.0,
        max=1.0,
        size=3,
        subtype='COLOR'
    )
    topo_active_color : FloatVectorProperty(
        name="Vertex Color",
        description="当前选择颜色",
        default=(1.0, 0.0, 0.0, 0.502),
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR'
    )
    topo_tweak_radius: IntProperty(
        name="Tweak Radius",
        description="笔刷半径",
        min = 10,
        max = 1000,
        default=50,
    )
    topo_tweak_falloff: FloatProperty(
        name="Tweak Falloff",
        description="笔刷衰减",
        default=0.5,
        min=0.01,
        max=1.0
    )
    topo_tweak_strength: FloatProperty(
        name="Tweak Strength",
        description="笔刷强度",
        default=1.0,
        min=0.01,
        max=1.0
    )
    topo_tweak_fill_color: FloatVectorProperty(
        name="Tweak Fill Color",
        description="笔刷颜色",
        default=(1, 0.565, 0.31, 0.239),
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR'
    )
    topo_tweak_outer_color: FloatVectorProperty(
        name="Tweak Outer Color",
        description="笔刷外边框颜色",
        default=(1, 0.522, 0, 1),
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR'
    )
    topo_tweak_inner_color: FloatVectorProperty(
        name="Tweak Inner Color",
        description="笔刷内边框颜色",
        default=(1, 0.522, 0, 0.5),
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR'
    )

    longpress_time : FloatProperty(
        name="LongPressTime",
        description="Long press Time",
        default=0.4,
        min=0.2,
        max=1.0
    )

    


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Tool settings:", icon = 'TOOL_SETTINGS')
        box = row.box().column()
        row = box.row()
        row.label(text="Long Press Time")
        row.prop(self, "longpress_time" , text = "Time" )
        row = box.row()
        row.label(text="Distance to Highlight")
        row.prop(self, "longpress_time" , text = "Time" )

        # row = layout.row()
        # row.column().label(text="Color settings:" , icon = 'COLOR')
        # box = row.box().column()
        # box.row().prop(self, "highlight_color" , text = "HighlightColor")

        # layout.prop( self, "keymap_setting_expanded", text="Keymap setting",
        #     icon='TRIA_DOWN' if self.keymap_setting_expanded else 'TRIA_RIGHT')
        
        # if self.keymap_setting_expanded :
        #     col = layout.column()
        #     col.row().prop(self, "keymap_category", expand=True)

        #     keyconfing = context.window_manager.keyconfigs.user            
        #     draw_tool_keymap( col.box() ,keyconfing , "3D View Tool: Edit Mesh, " + self.keymap_category )
        
        layout.prop( self, "topo_setting_expanded", text="拓扑工具", icon='TRIA_DOWN' if self.topo_setting_expanded else 'TRIA_RIGHT')
        if self.topo_setting_expanded:
            # col = layout.column()
            # col.row().prop(preferences, "keymap_category", expand=True)

            # keyconfing = context.window_manager.keyconfigs.user            
            # draw_tool_keymap( col.box() ,keyconfing , "3D View Tool: Edit Mesh, " + self.keymap_category )
            row = layout.row()
            row.column().label(text="视图显示:" , icon = 'COLOR')
            box = row.box().column()
            row = box.row()
            row.label(text="顶点尺寸")
            row.prop(self, "topo_vertex_size" , text = "")
            row = box.row()
            row.label(text="顶点颜色")
            row.prop(self, "topo_vertex_color" , text = "")
            row = box.row()
            row.label(text="选择顶点颜色")
            row.prop(self, "topo_vertex_select_color" , text = "")
            row = box.row()
            row.label(text="边颜色")
            row.prop(self, "topo_wire_color" , text = "")
            row = box.row()
            row.label(text="当前选择颜色")
            row.prop(self, "topo_active_color" , text = "")

            row = layout.row()
            row.column().label(text="吸附笔刷:" , icon = 'COLOR')
            box = row.box().column()
            row = box.row()
            row.label(text="笔刷半径")
            row.prop(self, "topo_tweak_radius" , text = "")
            row = box.row()
            row.label(text="笔刷衰减")
            row.prop(self, "topo_tweak_falloff" , text = "")
            row = box.row()
            row.label(text="笔刷强度")
            row.prop(self, "topo_tweak_strength" , text = "")
            row = box.row()
            row.label(text="笔刷颜色")
            row.prop(self, "topo_tweak_fill_color" , text = "")
            row = box.row()
            row.label(text="外边框颜色")
            row.prop(self, "topo_tweak_outer_color" , text = "")
            row = box.row()
            row.label(text="内边框颜色")
            row.prop(self, "topo_tweak_inner_color" , text = "")

def register():
    bpy.utils.register_class(ShortcutCollectionPreferences)

def unregister():
    bpy.utils.unregister_class(ShortcutCollectionPreferences)                