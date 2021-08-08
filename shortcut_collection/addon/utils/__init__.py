from . import msgbus
from . import addon
from . import prop

def getStore(item, key: str, default=None):
    key = key.split(".")
    for k in key:
        if( k in item ):
            item = item[k]
        else:
            return default

    return item

def setStore(item, key: str, val):
    key = key.split(".")
    i = 1
    l = len(key)
    for k in key:
        if( k not in item ):
            if(i < l):
                item[k] = {}
            else:
                item[k] = val
        item = item[k]
        i += 1
    return item

def register():
    pass

def unregister():
    pass
