"""This creates the NOCS Map for the .glb models.

run command: `blender --python create_nocs.py` (opens blender)
"""

import sys
#sys.path.append("/usr/local/lib/python3.6/dist-packages/")
sys.path.append("/home/weber/.local/lib/python3.7/site-packages")


import bpy
import math
import os
import numpy as np
#import chumpy as ch
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

def create_coord_map(obj):
    """Create normalized coordinate map as a color map
    
    Some code from https://github.com/YoungXIAO13/ObjectPoseEstimationSummary
    """
    mesh = obj.data
    vert_list = mesh.vertices
    
    # vcos = [obj.matrix_world @ v.co for v in vert_list]
    
    # x, y, z = [[v[i] for v in vcos] for i in range(3)]
    # min_x, min_y, min_z = min(x), min(y), min(z)
    # max_x, max_y, max_z = max(x), max(y), max(z)
    # size_x, size_y, size_z = max(x) - min(x), max(y) - min(y), max(z) - min(z)
    
    # get the color map to create as coordinate map
    if mesh.vertex_colors:
        color_map = mesh.vertex_colors.active
    else:
        color_map = mesh.vertex_colors.new()


    # print("MINIMUMS", min_x, min_y, min_z)
    # print("MAXIMUMS", max_x, max_y, max_z)
    # print("SIZES", size_x, size_y, size_z)
    
    max_r, max_g, max_b = 0, 0, 0

    allrgbs = []

    # apply the corresponding color to each vertex
    i = 0
    for poly in mesh.polygons:
        for idx in poly.loop_indices: #vertices
            loop = mesh.loops[idx]
            v = vert_list[loop.vertex_index]
            
            r = -v.co.y
            g = v.co.z # NOCS uses y up world
            b = -v.co.x
            
            # r = v.co.x
            # g = v.co.z # NOCS uses y up world
            # b = v.co.y
            color_map.data[i].color = (r,g,b,0) # rgba
            i += 1
    
    #print("Scales:",  2*np.abs(max_r), 2*np.abs(max_g),  2*np.abs(max_b))
    #print("Scales:",  max_r - (1-max_r), max_g - (1-max_g),  max_b - (1-max_b))
    mat = bpy.data.materials.new('nocs_material')
    
    # deactivate shadows
    mat.shadow_method = 'NONE'
    
    # set to vertex paint mode to see the result
    #bpy.ops.object.mode_set(mode='VERTEX_PAINT')
    
    obj.data.materials.clear()

    if mesh.materials:
        print("first material will be nocs: bad i think")
        mesh.materials[0] = mat
    else:
        print("add material: good i think")
        mesh.materials.append(mat)

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
    a = obj.dimensions[0]
    b = obj.dimensions[1]
    c = obj.dimensions[2]
    print("Object dimensions:", a,b,c)
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

