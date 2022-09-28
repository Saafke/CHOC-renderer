"""
blender --background --python xavier_graspit_to_blender_g.py

In this script:
- Loop over all of the 144 mano parameters
- Load the posed SMPL mesh
- Save as .glb file
"""

import sys
sys.path.append(".")
sys.path.append("mano_v1_2/webuser")
sys.path.append('/home/xavier/anaconda3/envs/som-env/lib/python3.10/site-packages')
import os
import random
import bpy
import numpy as np
from serialization import load_model
from smpl_handpca_wrapper import load_model as smplh_load_model
from obman_render import (mesh_manip, render, texturing, conditions, imageutils,
                         camutils, coordutils, depthutils)
from obman_render.grasps.grasputils import read_grasp_folder
import cv2
import json
import pickle
from mathutils import Matrix
import math
import bmesh

from bs4 import BeautifulSoup

# argv = sys.argv
# argv = argv[argv.index("--") + 1:]  # get all args after "--"
# indexxx = argv[0]

def grasp_string_to_pose(grasp_string):
    cat = grasp_string.split("_")[3]
    if grasp_string[:4] == "left":
        grasp_string = "right" + grasp_string[4:]
    xml_path = os.path.join('/home/xavier/.graspit/worlds/', cat, "{}.xml".format(grasp_string))
    
    # Get XML data
    with open(xml_path, 'r') as f:
        data = f.read()
    Bs_data = BeautifulSoup(data, "xml")

    # Get the pose
    fT = Bs_data.find_all('fullTransform')
    graspable_bodypose = fT[0]
    s = str(graspable_bodypose)
    pose = s[16:-16].split(")")
    left = pose[0].split(" ")
    right= pose[1].replace("[","").replace("]","").split(" ")
    quaternion = float(left[0]), float(left[1]), float(left[2]), float(left[3])
    translation = float(right[0]), float(right[1]), float(right[2])
    print("quaternion:", quaternion) 
    print("translation:", translation)

    return quaternion, translation

def id2objectIDstring(grasp_string):
    cat = grasp_string.split("_")[3]
    print(grasp_string)
    if grasp_string[:4] == "left":
        grasp_string = "right" + grasp_string[4:]
    print(grasp_string)
    # Reading the data inside the xml
    # file to a variable under the name
    # data
    xml_path = os.path.join('/home/xavier/.graspit/worlds/', cat, "{}.xml".format(grasp_string))
    print(xml_path)
    
    with open(xml_path, 'r') as f:
        data = f.read()
    
    print(type(data))
    # Passing the stored data inside
    # the beautifulsoup parser, storing
    # the returned object
    Bs_data = BeautifulSoup(data, "xml")
    
    # Finding all instances of tag
    # `unique`
    b_unique = Bs_data.find_all('filename')
    
    temp1 = str(b_unique[0]); print("temp1:", temp1, type(temp1))
    result = temp1.split("/")[4].split(".")[0]
    print("objectID string:", result)
    return result

def clear_scene():
    """
    Clears cameres, lights, and cube.
    """
    # Go into Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')
    # Deselect
    bpy.ops.object.select_all(action='DESELECT')
    # Loop over all objects in the scene
    for obj in bpy.data.objects:
        # Delete camera and light
        if obj.type == 'CAMERA' or obj.type == 'LIGHT':
            obj.select_set(True)
            bpy.ops.object.delete()
        # Delete standard Cube
        elif obj.type == 'MESH':
            #if obj.name == 'Cube':
            obj.select_set(True)
            bpy.ops.object.delete()
        else:
            pass
    # Deselect again
    bpy.ops.object.select_all(action='DESELECT')


# INIT
smpl_model_path = "mano_v1_2/models/SMPLH_female.pkl"

# Init Blender scene
scene = bpy.data.scenes['Scene']

# Load SMPL vertex indices by body part
f = open('smpl_vert_segmentation.json')
smpl_vertex_indices = json.load(f)
right_hand_indices = smpl_vertex_indices["rightHand"]
rightHandIndex1_indices = smpl_vertex_indices["rightHandIndex1"]
right_forearm_indices = smpl_vertex_indices["rightForeArm"]

# Load MYGRASPIT! pose
f = open('/home/xavier/Documents/ObjectPose/code-from-source/mano_grasp/mano_grasp/mano_outputs/grasp_dict.json')
all_grasps = json.load(f)

