import bpy
import bmesh
from bpy_extras import object_utils
from . import utils

# from numpy import ( ones, zeros, dot, linalg, mat, mean )
import numpy as np

def get_vertex_on_plane_fitting(selectVector):
    """获取位于拟合平面上的正三角形顶点坐标"""
    size = len(selectVector)
    a = np.ones((size, 3))
    for i in range(0, size):
        verts = selectVector[i]
        a[i, 0] = verts[0]
        a[i, 1] = verts[1]
    b = np.zeros((size, 1))
    for i in range(0, size):
        b[i, 0] = selectVector[i][2]
    A_T = a.T
    A1 = np.dot(A_T, a)
    A2 = np.linalg.inv(A1)
    A3 = np.dot(A2, A_T)
    X = np.dot(A3, b)
    # print('平面拟合结果为：z = %.3f * x + %.3f * y + %.3f'%(X[0,0],X[1,0],X[2,0]))

    matrix = np.mat(selectVector)
    co = np.mean(matrix, 0)

    c = (co[0,0], co[0,1], X[0,0] * co[0,0] + X[1,0] * co[0,1] + X[2,0])
    

    n = np.array([X[0,0], X[1,0], -1])    

    a = np.cross(n, np.array([1,0,0]))
    b = np.cross(n, a)
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)

    r = 1

    angle = np.array([0, 240, 120]) * np.pi/180
    x = c[0] + r * a[0] * np.cos(angle) + r * b[0] * np.sin(angle)
    y = c[1] + r * a[1] * np.cos(angle) + r * b[1] * np.sin(angle)
    z = c[2] + r * a[2] * np.cos(angle) + r * b[2] * np.sin(angle)

    return [(x[i], y[i], z[i]) for i in range(0, np.size(angle))]

def mesh_from_verts(verts_loc):
    mesh = bpy.data.meshes.new("Plane")
    bm = bmesh.new()
    for v_co in verts_loc:
        bm.verts.new(v_co)
    bm.verts.ensure_lookup_table()
    # for f_idx in faces:
    #     bm.faces.new([bm.verts[i] for i in f_idx])
    bm.faces.new([bm.verts[i] for i in range(len(bm.verts))])
    bm.faces.ensure_lookup_table()
    bm.faces[0].select = True
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh

class ViewAxis(bpy.types.Operator, object_utils.AddObjectHelper):
    """对齐视图到选择顶点"""
    bl_idname = "shortcut_collection.view_axis"
    bl_label = "ViewAxis"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        if(context.area.type == "VIEW_3D"):
            obj = context.active_object
            selectBMVert = [i for i in bmesh.from_edit_mesh(obj.data).verts if i.select]
            if(len(selectBMVert) < 3):
                self.report({'WARNING'}, "至少选择三个顶点！")
                return {'FINISHED'}
            # store = bpy.data.window_managers["WinMan"].ShortcutCollectionStore
            # objName = obj.data.name
            verts_loc = get_vertex_on_plane_fitting([(obj.matrix_world @ BMVert.co).to_tuple() for BMVert in selectBMVert]) 
            # history = utils.getStore(store.Object_List, objName + ".shortcut_collection_align.history")
            # if(not history):
            #     history = utils.setStore(store.Object_List, objName + ".shortcut_collection_align.history", [])
            # history.append(verts_loc)

            if(not utils.prop.get_object_prop("shortcut_collection_align.history")):
                utils.prop.add_object_prop("shortcut_collection_align", {})
                utils.prop.set_object_prop("shortcut_collection_align.history", {})
            utils.prop.set_object_prop("shortcut_collection_align.history.push", verts_loc)
            
            object_utils.object_data_add(context, mesh_from_verts(verts_loc), operator=self)

            bpy.ops.view3d.view_axis(type="TOP", align_active=True)

            bpy.ops.mesh.delete(type='VERT')


        return {'FINISHED'}

class LastViewAxis(bpy.types.Operator, object_utils.AddObjectHelper):
    """上次对齐的视图"""
    bl_idname = "shortcut_collection.last_view_axis"
    bl_label = "LastViewAxis"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        if(context.area.type == "VIEW_3D"):
            # store = bpy.data.window_managers["WinMan"].ShortcutCollectionStore
            # objName = context.active_object.data.name
            # history = utils.getStore(store.Object_List, objName + ".shortcut_collection_align.history")
            # verts_loc = history[-1]
            history = utils.prop.get_object_prop("shortcut_collection_align.history")
            verts_loc = history[str(len(history) - 1)]
            object_utils.object_data_add(context, mesh_from_verts(verts_loc), operator=self)
            bpy.ops.view3d.view_axis(type="TOP", align_active=True)
            bpy.ops.mesh.delete(type='VERT')
        return {'FINISHED'}

class HistoryViewAxis(bpy.types.Operator, object_utils.AddObjectHelper):
    """对齐的历史记录"""
    bl_idname = "shortcut_collection.history_view_axis"
    bl_label = "HistoryViewAxis"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        return {'FINISHED'}

def panelDraw(context, object, layout):
    if(object.mode == "EDIT"):
        layout.label(text="对齐:")
        # history = utils.getStore(Object_List, objName + ".shortcut_collection_align.history")
        history = utils.prop.get_object_prop("shortcut_collection_align.history")
        if(history and len(history)>0):
            split = layout.split(factor=0.6)
            col = split.column()
            col.operator("shortcut_collection.view_axis", text='对齐视图到选择顶点')
            col.scale_y = 2.0
            col = split.column(align=True)
            col.scale_y = 1.0
            col.operator("shortcut_collection.last_view_axis", text='上次对齐')
            col.operator("shortcut_collection.history_view_axis", text='历史记录')
        else:
            row = layout.row()
            row.operator("shortcut_collection.view_axis", text='对齐视图到选择顶点')
            
def register():
    bpy.utils.register_class(ViewAxis)
    bpy.utils.register_class(LastViewAxis)
    bpy.utils.register_class(HistoryViewAxis)
        

def unregister():
    bpy.utils.unregister_class(ViewAxis)
    bpy.utils.unregister_class(LastViewAxis)
    bpy.utils.unregister_class(HistoryViewAxis)