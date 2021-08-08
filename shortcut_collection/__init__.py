

bl_info = {
    'name': 'Shortcut collection',
    'author': 'zeronofreya',
    'description': '快捷操作集合',
    'blender': (2, 80, 0),
    'version': (0, 0, 1),
    'location': 'View3D',
    'category': '3D View'
}


from . import addon


def register():
    addon.register()

def unregister():
    addon.unregister()