# for grasp_index in all_grasps:
for grasp_index in all_grasps:
# for grasp_index in range(int(indexxx),145):

    # Remove everything from scene
    clear_scene()

    # Load current grasp
    data = all_grasps[str(grasp_index)]

    # Get the string
    grasp_string = data['body'][:-4]

    # Load smpl2mano correspondences
    right_smpl2mano = np.load('assets/models/smpl2righthand_verts.npy')
    # Load SMPL+H model and grasp infos
    ncomps = 45
    # Load SMPL mesh
    smplh_model = smplh_load_model(smpl_model_path, ncomps=2 * ncomps, flat_hand_mean=True)
    # Load MANO mesh
    mano_model = load_model("mano_v1_2/models/MANO_RIGHT.pkl")
    mano_mesh = bpy.data.meshes.new('Mano')
    mano_mesh.from_pydata(list(np.array(mano_model.r)), [], list(mano_model.f))
    mano_obj = bpy.data.objects.new('Mano', mano_mesh)
    bpy.context.collection.objects.link(mano_obj)
    mano_obj.hide_render = True
    # Load SMPL
    smpl_data_path = 'assets/SURREAL/smpl_data/smpl_data.npz'
    smpl_data = np.load(smpl_data_path)
    smplh_verts, faces = smplh_model.r, smplh_model.f
    smplh_obj = mesh_manip.load_smpl()
    # Smooth the edges of the body model
    bpy.ops.object.shade_smooth()

    # Set Mano Translation
    if 'mano_trans' in data:
        print("mano_trans is indeed in <grasp>")
        mano_model.trans[:] = [val for val in data['mano_trans']][0]
    else:
        mano_model.trans[:] = data['hand_trans']
        print("Here grasp hand_trans")
    # Set Mano Pose
    mano_model.pose[:] = data['mano_pose']
    # Alter the mesh to the pose
    mesh_manip.alter_mesh(mano_obj, mano_model.r.tolist())
    # With hand-pose
    def get_inv_hand_pca(mano_path='mano_v1_2/models/MANO_RIGHT.pkl'):
        with open(mano_path, 'rb') as f:
            hand_r = pickle.load(f, encoding='latin1')
        hands_pca_r = hand_r['hands_components']
        inv_hand_pca = np.linalg.inv(hands_pca_r)
        return inv_hand_pca
    inv_hand_pca = get_inv_hand_pca()
    grasp_pca_pose = np.array(data['mano_pose'][3:]).dot(inv_hand_pca)

    # Set a RANDOM SMPL mesh parameterization
    hand_pose = None
    hand_pose_offset = 3
    z_min = 0.5 # Min distance to camera
    z_max = 0.8 # Max distance to camera
    split = 'train'
    hand_pose_var = 2
    smplh_verts, posed_model, meta_info = mesh_manip.randomized_verts(
        smplh_model,
        smpl_data,
        ncomps= 2 * ncomps,
        z_min=z_min,
        z_max=z_max,
        side='right',
        hand_pose=grasp_pca_pose,
        hand_pose_offset=0,
        random_shape=False,
        random_pose=True,
        body_rot=False,
        split=split)
    # Center mesh on center_idx
    mesh_manip.alter_mesh(smplh_obj, smplh_verts.tolist())

    # Correctly rotate and translate
    rigid_transform = coordutils.get_rigid_transform_posed_mano(posed_model, mano_model)
    mat = np.array(rigid_transform)
    R = mat[:3,:3]
    Rt = R.transpose()
    T = mat[:3,3]
    newT = (-1*Rt).dot(T)
    # Populate new matrix
    new = np.zeros((4,4))
    new[:3,:3] = Rt
    new[:3, 3] = newT
    new[3, :3] = 0
    new[3, 3] = 1
    smplh_obj.matrix_world = Matrix(new)
    for ob in bpy.data.objects:
        if ob.name == "f_avg":
            obj = ob
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    #obj.scale = (obj_scale, obj_scale, obj_scale)
    obj.scale = (1, 1, 1)

    # xavier:
    mano_obj.rotation_euler[0] = obj.rotation_euler[0] + math.radians(90)
    smplh_obj.rotation_euler[0] = obj.rotation_euler[0] + math.radians(90)
    smplh_obj.rotation_euler[2] = obj.rotation_euler[2] - math.radians(90)

    for ob in bpy.data.objects:
        if ob.name == "Light" or ob.name == "Camera" or ob.name == "Mano":
            ob.select_set(True)
        elif ob.name == "f_avg":
            ob.select_set(True)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            ob.select_set(False)
    bpy.ops.object.delete()
    for ob in bpy.data.objects:
        if ob.name == "f_avg":
            ob.select_set(True)
    ob = bpy.context.object

    # TODO: remove vertices
    #ob = bpy.context.object
    bpy.ops.object.mode_set( mode = 'EDIT' )
    me = ob.data
    bm = bmesh.from_edit_mesh(me)
    # verts = [v for v in bm.verts if v.co[1] &gt; 0]
    vertices = [v for v in bm.verts]
    oa = bpy.context.active_object
    vertices_to_delete = []
    for vert in vertices:
        if not vert.index in right_hand_indices and \
           not vert.index in rightHandIndex1_indices and \
           not vert.index in right_forearm_indices:
            vert.select = True
            vertices_to_delete.append(vert)
        else:
            vert.select = False
    bpy.ops.mesh.dissolve_verts()


    # Rotate hand+forearm mesh 90 degrees about Z-Axis
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    ob.rotation_euler[2] = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)

    # TODO: Let's repair the pose of the hand...
    quat, translation = grasp_string_to_pose(grasp_string)
    # W,X,Y,Z -> X,-Z,Y,W
    quat = [quat[1], -quat[3], quat[2], quat[0]]
    # X,Y,Z, -> X,-Z,Y
    translation = [translation[0], -translation[2], translation[1]]

    print("quat:", quat)
    print("trans_vec:", translation)
    
    # Convert to Transformation Matrix 4x4
    from scipy.spatial.transform import Rotation as R
    r = R.from_quat(quat)
    rot_matrix = r.as_matrix()
    transformation_matrix = np.zeros((4,4))
    transformation_matrix[:3,:3] = rot_matrix
    transformation_matrix[:3,3] = np.transpose(translation)
    transformation_matrix[3,3] = 1

    # Invert Transformation Matrix 4x4
    transformation_matrix_inv = np.linalg.inv(transformation_matrix)
    print(transformation_matrix)
    print(transformation_matrix_inv)

    # Extract quaternion and translation
    rot_matrix = transformation_matrix_inv[:3,:3]
    r = R.from_matrix(rot_matrix)

    # CORRECT! - NOTE that this is (x,y,z,w) format
    quat_inv = r.as_quat()
    trans_vec = transformation_matrix_inv[:3,3]

    print("inverted quat (x,y,z,w):", quat_inv)
    print("inverted trans_vec:", trans_vec)

    # Now, lets transform back the HAND
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion[0] = quat_inv[3] # W
    ob.rotation_quaternion[1] = quat_inv[0] # X
    ob.rotation_quaternion[2] = quat_inv[1] # Y
    ob.rotation_quaternion[3] = quat_inv[2] # Z
    ob.location[0] = trans_vec[0] / 1000 # W
    ob.location[1] = trans_vec[1] / 1000 # X
    ob.location[2] = trans_vec[2] / 1000 # Y
    bpy.ops.object.transform_apply(rotation=True, location=True)

    # # Let's import the object and inspect grasp + object
    if True:
        print("/home/xavier/Documents/ObjectPose/code-from-source/SOM_renderer/DATA")
        cat = grasp_string.split("_")[3]
        object_stringgg = id2objectIDstring(grasp_string)
        ppp = os.path.join("/home/xavier/Documents/ObjectPose/code-from-source/SOM_renderer/DATA/OBJECTS/centered", cat, "{}.glb".format(object_stringgg))
        bpy.ops.import_scene.gltf(filepath=ppp)
        xx = json5
    
    # Save to .glb file
    bpy.ops.export_scene.gltf(filepath="xavier_outputs/{}.glb".format(grasp_string),
                              export_format='GLB',
                              use_selection=True
                              )

    # Mirror the hand mesh about the global X-axis
    bpy.ops.transform.mirror(constraint_axis=(True, False, False), orient_type='GLOBAL')
    left_grasp_string = "left" + grasp_string[5:]
    
    # Save left hand version
    bpy.ops.export_scene.gltf(filepath="xavier_outputs/{}.glb".format(left_grasp_string),
                              export_format='GLB',
                              use_selection=True
                              )

    print("Saved:", left_grasp_string)
    print("Saved:", grasp_string)
    #input("Here, check xavier_outputs. Press Enter for next...")

print("Done. Check xavier_outputs.")