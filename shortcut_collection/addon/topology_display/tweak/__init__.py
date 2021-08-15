import bpy
from mathutils import Vector
from .brushfalloff import BrushFalloff
from .core import TweakCore
from ...utils.addon import get_visible_objs

brushFalloff = BrushFalloff()

tweakCore = TweakCore()

class Tweak(bpy.types.Operator):
    """使用平滑笔刷调整顶点位置"""
    bl_idname = "shortcut_collection.topology_display_tweak"
    bl_label = "TopologyDisplayTweak"
    bl_options = {'REGISTER', "UNDO"}  

    @classmethod
    def poll(cls, context):
        sourcesObjs =  [obj for obj in get_visible_objs(context) if obj != context.active_object]
        return len(sourcesObjs) > 0

    def invoke(self, context, event):
        self.lmb = False
        self.f_press = False
        self.act = context.active_object

        self.gizmo = context.space_data.show_gizmo_context
        if self.gizmo:
            context.space_data.show_gizmo_context = False
          
        tweakCore.init(context)

        brushFalloff.init(context)
        brushFalloff.show()

        self.update = brushFalloff.update_radius

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self.act.mode != "EDIT":
            brushFalloff.close()
            return {"FINISHED"}
        if self.f_press:
            if event.type == "F" and event.value == 'RELEASE':
                self.f_press = False
                brushFalloff.update_end()
            elif event.type == 'MOUSEMOVE':
                self.update(Vector((event.mouse_region_x, event.mouse_region_y)))
                context.area.tag_redraw()
            elif event.type == 'LEFTMOUSE':
                if not self.lmb:
                    self.lmb = True
                    self.update = brushFalloff.update_falloff
                elif event.value == 'RELEASE':
                    self.lmb = False
            
            return {"RUNNING_MODAL"}

        
        if event.type == 'MOUSEMOVE':
            p,n,i,d = tweakCore.ray_cast_sources(Vector((event.mouse_region_x, event.mouse_region_y)))
            brushFalloff.update_center( p, n)
            if self.lmb:
                tweakCore.drag(
                    Vector((event.mouse_region_x, event.mouse_region_y)), 
                    brushFalloff.scale
                )                
            context.area.tag_redraw()
            self.firstRun = True
            return {"RUNNING_MODAL"}
        elif event.type == 'LEFTMOUSE':
            self.lmb = event.value == 'PRESS'
            if event.value == 'PRESS':
                tweakCore.click(Vector((event.mouse_region_x, event.mouse_region_y)), brushFalloff.scale)
            if event.value == 'RELEASE':
                bpy.ops.ed.undo_push(message="创建历史记录")
                self.lmb = False
                context.area.tag_redraw()
            return {"RUNNING_MODAL"}
        elif event.type == 'WHEELDOWNMOUSE' or event.type == 'WHEELUPMOUSE':
            return {"PASS_THROUGH"}
        elif event.type == "F":
            self.lmb = False
            self.f_press = True
            self.update = brushFalloff.update_radius
            brushFalloff.update_start(Vector((event.mouse_region_x, event.mouse_region_y)))
            return {"RUNNING_MODAL"}

        # elif event.type == "RIGHTMOUSE":
        #     brushFalloff.update_center()
        #     context.area.tag_redraw()

        if event.type == "ESC":
            context.space_data.show_gizmo_context  = self.gizmo
            brushFalloff.close()
            context.area.tag_redraw()
            return {"FINISHED"}

        brushFalloff.update_center()
        context.area.tag_redraw()
        return {"PASS_THROUGH"}

addon_keymaps = []

def registerKeymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            Tweak.bl_idname, type='C', value='PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

def unregisterKeymaps():
    # for km, kmi in addon_keymaps:
    pass

def register():
    bpy.utils.register_class(Tweak)
    registerKeymaps()

def unregister():
    bpy.utils.unregister_class(Tweak)  
    unregisterKeymaps()  