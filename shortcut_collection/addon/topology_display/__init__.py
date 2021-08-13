import bpy
from bpy.app.handlers import persistent
from .. import utils
from . import tweak

from .draw import panelDraw

def storeTheme(view_3d):
    theme = utils.prop.get_scene_prop("shortcut_collection_theme")
    if(not theme):
        theme = utils.prop.add_scene_prop("shortcut_collection_theme", {}, {
            "description":"保存用到的主题"
        })
    theme["Wire_Edit"] = view_3d.wire_edit
    theme["Vertex"] = view_3d.vertex
    theme["Vertex_Select"] = view_3d.vertex_select
    theme["Editmesh_Active"] = view_3d.editmesh_active
    theme["Vertex_Size"] = view_3d.vertex_size
    return theme

def add(context):
    # item = utils.getStore(store.Object_List, objName + ".topo")
    objProp = utils.prop.get_object_prop("shortcut_collection_topology")
    overlay = utils.addon.get_space_data(context).overlay
    view_3d = context.preferences.themes[0].view_3d
    objProp["status"] = 1
    objProp["show_occlude_wire"] = overlay.show_occlude_wire
    objProp["wireframe_opacity"] = overlay.wireframe_opacity
    objProp["show_in_front"] = context.object.show_in_front

    storeTheme(view_3d)

    overlay.show_occlude_wire = True
    overlay.wireframe_opacity = 0.6
    context.object.show_in_front = True
    view_3d.wire_edit = (0.475, 0.992, 1.0)
    view_3d.vertex = (1.0, 0.0, 0.98)
    view_3d.vertex_select = (1.0, 0.918, 0.0)
    view_3d.editmesh_active = (1.0, 0.0, 0.0, 0.502)
    view_3d.vertex_size = 4

def remove(context):
    # item = utils.getStore(store.Object_List, objName + ".topo")
    objProp = utils.prop.get_object_prop("shortcut_collection_topology")
    theme = utils.prop.get_scene_prop("shortcut_collection_theme")
    overlay = utils.addon.get_space_data(context).overlay
    view_3d = context.preferences.themes[0].view_3d
    # item["status"] = False
    objProp["status"] = 0

    overlay.show_occlude_wire = objProp["show_occlude_wire"]
    overlay.wireframe_opacity = objProp["wireframe_opacity"]
    context.object.show_in_front = objProp["show_in_front"]
    view_3d.wire_edit = theme["Wire_Edit"]
    view_3d.vertex = theme["Vertex"]
    view_3d.vertex_select = theme["Vertex_Select"]
    view_3d.editmesh_active = theme["Editmesh_Active"]
    view_3d.vertex_size = theme["Vertex_Size"]

def mode_change(object, *args):
    """物体模式切换回调"""
    # store = bpy.data.window_managers["WinMan"].ShortcutCollectionStore
    # key = bpy.context.active_object.data.name
    if(object.mode == "OBJECT"):
        remove(bpy.context)
    elif(object.mode == "EDIT"):
        add(bpy.context)


class TopologyDisplay(bpy.types.Operator):
    """拓扑视图优化"""
    bl_idname = "shortcut_collection.topology_display"
    bl_label = "Topology Display"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        if(context.area.type == "VIEW_3D"):

            # store = bpy.data.window_managers["WinMan"].ShortcutCollectionStore
            # objName = context.active_object.data.name
            # topo = utils.getStore(store.Object_List, objName + ".topo")
            topo = utils.prop.get_object_prop("shortcut_collection_topology")
            if(not topo):
                # topo = utils.setStore(store.Object_List, objName + ".topo", {
                #     "status": False
                # })
                topo = utils.prop.add_object_prop("shortcut_collection_topology", {"status": 0})
            if(topo["status"]):
                remove(context)
                utils.msgbus.remove(context.object)
            else:
                add(context)
                utils.msgbus.add(context.object,"mode", mode_change)
        return {'FINISHED'}

class TopologyDisplayOccludeWire(bpy.types.Operator):
    """是否隐藏线框"""
    bl_idname = "shortcut_collection.topology_display_occlude_wire"
    bl_label = "TopologyDisplayOccludeWire"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        overlay = utils.addon.get_space_data(context).overlay
        overlay.show_occlude_wire = not overlay.show_occlude_wire
        return {'FINISHED'}
        
class TopologyDisplayInFront(bpy.types.Operator):
    """是否在前面"""
    bl_idname = "shortcut_collection.topology_display_in_front"
    bl_label = "TopologyDisplayInFront"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        act = context.active_object
        act.show_in_front = not act.show_in_front
        return {'FINISHED'}

class TopologyDisplayWireframeOpacity(bpy.types.Operator):
    """是否线框透明"""
    bl_idname = "shortcut_collection.topology_display_wireframe_opacity"
    bl_label = "TopologyDisplayWireframeOpacity"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        overlay = utils.addon.get_space_data(context).overlay
        overlay.wireframe_opacity = 1.0 if overlay.wireframe_opacity < 1 else 0.6
        return {'FINISHED'}

@persistent
def load_handler(*args):
    topo = utils.prop.get_object_prop("shortcut_collection_topology")
    if(topo and topo["status"]):
        utils.msgbus.add(bpy.context.object,"mode", mode_change)


def register():
    bpy.utils.register_class(TopologyDisplay)
    bpy.utils.register_class(TopologyDisplayOccludeWire)
    bpy.utils.register_class(TopologyDisplayInFront)
    bpy.utils.register_class(TopologyDisplayWireframeOpacity)
    # bpy.utils.register_class(Tweak)
    tweak.register()
    bpy.app.handlers.load_post.append(load_handler)
        
def unregister():
    bpy.utils.unregister_class(TopologyDisplay)
    bpy.utils.unregister_class(TopologyDisplayOccludeWire)
    bpy.utils.unregister_class(TopologyDisplayInFront)
    bpy.utils.unregister_class(TopologyDisplayWireframeOpacity)
    # bpy.utils.unregister_class(Tweak)
    tweak.unregister()
        