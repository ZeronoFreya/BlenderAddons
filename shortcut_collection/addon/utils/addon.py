import bpy


def get_space_data(context) -> bpy.types.Space:
    space_data = context.space_data
    if space_data is None or space_data.type != 'VIEW_3D':
        for window in context.window_manager.windows:   
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    space_data = area.spaces.active
                    break
    return space_data

def get_visible_objs(context):
    space = context.space_data
    if not space: return []
    local_view = space.local_view
    objs = context.visible_objects
    if local_view:
        depsgraph = context.evaluated_depsgraph_get()
        return [obj for obj in objs if (obj.type == "MESH" and obj.evaluated_get(depsgraph).local_view_get(space))]
    else:
        return [obj for obj in objs if obj.type == "MESH"]