def loop():
    # Init stuff
    objs_path = "/media/weber/Windows-HDD/myNOCS/objects/curate16/objects-centred/"
    #objs_more_vertices_path = "/media/weber/Windows-HDD/myNOCS/objects/curate16/objects-centred-and-more-vertices"
    objs_categories = ["box", "non-stem", "stem"]
    save_path = "/media/weber/Windows-HDD/myNOCS/objects/curate16/objects_nocs_y-up"
    scales_path = "/media/weber/Windows-HDD/myNOCS/objects/curate16/objects-scales"

    # make save dirs for all object cats
    for cat in objs_categories:
        print(os.path.join(save_path,cat))
        make_folder(os.path.join(save_path,cat))
        make_folder(os.path.join(scales_path,cat))

    # Loop over categories
    for cat in objs_categories:
        
        im_count = 1

        # get all .glb models
        cat_objects = [_ for _ in os.listdir(objs_path+cat) if _.endswith(".glb")]

        # Loop over these models
        for obj_path in cat_objects:
            
            # Import object into the scene
            bpy.ops.import_scene.gltf(filepath=os.path.join(objs_path,cat,obj_path))

            # de-select previous stuff
            bpy.ops.object.select_all(action='DESELECT')

            # Select object
            obj = select_my_object()

            
            # -- Normalize object, need to calculate the rectangular cuboid space diagonal
            space_dag = get_space_dag(obj)
            obj.scale /= space_dag 

            #update
            bpy.context.view_layer.update()

            # CHECK if normalized correctly
            a = obj.dimensions[0]
            b = obj.dimensions[1]
            c = obj.dimensions[2]
            assert math.isclose(get_space_dag(obj), 1, abs_tol=1e-6)

            # Translate object to centre of unit cube
            obj.location[0] -= 0.5
            obj.location[1] -= 0.5
            # reset the scale to be just 1; and the rotation to 0,0,0
            bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
            obj.location[2] += (1 - obj.dimensions[2]) / 2
            
            # update
            bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
            bpy.context.view_layer.update()

            ### Get the scales, save it to text path
            x = obj.dimensions[0]
            y = obj.dimensions[1]
            z = obj.dimensions[2]
            txt_path = os.path.join(scales_path, cat, obj_path[:-4]+".txt")
            np.savetxt(txt_path, [x,z,y])
            ###

            # Color code it (i.e. make NOCS map material)
            create_coord_map(obj)

            
            # -- De-normalize object
            # translate back to centre
            obj.location[0] += 0.5
            obj.location[1] += 0.5
            obj.location[2] -= (1 - obj.dimensions[2]) / 2

            # reset origin, this gets shifted in the process
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

            # scale back to original
            obj.scale *= space_dag 

            # Give object rotation and location (0,0,0), and scale 1
            bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

            # Clear scene
            clear_scene()

            # Save 
            bpy.ops.export_scene.gltf(export_format='GLB', filepath=os.path.join(save_path, cat, obj_path))

            im_count += 1
            
            print("{}:{}/{}".format(cat, im_count, len(cat_objects)))

            # Remove the object
            clear_mesh()

def single():
    # ------- old ---------- single object ------------
    
    # Load CENTERED .glb file, let's try a box first
    #bpy.ops.import_scene.gltf(filepath="/media/weber/Windows-HDD/myNOCS/objects/curate16/objects-centred/box/7685495f6e5aac1339a00425b5e3771a.glb")
    #bpy.ops.import_scene.gltf(filepath="/media/weber/Windows-HDD/myNOCS/objects/curate16/objects-centred/box/lol.glb")
    #bpy.ops.import_scene.gltf(filepath="/media/weber/Windows-HDD/myNOCS/objects/curate16/objects-centred-and-more-vertices/box/1dd407598b5850959b1500745a428d00.glb")
    #bpy.ops.import_mesh.ply(filepath="/home/weber/best.ply")
    bpy.ops.import_scene.gltf(filepath="/home/weber/human3.glb")

    # de-select previous stuff
    bpy.ops.object.select_all(action='DESELECT')

    # Select object
    obj = select_my_object()

    
    # -- Normalize object, need to calculate the rectangular cuboid space diagonal
    space_dag = get_space_dag(obj)
    obj.scale /= space_dag 

    #update
    bpy.context.view_layer.update()

    # CHECK if normalized correctly
    assert math.isclose(get_space_dag(obj), 1, abs_tol=1e-6)

    # Translate object to centre of unit cube
    obj.location[0] -= 0.5
    obj.location[1] -= 0.5
    obj.location[2] += (1 - obj.dimensions[2]) / 2
    
    # update
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    bpy.context.view_layer.update()

    # Color code it (i.e. make NOCS map material)
    create_coord_map(obj)

    
    # -- De-normalize object
    #translate back to centre
    obj.location[0] += 0.5
    obj.location[1] += 0.5
    obj.location[2] -= (1 - obj.dimensions[2]) / 2

    # reset origin, this gets shifted in the process
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

    # scale back to original
    obj.scale *= space_dag 

    # Give object rotation and location (0,0,0), and scale 1
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

    # TODO:MAYBE DELETE THIS LINE BEFORE SAVING back to vertex_paint just for showing
    #bpy.ops.object.mode_set(mode='VERTEX_PAINT')

