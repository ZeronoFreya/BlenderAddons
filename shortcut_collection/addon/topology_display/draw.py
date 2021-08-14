
from .. import utils
from .tweak.brushfalloff import BrushFalloff

def panelDraw(context, object, layout):
    if(object.mode == "EDIT"):
        layout.label(text="拓扑视图优化:")

        row = layout.row(align=True)
        icon = 'KEYTYPE_EXTREME_VEC'
        text = "禁用"
        topo = utils.prop.get_object_prop("shortcut_collection_topology")
        if(topo and topo["status"]):
            icon = 'KEYTYPE_JITTER_VEC'
            text = "启用"
        # row.label(text='', icon=icon)
        row.operator("shortcut_collection.topology_display", text=text, icon=icon)
        # 状态
        row = layout.row(align=True)
        overlay = utils.addon.get_space_data(context).overlay
        row.operator("shortcut_collection.topology_display_occlude_wire", text="隐藏线框", icon="CHECKBOX_HLT" if overlay.show_occlude_wire else "CHECKBOX_DEHLT")
        row.operator("shortcut_collection.topology_display_in_front", text="在前面", icon="CHECKBOX_HLT" if object.show_in_front else "CHECKBOX_DEHLT") 
        row.operator("shortcut_collection.topology_display_wireframe_opacity", text="线框透明", icon="CHECKBOX_HLT" if overlay.wireframe_opacity < 1 else "CHECKBOX_DEHLT") 

        row = layout.row()
        row.operator("shortcut_collection.topology_display_tweak", text="tweak")



