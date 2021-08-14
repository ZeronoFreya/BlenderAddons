import bpy
import bmesh

from math import pow as mPow
# from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.view3d_utils import (region_2d_to_origin_3d, region_2d_to_vector_3d, location_3d_to_region_2d)

from ...utils.addon import get_visible_objs

def getBVHTree(objs, depsgraph, applyModifiers=True, world_space=True):
    if len(objs) == 0: return None
    bm = bmesh.new()
    if applyModifiers:
        if world_space:
            i = 0
            for obj in objs:
                obj_eval = obj.evaluated_get(depsgraph)
                bm.from_mesh(obj_eval.to_mesh())
                bmesh.ops.transform(
                    bm,
                    verts=bm.verts[i:],
                    matrix=obj.matrix_world,
                )
                i = len(bm.verts)
                obj_eval.to_mesh_clear()
        else:
            for obj in objs:
                bm.from_mesh(obj.data)
        bm.normal_update()
        bvh = BVHTree.FromBMesh(bm)
        bm.free()
        return bvh
    else:
        vertices = []
        polygons = []
        if world_space:
            for obj in objs:
                obj.data.transform(obj.matrix_world)
                vertices.extend([v.co for v in obj.data.vertices])
                polygons.extend([p.vertices for p in obj.data.polygons])
                obj.data.transform(obj.matrix_world.inverted())
        else:
            for obj in objs:
                vertices.extend([v.co for v in obj.data.vertices])
                polygons.extend([p.vertices for p in obj.data.polygons])
        return BVHTree.FromPolygons(vertices, polygons)
                

def sourcesBVHTree(context, act, depsgraph, sourcesObjs=None):
    """获取目标物体的BVHTree"""
    if not act: return None
    if not sourcesObjs:
        # sourcesObjs =  [obj for obj in bpy.data.objects if (obj.type == "MESH" and obj != act)]
        sourcesObjs =  [obj for obj in get_visible_objs(context) if obj != act]
    if not isinstance(sourcesObjs, list):
        sourcesObjs = [sourcesObjs]
    if(len(sourcesObjs) == 0): return None
    return getBVHTree(sourcesObjs, depsgraph)

def activeBVHTree(act, depsgraph):
    """获取活动物体的BVHTree"""
    if not act: return None
    return getBVHTree([act], depsgraph)

def vertsInRadius(act, point, radius, onlySelect=False):
    """以某点为球心，获取半径内的所有顶点"""
    nearest = []
    if onlySelect:
        selectBMVert = [i for i in bmesh.from_edit_mesh(act.data).verts if i.select]
    else:
        selectBMVert = [i for i in bmesh.from_edit_mesh(act.data).verts]
    matrix_world = act.matrix_world
    for bmv in selectBMVert:
        if not bmv.is_valid: continue
        bmv_world = matrix_world @ bmv.co
        d3d = (bmv_world - point).length
        if d3d > radius: continue
        nearest.append((bmv, d3d))
    return nearest



class TweakCore:
    act = None
    rgn = None
    r3d = None
    sourcesBvh = None
    matrix_i = None

    def init(self, context):
        self.act = context.active_object
        self.rgn = context.region
        self.r3d = context.space_data.region_3d
        self.depsgraph = context.evaluated_depsgraph_get()
        self.sourcesBvh = sourcesBVHTree(context, self.act, self.depsgraph)
        self.matrix_i = self.act.matrix_world.inverted()
        self.prefs = context.preferences.addons["shortcut_collection"].preferences
    
    def get_ray(self, region_2d):
        origin = region_2d_to_origin_3d(self.rgn, self.r3d, region_2d)
        direction = region_2d_to_vector_3d(self.rgn, self.r3d, region_2d)
        return origin, direction 
    
    def ray_cast_sources(self, mouse):
        origin, direction = self.get_ray( mouse )
        return self.sourcesBvh.ray_cast(origin, direction) 
    
    def setVert(self, vert, offset):
        if not vert: return
        co = location_3d_to_region_2d(self.rgn, self.r3d, self.act.matrix_world @ vert.co) + offset
        
        origin, direction = self.get_ray(co)
        p,n,i,d = self.sourcesBvh.ray_cast(origin, direction) 
        if p is None: return
        vert.co = self.matrix_i @ p
        vert.normal = n
        return p


    def pendingVerts(self, mouse, radius):
        """暂存待处理顶点"""
        origin, direction = self.get_ray( mouse )
        bvh = activeBVHTree(self.act, self.depsgraph)
        p, _, _, _ = bvh.ray_cast(origin, direction)
        self.verts = vertsInRadius(self.act, p, radius) if p else None
        return self.verts
    
    def click(self, mouse, scale):
        self.mouse = mouse
        verts = self.pendingVerts(mouse, self.prefs.topo_tweak_radius * scale)
        if not verts: return
        bpy.ops.mesh.select_all(action='DESELECT')
        for v,_ in verts:
            v.select = True
    
    def drag(self, mouse, scale):
        delta = mouse - self.mouse
        self.mouse = mouse
        if not self.verts: return None
        for v, d in self.verts:
            offset = max(0.0, min(1.0, (1.0 - mPow(d / (self.prefs.topo_tweak_radius * scale), self.prefs.topo_tweak_falloff)))) * self.prefs.topo_tweak_strength * delta
            self.setVert(v, offset)
        bmesh.update_edit_mesh(self.act.data, loop_triangles=False, destructive=False)
        self.act.data.update()

        