def single_fix_bug():

    # Load CENTERED .glb file, let's try a box first
    #bpy.ops.import_scene.gltf(filepath="/home/weber/Documents/from-source/6DPoseAnnotator/xavier/9_centred.glb")
    #bpy.ops.import_scene.gltf(filepath="/media/weber/Windows-HDD/myNOCS/objects/curate16/objects-centred/box/lol.glb")
    #bpy.ops.import_scene.gltf(filepath="/home/weber/human.glb")

    # de-select previous stuff
    bpy.ops.object.select_all(action='DESELECT')

    # Select object
    obj = select_my_object()

    # Init some things
    obj_mesh_name = obj.data.name
    obj.show_texture_space = True
    bpy.data.meshes[obj_mesh_name].use_auto_texspace = False

    
    # -- Normalize object, need to calculate the rectangular cuboid space diagonal
    space_dag = get_space_dag(obj)
    obj.scale /= space_dag 

    #update
    bpy.context.view_layer.update()

    # CHECK if normalized correctly
    assert math.isclose(get_space_dag(obj), 1, abs_tol=1e-6)

    # Translate object to centre of unit cube
    obj.location[0] -= 0.5
    obj.location[1] -= 0.5
    obj.location[2] += (1 - obj.dimensions[2]) / 2
    
    # update
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
    bpy.context.view_layer.update()

    # Color code it (i.e. make NOCS map material)
    #create_coord_map(obj)

    
    # # -- De-normalize object
    # translate back to centre
    obj.location[0] += 0.5
    obj.location[1] += 0.5
    obj.location[2] -= (1 - obj.dimensions[2]) / 2

    # reset origin, this gets shifted in the process
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

    # # -- De-normalize texture space
    bpy.data.meshes[obj_mesh_name].texspace_location[0] = 0
    bpy.data.meshes[obj_mesh_name].texspace_location[1] = 0
    bpy.data.meshes[obj_mesh_name].texspace_location[2] = obj.dimensions[2] / 2
    bpy.data.meshes[obj_mesh_name].texspace_size = 0.5, 0.5, 0.5

    # scale object back to original
    obj.scale *= space_dag 

    # # Give object rotation and location (0,0,0), and scale 1
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

    # Change texture space again
    bpy.data.meshes[obj_mesh_name].texspace_location[2] *= space_dag
    bpy.data.meshes[obj_mesh_name].texspace_size = 0.5 *space_dag, 0.5 *space_dag, 0.5 *space_dag

    # Save texture space (i.e. the bounding box) information to .txt file
    np.savetxt("./texture_space_example.txt", [bpy.data.meshes[obj_mesh_name].texspace_size[0]])

    mat = bpy.data.materials
    for m in mat:
        nocs_mat = m 

    # get the nodes
    mat_nodes = nocs_mat.node_tree.nodes
    mat_links = nocs_mat.node_tree.links
    for n in mat_nodes:
        if n.name == "Vertex Color":
            mat_vertex_node = n
        if n.name == "Material Output":
            mat_output_node = n
        if n.name == "Principled BSDF":
            for link in n.inputs[0].links:
                nocs_mat.node_tree.links.remove(link)
    # set new node - texture coordinate
    tex_node = mat_nodes.new('ShaderNodeTexCoord')
    # set new link - bypassing principle node
    mat_links.new(tex_node.outputs["Generated"], mat_output_node.inputs[0])        
    ####

