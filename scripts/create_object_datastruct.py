"""

"""
import os
import random
import numpy as np
import bpy
import json

def clear_scene():
	"""
	Clears all stuff (including the cube) except objects in the scene.
	"""
	#bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	for obj in bpy.data.objects:
		if obj.type == 'CAMERA' or obj.type == 'LIGHT':
			obj.select_set(True)
			bpy.ops.object.delete()
		elif obj.type == 'MESH':
			obj.select_set(True)
			bpy.ops.object.delete()
		elif obj.name[:-3] == "Camera." or obj.name[:-3] == "Light.": #removes extra light & camera objects that i added accidentily
			obj.select_set(True)
			bpy.ops.object.delete()
		else:
			pass
	bpy.ops.object.select_all(action='DESELECT')

folder = "/home/xavier/Documents/ObjectPose/code-from-source/SOM_renderer/DATA/OBJECTS (copy)"
list_objects = []

# # Get ALL object paths (all categories)
# for cat in ["box", "nonstem", "stem"]:
#     objects = os.listdir( os.path.join(folder, "centered", "box"))
#     list_objects.append(objects)
# random.shuffle(list_objects)
# print(list_objects)

objectID = 0
objects_dict = {}
objects_array = []

# Get ALL object paths (all categories)
for cat in ["box", "nonstem", "stem"]:
	
	object_files = os.listdir( os.path.join(folder, "centered", cat))

	for o_string in object_files:
		
		print(type(o_string))

		object_dict = {}

		# Extract category
		category = cat
		if category == "box":
			object_dict["category"] = 0
		elif category == "nonstem":
			object_dict["category"] = 1
		elif category == "stem":
			object_dict["category"] = 2
		else:
			raise Exception
		
		# Extract ShapeNetSem name
		shapenetsem_name = o_string[:-4]
		
		# Extract scale
		s_file = os.path.join(folder, "scales", cat, "{}.txt".format(shapenetsem_name))
		scales_array = np.loadtxt(s_file)

		# Extract texture space
		ts_file = os.path.join(folder, "texture_spaces", cat, "{}".format(shapenetsem_name))
		texture_space = np.loadtxt(ts_file)
		
		
		# Set scene
		sce = bpy.context.scene.name
		# Delete everything
		clear_scene()
		# Import object
		bpy.ops.import_scene.gltf(filepath=os.path.join(folder, "centered", cat, o_string))
		scene = bpy.context.scene
		for ob in scene.objects:
			# Extract name
			name = ob.name
			
			# Extract dimensions
			width = ob.dimensions[0]
			height = ob.dimensions[1]
			depth = ob.dimensions[2]
			
			print(width, height, depth)

		object_dict["name"] = name
		object_dict["shapenet_name"] = shapenetsem_name
		object_dict["width"] = width
		object_dict["height"] = height
		object_dict["depth"] = depth
		object_dict["texture_space_variable"] = texture_space.tolist()
		object_dict["scales"] = scales_array.tolist()

		clear_scene()
		objects_array.append(object_dict)
		objectID += 1

		print("\n")

random.shuffle(objects_array)

# Restructure so that ID is back on top
objectID = 0
new_dicts = []
for o in objects_array:
	# create new dict
	temp_dict = {}
	temp_dict["id"] = objectID
	for k, v in o.items():
		temp_dict[k] = v
	new_dicts.append(temp_dict)
	objectID+=1

objects_dict['objects'] = new_dicts

with open(os.path.join('object_datastructure.json'), 'w') as f:
	json.dump(objects_dict, f, indent=4, sort_keys=False)

print("done.")