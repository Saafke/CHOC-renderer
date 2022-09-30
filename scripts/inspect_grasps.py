"""
Script to
- Load grasp and corresponding object
- Render and save an image of them, so we can know what's wrong

$ blender --python scripts/inspect_grasps.py -- /media/xavier/DATA/SOM_renderer_DATA
"""
import bpy, bmesh

# Import python dependencies
import sys
sys.path.append("/home/xavier/Documents/ObjectPose/code-from-source/new_SOM_renderer")
sys.path.append('/home/xavier/anaconda3/envs/som-env/lib/python3.10/site-packages')
import utils_blender
import os
import json
import math
import mathutils

def align_forearm_with_pos_yaxis():

	# SELECT HAND
	for ob in bpy.data.objects:
		if ob.name == "f_avg":
			ob.select_set(True)
			bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
	ob = bpy.context.object
	bpy.ops.object.mode_set( mode = 'EDIT' )
	me = ob.data
	bm = bmesh.from_edit_mesh(me)
	vertices = [v for v in bm.verts]
	B = vertices[108] # near the forearm
	A = vertices[162] # near the hand
	print("index, coord of vertex 108:", B.index, B.co)
	print("index, coord of vertex 162:", A.index, A.co)

	draw=True
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

	print(A_to_B)
	print(Y)
	
	# Convert to 2D
	A_to_B.resize_2d()
	Y.resize_2d()

	print(A_to_B)
	print(Y)

	# Get angle
	angle = A_to_B.angle(Y)
	print("angle:", math.degrees(angle))
	angle = A_to_B.angle_signed(Y)
	print("angle_signed (radians, degrees):",angle, math.degrees(angle))
	
	xx=json5
	bpy.ops.object.mode_set( mode = 'OBJECT' )

	# Rotate both object and hand
	for ob in bpy.data.objects:
		if ob.type == 'MESH':
			ob.rotation_mode = 'XYZ'
			ob.rotation_euler[2] = -1*angle

	# Back to object mode
	#bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


# Get arguments from command
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
DATA_FOLDER = argv[0]
utils_blender.clear_mesh()

# Initialize camera
cam_obj = bpy.data.objects['Camera']
cam_obj.rotation_mode = 'XYZ'
cam_obj.location[0] = 1
cam_obj.location[1] = -0.92
cam_obj.location[2] = 0.56
cam_obj.rotation_euler[0] = math.radians(72)
cam_obj.rotation_euler[1] = 0
cam_obj.rotation_euler[2] = math.radians(46.2)

# GraspINFO
f = open(os.path.join(DATA_FOLDER, 'grasps', 'grasp_datastructure.json'))
grasps_info = json.load(f)
# GraspID 2 ObjectID mapping
f = open(os.path.join(DATA_FOLDER, 'grasps', 'graspId_2_objectId.json'))
graspID_to_objectID = json.load(f)
# Loop over grasps
grasp_folder = os.path.join(DATA_FOLDER, 'grasps', 'meshes')
grasps = os.listdir(grasp_folder)
grasps.sort()

for g in grasps:
	
	g = "0010.glb"
	
	# Get the grasp path and index
	grasp_path = os.path.join(DATA_FOLDER, 'grasps', 'meshes', g)
	if g == "0000.glb":
		graspIdx = 0
	else:
		graspIdx = g[:-4].lstrip("0")
		graspIdx = int(graspIdx)
	
	# Get corresponding info of this grasp by looking into the JSON
	#object_string = grasps_info['grasps'][graspIdx]['object_string']
	#object_id = grasps_info['grasps'][graspIdx]['object_id']

	# Load both grasp and object
	model_string = graspID_to_objectID[str(graspIdx)]
	model_path = os.path.join(DATA_FOLDER, 'objects', 'centered', "{}.glb".format(model_string))
	bpy.ops.import_scene.gltf(filepath=model_path)
	bpy.ops.import_scene.gltf(filepath=grasp_path)
	
	# TODO: align the forearm with the camera line
	align_forearm_with_pos_yaxis()

	# Save render
	sce = bpy.context.scene.name
	bpy.data.scenes[sce].render.filepath = os.path.join('/home/xavier/Desktop/outputs', '{}.png'.format(g[:-4]))
	bpy.ops.render.render(write_still=True)  

	# clear meshes
	utils_blender.clear_mesh()
print("Done!")