def loop_fix_bug():
    # Init stuff
    objs_path = "DATA/OBJECTS/centered/"
    objs_categories = ["box", "non-stem", "stem"]
    save_path = "DATA/OBJECTS/nocs_y-up"
    scales_path = "DATA/OBJECTS/scales"
    save_txt_dir = 'DATA/OBJECTS/texture_spaces'


    # make save dirs for all object cats
    for cat in objs_categories:
        #print(os.path.join(save_path,cat))
        make_folder(os.path.join(save_path,cat))
        make_folder(os.path.join(scales_path,cat))
        make_folder(os.path.join(save_txt_dir,cat))

    # Loop over categories
    for cat in objs_categories:
        
        scale_factor_sum = 0
        
        im_count = 1

        # get all .glb models
        cat_objects = [_ for _ in os.listdir(objs_path+cat) if _.endswith(".glb")]

        # Loop over these .glb models
        for obj_path in cat_objects:
            
            # Import .glb object into the scene
            bpy.ops.import_scene.gltf(filepath=os.path.join(objs_path,cat,obj_path))

            # de-select previous stuff
            bpy.ops.object.select_all(action='DESELECT')

            # Select object
            obj = select_my_object()

            # Init some things
            obj_mesh_name = obj.data.name
            obj.show_texture_space = True
            bpy.data.meshes[obj_mesh_name].use_auto_texspace = False

            
            # -- Normalize object, need to calculate the rectangular cuboid space diagonal
            space_dag = get_space_dag(obj)
            obj.scale /= space_dag 
            scale_factor_sum += space_dag

            #update
            bpy.context.view_layer.update()

            # CHECK if normalized correctly
            a = obj.dimensions[0]
            b = obj.dimensions[1]
            c = obj.dimensions[2]
            assert math.isclose(get_space_dag(obj), 1, abs_tol=1e-6)

            # Translate object to centre of unit cube
            obj.location[0] -= 0.5
            obj.location[1] -= 0.5
            # reset the scale to be just 1; and the rotation to 0,0,0
            bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
            obj.location[2] += (1 - obj.dimensions[2]) / 2
            
            # update
            bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
            bpy.context.view_layer.update()

            ### Get the scales, save it to text path
            x = obj.dimensions[0]
            y = obj.dimensions[1]
            z = obj.dimensions[2]
            txt_path = os.path.join(scales_path, cat, obj_path[:-4]+".txt")
            np.savetxt(txt_path, [x,z,y])
            ###

            # Color code it (i.e. make NOCS map material)
            #create_coord_map(obj)

            
            # -- De-normalize object
            # translate back to centre
            obj.location[0] += 0.5
            obj.location[1] += 0.5
            obj.location[2] -= (1 - obj.dimensions[2]) / 2

            # reset origin, this gets shifted in the process
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

            # # -- De-normalize texture space
            bpy.data.meshes[obj_mesh_name].texspace_location[0] = 0
            bpy.data.meshes[obj_mesh_name].texspace_location[1] = 0
            bpy.data.meshes[obj_mesh_name].texspace_location[2] = obj.dimensions[2] / 2
            bpy.data.meshes[obj_mesh_name].texspace_size = 0.5, 0.5, 0.5

            # scale object back to original
            obj.scale *= space_dag 

            # # Give object rotation and location (0,0,0), and scale 1
            bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

            # Change texture space again
            bpy.data.meshes[obj_mesh_name].texspace_location[2] *= space_dag
            bpy.data.meshes[obj_mesh_name].texspace_size = 0.5 *space_dag, 0.5 *space_dag, 0.5 *space_dag

            # Save texture space (i.e. the bounding box) information to .txt file
            save_txt_path = os.path.join(save_txt_dir, cat, obj_path[:-4])
            np.savetxt(save_txt_path, [bpy.data.meshes[obj_mesh_name].texspace_size[0]])
            
            # Clear scene
            clear_scene()

            # Save 
            bpy.ops.export_scene.gltf(export_format='GLB', filepath=os.path.join(save_path, cat, obj_path))

            im_count += 1
            
            print("{}:{}/{}".format(cat, im_count, len(cat_objects)))

            # Remove the object
            clear_mesh()

        scale_factor_avg = scale_factor_sum / 16
        print("Average scale factor for {} is {}.".format(cat, scale_factor_avg))

def camera_init():

    # Initialize camera
    cam_obj = bpy.data.objects['Camera']
    cam_obj.rotation_mode = "XYZ"
    
    cam = bpy.data.cameras['Camera']
    cam.lens = 1.93 # mm
    cam.sensor_width = 2.688 # mm
    cam.sensor_height = 1.792 # mm
    cam.sensor_fit = "HORIZONTAL" # default is "AUTO"

    # Set its location
    cam_obj.location[0] = 0.5
    cam_obj.location[1] = -3
    cam_obj.location[2] = 0.5

    # Set its rotation
    cam_obj.rotation_euler[0] = math.radians(90)
    cam_obj.rotation_euler[1] = 0
    cam_obj.rotation_euler[2] = 0
       
# -- Set the scenecamera_init
sce = bpy.context.scene
bpy.data.scenes[sce.name].view_settings.view_transform = "Raw" # Default is Filmic

#camera_init()
#set_unit_cube()
#single_fix_bug()
# single()

loop_fix_bug()

print("Ran successfully.")
#bpy.ops.wm.quit_blender()



