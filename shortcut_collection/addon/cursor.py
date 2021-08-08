import bpy

class Cursor0(bpy.types.Operator):
    """游标归零"""
    bl_idname = "shortcut_collection.cursor_0"
    bl_label = "Cursor"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        if(context.area.type == "VIEW_3D"):
            context.scene.cursor.location = [0,0,0]
        return {'FINISHED'}

class CursorX0(bpy.types.Operator):
    """游标X轴归零"""
    bl_idname = "shortcut_collection.cursor_x_0"
    bl_label = "Cursor"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        if(context.area.type == "VIEW_3D"):
            context.scene.cursor.location[0] = 0
        return {'FINISHED'}

def panelDraw(context, object, layout):
    layout.label(text="游标设置:")
    row = layout.row()
    row.operator("shortcut_collection.cursor_0", text='原点')
    row.operator("shortcut_collection.cursor_x_0", text='X = 0')
    
def register():
    bpy.utils.register_class(Cursor0)
    bpy.utils.register_class(CursorX0)
        

def unregister():
    bpy.utils.unregister_class(Cursor0)
    bpy.utils.unregister_class(CursorX0)