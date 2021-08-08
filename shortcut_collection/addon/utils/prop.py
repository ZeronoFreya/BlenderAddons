import bpy
# from rna_prop_ui import rna_idprop_ui_prop_get
from ast import literal_eval
# from re import match
from idprop.types import (IDPropertyArray, IDPropertyGroup)

defParameters = {
    "description":"",
    "default": 1.0,
    "min":0.0,
    "max":1.0,
    "soft_min":0.0,
    "soft_max":1.0,
    "use_soft_limits":False,
    "is_overridable_library":False
}

def __add_prop(propData, key:str, val, info):
    rna_ui = propData.get('_RNA_UI')
    if rna_ui is None:
        rna_ui = propData['_RNA_UI'] = {}
    if(key not in propData):
        propData[key] = val
        rna_ui[key] = defParameters.update(info)
    # print(type(scene[key]),"^^^^^^^^")
    return propData[key]



def __get_prop(propData, key:str, default):
    rna_ui = propData.get('_RNA_UI')
    if rna_ui is None:
        rna_ui = propData['_RNA_UI'] = {}
        return None
    key = key.split(".")
    if(key[0] not in propData):
        return None
    val = propData[key[0]]
    del(key[0])
    if(isinstance(val, str)):
        try:
            eVal = literal_eval(val)
            for k in key:
                if(isinstance(eVal, IDPropertyArray)):
                    k = int(key[0])
                    return eVal[k]
                elif(isinstance(eVal, IDPropertyGroup)):
                    if( k in eVal ):
                        eVal = eVal[k]
                    else:
                        return default
                else:
                    return default
            return eVal
        except (SyntaxError, ValueError):
            return default
    elif(isinstance(val, IDPropertyArray)):
        try:
            k = int(key[0])
            return val[k]
        except ValueError:
            return default
    elif(isinstance(val, IDPropertyGroup)):
        try:
            eVal = val
            for k in key:
                if(isinstance(eVal, IDPropertyArray)):
                    k = int(key[0])
                    return eVal[k]
                elif(isinstance(eVal, IDPropertyGroup)):
                    if( k in eVal ):
                        eVal = eVal[k]
                    else:
                        return default
                else:
                    return default
            return eVal
        except ValueError:
            return default
    else:
        if(len(key)>0):
            return default
        return val


def __set_prop(propData, key:str, val):
    key = key.split(".")
    if(key[0] not in propData):
        return False, "找不到 " + key[0]
    if(isinstance(propData[key[0]], str)):
        propData[key[0]] = get_scene_prop(key[0])
    data = propData[key[0]]
    del(key[0])
    lastK = key[0]
    i = 1
    l = len(key)
    for k in key:
        if(i == 1):
            lastK = k
            i += 1
            continue
        # # print(lastK, data, i, "<<<<<<<<<<<<<<<<")
        if(k == "push"):
            if(isinstance(data[lastK], IDPropertyArray)):
                k = len(data[lastK])
            elif(isinstance(data[lastK], IDPropertyGroup)):
                k = "!" + str(len(data[lastK]))
            else:
                break
        try:
            num = int(k)
            if(l == i):
                if(lastK not in data):
                    data[lastK] = [0 for _ in range(abs(num))] if num < 0 else [0 for _ in range(num+1)]
                elif(isinstance(data[lastK], IDPropertyArray)):
                    s = len(data[lastK]) - abs(num) if num < 0 else len(data[lastK]) - num - 1
                    if(s < 0):
                        newList = data[lastK].to_list()
                        newList.extend([0 for _ in range(abs(s))])
                        data[lastK] = newList
            elif(lastK not in data):
                data[lastK] = {}
            
            data = data[lastK] 
            lastK = num if isinstance(data, IDPropertyArray) else k
            # print(lastK, data, type(data), "$$$$$$$$$$$$$$$$$")
        except (SyntaxError, ValueError):
            # print(lastK, data, type(data), "!!!!!!!!!!!!!!")
            if(lastK not in data):
                data[lastK] = {}
            data = data[lastK] 
            lastK = k[1:] if k.startswith("!") else k
            # print(lastK, data, type(data), "??????????????")
        i += 1
    # print(lastK, type(lastK), data, type(data), "###############################")
    # if(lastK == "push"):
    #     if(isinstance(data, IDPropertyArray)):
    #         newList = data.to_list()
    #         newList.append(val)
    #         data[lastK] = newList
    #     else:
    #         return False
    data[lastK] = val
    return data[lastK]


def add_scene_prop(key:str, val:any=1.0, info: dict={}):
    return __add_prop(bpy.context.scene, key, val, info)

def add_object_prop(key:str, val:any=1.0, info: dict={}):
    return __add_prop(bpy.context.object, key, val, info)

def get_scene_prop(key:str, default=None):    
    return __get_prop(bpy.context.scene, key, default)

def get_object_prop(key:str, default=None):    
    return __get_prop(bpy.context.object, key, default)
    
def set_scene_prop(key:str, val:any=1.0):
    return __set_prop(bpy.context.scene, key, val)

def set_object_prop(key:str, val:any=1.0):
    return __set_prop(bpy.context.object, key, val)
    
    

    

