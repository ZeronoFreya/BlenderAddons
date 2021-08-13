import bpy
from mathutils import Vector
from .brushfalloff import BrushFalloff
from .core import TweakCore

brushFalloff = BrushFalloff(50, 1.5, 0.5, Vector((1,0.565,0.31,0.239)), Vector((1,0.522,0,1)), Vector((1,0.522,0,0.5)))

tweakCore = TweakCore()

class Tweak(bpy.types.Operator):
    """使用平滑笔刷调整顶点位置"""
    bl_idname = "shortcut_collection.topology_display_tweak"
    bl_label = "TopologyDisplayTweak"
    bl_options = {'REGISTER', "UNDO"}  

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
                    brushFalloff.radius, 
                    brushFalloff.falloff, 
                    brushFalloff.strength,
                    brushFalloff.scale
                )                
            context.area.tag_redraw()
            return {"RUNNING_MODAL"}
        elif event.type == 'LEFTMOUSE':
            self.lmb = event.value == 'PRESS'
            if event.value == 'PRESS':
                tweakCore.click(Vector((event.mouse_region_x, event.mouse_region_y)), brushFalloff.radius, brushFalloff.scale)
            if event.value == 'RELEASE':
                self.lmb = False
                context.area.tag_redraw()
            return {"RUNNING_MODAL"}
        # elif event.type == 'WHEELDOWNMOUSE' or event.type == 'WHEELUPMOUSE':
        #     brushFalloff.update_scale(p)
        elif event.type == "F":
            self.lmb = False
            self.f_press = True
            self.update = brushFalloff.update_radius
            brushFalloff.update_start(Vector((event.mouse_region_x, event.mouse_region_y)))
            return {"RUNNING_MODAL"}

        if event.type == "RIGHTMOUSE":
            context.space_data.show_gizmo_context  = self.gizmo
            brushFalloff.close()
            context.area.tag_redraw()
            return {"FINISHED"}

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