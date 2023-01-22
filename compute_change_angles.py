import sys
sys.path.append(".")
import os
import random
import pickle
import bpy, bmesh
import mathutils
import math
import numpy as np
np.set_printoptions(suppress=True)
import json
import time

sys.path.append('/mnt/c7dd8318-a1d3-4622-a5fb-3fc2d8819579/CORSMAL/envs/choc-render-env/lib/python3.10/site-packages')
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2
import config
from PIL import Image
from scipy.spatial.transform import Rotation as R

import node
import utils_blender
import utils_cam_light
import utils_object
import utils_projection
import utils_table

# Read arguments after "--"
argv = sys.argv
argv = argv[argv.index("--") + 1:] 
if len(argv) < 1:
	raise Exception("Please specify 1. the path to the dataset folder")
DATA_FOLDER = argv[0]

def get_change_angle(draw=False):
	"""
	We align the forearm, with the positive y-axis.
	"""
	# SELECT HAND
	for ob in bpy.data.objects:
		if ob.name == "f_avg":
			ob.select_set(True)
			bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
			forearm_mesh_obj = bpy.context.object
	# Get the two vertices, one near the end and one near the beginning of the forearm
	bpy.ops.object.mode_set( mode = 'EDIT' )
	me = forearm_mesh_obj.data
	bm = bmesh.from_edit_mesh(me)
	vertices = [v for v in bm.verts]
	B = vertices[108] # near the forearm
	A = vertices[162] # near the hand
	
	if draw:
		start = B.co
		end =  A.co
		line_mesh = bpy.data.meshes.new(name='Forearm Line Mesh')
		line_mesh.from_pydata([start,end], [[0,1]], [])
		line_mesh.update()
		line_mesh.validate()
		# create the object with the line_mesh just created
		line_obj = bpy.data.objects.new('Forearm Line', line_mesh)
		# add the Object to the scene
		bpy.context.scene.collection.objects.link(line_obj)

	# Get vector of our two points
	A_to_B = B.co - A.co
	# Y-axis vector
	Y = mathutils.Vector((0.0, 1.0, 0.0))
	# Convert to 2D (ignoring the Z-axis)
	A_to_B.resize_2d()
	Y.resize_2d()

	# Get the signed angle
	angle = A_to_B.angle_signed(Y)

	# Rotate the hand and object, about the Z-axis
	bpy.ops.object.mode_set( mode = 'OBJECT' )
	for ob in bpy.data.objects:
		if ob.type == 'MESH':
			ob.rotation_mode = 'XYZ'
			ob.rotation_euler[2] = -1*angle
			# Apply the changes
			ob.select_set(True)
			bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
			ob.select_set(False)

	return angle

# Get grasp files
grasp_folder = os.path.join(DATA_FOLDER, 'grasps', 'meshes')
grasps = os.listdir(grasp_folder)
grasps.sort()

# Get background files
background_folder = os.path.join(DATA_FOLDER, 'backgrounds', 'rgb')
background_rgbs = os.listdir(background_folder)
background_rgbs.sort()

# GraspID 2 ObjectID mapping
f = open(os.path.join(DATA_FOLDER, 'grasps', 'graspId_2_objectId.json'))
graspID_to_objectID = json.load(f)
# GraspINFO
f = open(os.path.join(DATA_FOLDER, 'grasps', 'grasp_datastructure.json'))
grasps_info = json.load(f)
# objectINFO
f = open(os.path.join(DATA_FOLDER, 'object_models', 'object_datastructure.json'))
object_info = json.load(f)

# Store mapping
mapping_graspID_2_change_angle = {}

# Loop over the grasps (and therefore also objects) (288)
for g in grasps:
	# Get the grasp path and index
	grasp_path = os.path.join(DATA_FOLDER, 'grasps', 'meshes', g)
	if g == "0000.glb":
		graspIdx = 0
	else:
		graspIdx = g[:-4].lstrip("0")
		graspIdx = int(graspIdx)
	
	print(graspIdx)
	
	# Get corresponding info of this grasp by looking into the JSON
	# object_string = grasps_info['grasps'][graspIdx]['object_string']
	# object_cat_idx = grasps_info['grasps'][graspIdx]['object_category']
	# object_cat_name = grasps_info['categories'][object_cat_idx]['name']
	# object_texspace_size = object_info['objects'][int(object_id)]['texture_space_variable']
	
	object_id = grasps_info['grasps'][graspIdx]['object_id']
	obj_name = "{}.glb".format(object_info["objects"][object_id]["shapenet_name"])
	model_path = os.path.join(DATA_FOLDER, 'object_models', 'meshes', obj_name)

	# Clear scene of mesh and light objects
	utils_blender.clear_mesh()
	utils_blender.clear_lights()

	# Import object
	bpy.ops.import_scene.gltf(filepath=model_path)
	# # Flip box with 50% percent change
	# if obj_cat_idx == 0:
	# 	print("yup this is a box")
	# 	if flip_box:
	# 		# Get object
	# 		for ob in bpy.data.objects:
	# 			if ob.type == 'MESH':
	# 				print("this mesh will be flipped:", ob.name)
	# 				ob.rotation_mode = 'XYZ'
	# 				ob.rotation_euler[2] = math.radians(180)
	# 				# Apply
	# 				bpy.ops.object.transform_apply(rotation=True)

	# Import hand
	bpy.ops.import_scene.gltf(filepath=grasp_path)
	
	# Align the forearm with the principle axis of the camera, pointing towards the camera
	angle = get_change_angle()


	mapping_graspID_2_change_angle[graspIdx] = -1*angle

print(mapping_graspID_2_change_angle)

mapping_path = "./mapping_graspID_2_changeAngle.json"
with open(mapping_path, 'w') as f:
    json.dump(mapping_graspID_2_change_angle, f, indent=4, sort_keys=True)
			
