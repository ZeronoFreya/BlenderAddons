import bpy

def add(object,data_path,callback):
    subscribe_to = object.path_resolve(data_path, False)
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=object,
        args=(object,data_path,),
        notify=callback,
    )

def remove(object):
    bpy.msgbus.clear_by_owner(object)