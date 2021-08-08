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
