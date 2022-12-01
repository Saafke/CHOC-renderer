"""This creates the NOCS Map for the .glb models.

run command: `blender --python compute_avg_scale_factor.py` (opens blender)
"""

import sys
#sys.path.append("/usr/local/lib/python3.6/dist-packages/")
sys.path.append("/home/weber/.local/lib/python3.7/site-packages")

import json

import bpy
import math
import os
import numpy as np
import pickle

def clear_scene():
    """
    Clears all stuff (including the cube) except objects in the scene.
    """
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        print(obj.name[:-3])
        if obj.type == 'CAMERA' or obj.type == 'LIGHT':
            obj.select_set(True)
            bpy.ops.object.delete()
        elif obj.type == 'MESH':
            print("mesh", obj.name)
            if obj.name == 'Cube':
                obj.select_set(True)
                bpy.ops.object.delete()
        elif obj.name[:-3] == "Camera." or obj.name[:-3] == "Light.": #removes extra light & camera objects that i added accidentily
            obj.select_set(True)
            bpy.ops.object.delete()
        else:
            pass
    
    bpy.ops.object.select_all(action='DESELECT')

def clear_mesh():
    """
    Clears all meshes in the scene.
    """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.ops.object.delete()
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

def set_unit_cube():
    """Sets the default cube to a transparent unit cube.

    Bottom left corner is (0,0,0)
    Furthest corner from (0,0,0) is (1,1,1)

    Not necessary for creating NOCS map, but is helpful for visualisation.
    """
    # set cube transparent
    bpy.data.objects["Cube"].data.materials[0].diffuse_color[3] = 0
    
    # set location
    bpy.data.objects["Cube"].location[0] += -1
    bpy.data.objects["Cube"].location[1] += -1
    bpy.data.objects["Cube"].location[2] += 1
    
    # update
    bpy.context.view_layer.update()
    
    # re-set origin of the cube
    scene = bpy.context.scene
    for ob in scene.objects:
        ob.select_set(False)
        if ob.type == 'MESH' and ob is bpy.data.objects['Cube']:
            ob.select_set(True)
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    
    # update
    bpy.context.view_layer.update()
    
    # scale to create the unit cube
    bpy.data.objects["Cube"].scale[0] /= 2
    bpy.data.objects["Cube"].scale[1] /= 2
    bpy.data.objects["Cube"].scale[2] /= 2

def select_my_object():
    scene = bpy.context.scene
    for ob in scene.objects:
        ob.select_set(False)
        if ob.type == 'MESH' and ob.name != 'Cube':
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
    obj = bpy.context.view_layer.objects.active
    return obj

def get_space_dag(obj):
    """ Calculates the Space Diagonal of a 3D box. 
    
    3D Pythagoras Theorem.
    """
    a = obj.dimensions[0] * 1000 # 1000 because convert meter to millimeter
    b = obj.dimensions[1] * 1000
    c = obj.dimensions[2] * 1000
    print("Object dimensions: ({:.2f}, {:.2f}, {:.2f})".format(a,b,c))
    space_dag = math.sqrt( math.pow(a,2) + math.pow(b,2) + math.pow(c,2) )
    print("Space diagonal:", space_dag)
    return space_dag
    
def make_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)
        
def clear_mesh():
    """
    Clears all meshes in the scene.
    """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH' or obj.type == 'LAMP':
            obj.select_set(True)
            bpy.ops.object.delete()
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

def compute():
    # Init stuff
    objs_path = "/media/DATA/SOM_renderer_DATA/objects/centered"
    objs_categories = ["box", "nonstem", "stem"]

    # Get information about the objects
    f = open("/media/DATA/SOM_renderer_DATA/objects/object_datastructure.json")
    objects_info = json.load(f)
    f = open("/media/DATA/SOM_renderer_DATA/objects/object_string2id.json")
    string2id = json.load(f)

    # Init summations
    scale_factor_sum = {'box': 0, 'nonstem': 0, 'stem': 0}
    
    clear_scene()

    # get all .glb models
    cat_objects = [_ for _ in os.listdir(objs_path) if _.endswith(".glb")]

    counter = 0 

    # Loop over these models
    for obj_path in cat_objects:

        # Get the category of this object
        object_id = string2id[obj_path[:-4]]
        object_category_id = objects_info["objects"][object_id]["category"]
        object_category_name = objects_info["categories"][object_category_id]["name"]
        print(obj_path, object_id, object_category_id, object_category_name)

        if object_id in [10,32,37,45,11,2,4,21,1,46,33,23]:
            print("Object not in train set. Skipping...")
        else:
            # Import object into the scene
            bpy.ops.import_scene.gltf(filepath=os.path.join(objs_path,obj_path))

            # de-select previous stuff
            bpy.ops.object.select_all(action='DESELECT')

            # Select object
            obj = select_my_object()

            # Init some things
            obj_mesh_name = obj.data.name
            obj.show_texture_space = True
            bpy.data.meshes[obj_mesh_name].use_auto_texspace = False

            # -- Compute scale: calculate the rectangular cuboid space diagonal
            space_dag = get_space_dag(obj)
            print("space_dag:", space_dag)
            scale_factor_sum[object_category_name] += space_dag

            # Clear scene
            clear_scene()

            # Remove the object
            clear_mesh()
            counter+=1 

    print("coutner:", counter)
    for cat in objs_categories:
        scale_factor_avg = scale_factor_sum[cat] / (counter/3)
        print("Average scale factor for {} is {}.".format(cat, scale_factor_avg))

"""

WHOLE SOM:
Average scale factor for box is 256.0874845053928.
Average scale factor for nonstem is 145.174812977167.
Average scale factor for stem is 152.3643013772757.

ONLY TRAIN:
Average scale factor for box is 263.975385487663.
Average scale factor for nonstem is 145.58462366809738.
Average scale factor for stem is 156.92298518478205.

"""
compute()