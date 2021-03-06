import bpy
import gpu
import bgl
from math import pow as mPow, log as mLog
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import (region_2d_to_origin_3d, region_2d_to_vector_3d, location_3d_to_region_2d)

vertex_shader = '''
    uniform mat4  MVPMatrix;        // pixel matrix
    uniform vec3  center;           // center of circle
    uniform vec4  color;            // color of circle
    uniform vec3  plane_x;          // x direction in plane the circle lies in
    uniform vec3  plane_y;          // y direction in plane the circle lies in
    uniform float radius;           // radius of circle
    uniform float width;            // line width, perpendicular to line (in plane)
    #define PI    3.14159265359
    #define TAU   6.28318530718
    /////////////////////////////////////////////////////////////////////////
    in vec2 pos;                    // x: [0,1], ratio of circumference.  y: [0,1], inner/outer radius (width)
    void main() {
        float ang = TAU * pos.x;
        float r = radius + pos.y * width;
        vec3 p = center + r * (plane_x * cos(ang) + plane_y * sin(ang));
        gl_Position = MVPMatrix * vec4(p, 1.0);
    }
    /////////////////////////////////////////////////////////////////////////
'''

fragment_shader = '''
    uniform mat4  MVPMatrix;        // pixel matrix
    uniform vec3  center;           // center of circle
    uniform vec4  color;            // color of circle
    uniform vec3  plane_x;          // x direction in plane the circle lies in
    uniform vec3  plane_y;          // y direction in plane the circle lies in
    uniform float radius;           // radius of circle
    uniform float width;            // line width, perpendicular to line (in plane)
    #define PI    3.14159265359
    #define TAU   6.28318530718

    /////////////////////
    /////////////////////////////////////////////////////////////////////////
    out vec4 outColor;
    void main() {
        outColor = color;
        outColor = blender_srgb_to_framebuffer_space(outColor);
    }
'''

shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
cnt = 100
pts = [
    p for i0 in range(cnt)
    for p in [
        ((i0+0)/cnt,0), ((i0+1)/cnt,0), ((i0+1)/cnt,1),
        ((i0+0)/cnt,0), ((i0+1)/cnt,1), ((i0+0)/cnt,1),
    ]
]
batch = batch_for_shader(
    shader, 'TRIS',
    {"pos": pts},
)

float_inf = float('inf')


class BrushFalloff:
    
    def __init__(self):
        self.point = None
        self._handler = None
        self.scale = 1.0
        self.mouse = None
    
    def init(self, context):
        self.rgn = context.region
        self.r3d = context.space_data.region_3d
        self.matrix = context.region_data.perspective_matrix
        self.prefs = context.preferences.addons["shortcut_collection"].preferences        

    def update_center(self, p=None, n=None):
        self.point = p
        if n: self.normal = n
    
    def set_radius(self, radius):
        if isinstance(radius, int):
            self.prefs.topo_tweak_radius = radius

    def update_radius(self, mouse=None):
        if not mouse: return
        self.set_radius(int((mouse - self.mouse).length))
    
    def set_falloff(self, falloff):
        if isinstance(falloff, float):
            self.prefs.topo_tweak_falloff = falloff
    
    def update_falloff(self, mouse=None):
        if not mouse: return
        radius = self.prefs.topo_tweak_radius
        self.set_falloff(min(radius, (mouse - self.mouse).length ) / radius)
    
    def update_start(self, mouse):
        self.mouse = mouse

    def update_end(self):
        self.mouse = None

    def draw3D_circle(self, center, radius, color, width, x, y):
        bgl.glEnable(bgl.GL_BLEND)
        shader.uniform_float("center", center)
        shader.uniform_float("radius", radius)
        shader.uniform_float("color", color)
        shader.uniform_float("width",  width)
        shader.uniform_float('plane_x', x)
        shader.uniform_float('plane_y', y)
        shader.uniform_float('MVPMatrix', self.matrix)
        batch.draw(shader)

        # bgl.glDisable(bgl.GL_DEPTH_TEST)
        bgl.glDisable(bgl.GL_BLEND)
        gpu.shader.unbind()
    
    def point2D_to_Point(self, xy, depth):
        if depth is None: return None
        o = region_2d_to_origin_3d(self.rgn, self.r3d, xy)
        d = region_2d_to_vector_3d(self.rgn, self.r3d, xy)
        if o is None or d is None: return None

        return o + max(0.0, min(float_inf, depth)) * d
    
    def get_scale(self):
        xy = location_3d_to_region_2d(self.rgn, self.r3d, self.point)
        if xy is None: return None
        xyz = region_2d_to_origin_3d(self.rgn, self.r3d, xy)
        depth = (self.point - xyz).length
        if not depth: return None

        p3d0 = self.point2D_to_Point(Vector((0,0)), depth)
        p3d1 = self.point2D_to_Point(Vector((1,0)), depth)
        self.scale = (p3d0 - p3d1).length 
        return self.scale

    def draw_brush(self):
        if(not self.point): return
        scale = self.get_scale()
        if not scale: return
        
        shader.bind()
        
        x = Vector((-self.normal.x + 3.14, self.normal.y + 42, self.normal.z - 1.61))
        y = -x.cross(self.normal)
        x = y.cross(self.normal)
        x.normalize()
        y.normalize()

        r = self.prefs.topo_tweak_radius
        cc = (*self.prefs.topo_tweak_fill_color[:3], self.prefs.topo_tweak_fill_color[3] * self.prefs.topo_tweak_strength * 0.60 + 0.10)

        ff = mLog(0.5) / mLog(max(0.01, min(0.99, self.prefs.topo_tweak_falloff )))
        ff = mPow(0.5, 1.0 / ff)
        fs = (1-ff) * r * scale

        bgl.glDepthRange(0.0, 0.99996)
        # ????????????
        self.draw3D_circle(self.point, r*scale - fs, cc, fs, x, y)
        bgl.glDepthRange(0.0, 0.99995)
        # ?????????
        self.draw3D_circle(self.point, r*scale, self.prefs.topo_tweak_outer_color, 2*scale, x, y)
        # ?????????
        self.draw3D_circle(self.point, r*scale*ff, self.prefs.topo_tweak_inner_color, 2*scale, x, y)
        bgl.glDepthRange(0.0, 1.0)

    def show(self):
        self._handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_brush, (), 'WINDOW', 'POST_VIEW')
    
    def close(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handler, 'WINDOW')
