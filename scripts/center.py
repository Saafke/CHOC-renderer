"""
Script for centering objects perfectly, according to their dimensions.
Run command: 
$ blender --python center.py
"""

import bpy
import math
import os
import numpy as np

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

def select_my_object():
    scene = bpy.context.scene
    for ob in scene.objects:
        ob.select_set(False)
        if ob.type == 'MESH' and ob.name != 'Cube':
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
    obj = bpy.context.view_layer.objects.active
    return obj

def single(path, save_path):

    sce = bpy.context.scene

    # Remove default object/camera/light
    clear_scene()

    # Import object
    bpy.ops.import_scene.gltf(filepath=path)

    # Select it
    obj = select_my_object()

    # Print current location
    print("Current location:", obj.location[0], obj.location[1], obj.location[2])

    # -- Center it, we will put the cursor in the right spot (i.e. centre of the bottom), then move the object to 0,0,0
    # set geometry to origin
    bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN")

    xverts = []
    yverts = []
    zverts = []
    # get all z coordinates of the vertices
    for face in obj.data.polygons:
        verts_in_face = face.vertices[:]
        for vert in verts_in_face:
            local_point = obj.data.vertices[vert].co
            world_point = obj.matrix_world @ local_point
            xverts.append(world_point[0])
            yverts.append(world_point[1])
            zverts.append(world_point[2])

    # Get midpoint of objects for x and y
    middlex = obj.dimensions[0] / 2
    middley = obj.dimensions[1] / 2

    # CHECKS
    print("middlex:", middlex * 100)
    print("middley:", middley * 100)
    print(min(xverts) *100, "cm", max(xverts) * 100, "cm")
    print(min(yverts) *100, "cm", max(yverts) * 100, "cm")

    # Set correct cursor location
    sce.cursor.location = ( (max(xverts) - middlex), (max(yverts) - middley), min(zverts) )

    # set the origin to the cursor
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

    # set the object to (0,0,0)
    obj.location = (0,0,0)

    # reset the cursor
    sce.cursor.location = (0,0,0)

    # APPLY CHANGES
    bpy.ops.object.transform_apply(location=True)

    xverts = []
    yverts = []
    zverts = []
    # get all z coordinates of the vertices
    for face in obj.data.polygons:
        verts_in_face = face.vertices[:]
        for vert in verts_in_face:
            local_point = obj.data.vertices[vert].co
            world_point = obj.matrix_world @ local_point
            xverts.append(world_point[0])
            yverts.append(world_point[1])
            zverts.append(world_point[2])

    print(min(xverts) *100, "cm", max(xverts) * 100, "cm")
    print(min(yverts) *100, "cm", max(yverts) * 100, "cm")
    assert math.isclose(min(xverts), -max(xverts), abs_tol=10**-8)
    assert math.isclose(min(yverts), -max(yverts), abs_tol=10**-8)

    # Save
    bpy.ops.export_scene.gltf(export_format='GLB', filepath=save_path)

# Centering one object
path = "mesh.glb"
save_path = "mesh_centered.glb"
single(path, save_path)

print("\nRan succesfully.\n")
