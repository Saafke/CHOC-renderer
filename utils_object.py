import bpy, bmesh
import config
import os
import random
from PIL import Image
import numpy as np
import math
import utils_table
import utils_blender
from scipy.spatial.transform import Rotation as R
import mathutils

class ObjectUtils():
	
	def get_initial_rotation(self):
		return self.change_angle

	def re_render_object(self, obj_model, cur_obj_class, location_xyz, pose_quaternion_wxyz):
		"""Loads an object places it in the correct location,
			with the correct rotation and scale.
		"""

		# Import object
		bpy.ops.import_scene.gltf(filepath=obj_model)
		print("current object class:", cur_obj_class)

		### Set pass indices
		for o in bpy.data.objects:
			if o.name != 'Camera' and o.name != 'Light':  # if syn-object
				o.pass_index = config.obj2id[cur_obj_class]
			else:
				pass

		# Loop over meshes, set the 6D pose
		self.change_angle = 0
		scene = bpy.context.scene
		for obj in scene.objects:
			obj.select_set(False)
			# if a mesh
			if obj.type == 'MESH':
				# Place object at location
				obj.location[0] = location_xyz[0]
				obj.location[1] = location_xyz[1]
				obj.location[2] = location_xyz[2]

				obj.rotation_mode = 'QUATERNION'
				obj.rotation_quaternion[0] = pose_quaternion_wxyz[0]
				obj.rotation_quaternion[1] = pose_quaternion_wxyz[1]
				obj.rotation_quaternion[2] = pose_quaternion_wxyz[2]
				obj.rotation_quaternion[3] = pose_quaternion_wxyz[3]

				self.locationx = obj.location[0]
				self.locationy = obj.location[1]
				self.locationz = obj.location[2]

				self.rotationw = obj.rotation_quaternion[0]
				self.rotationx = obj.rotation_quaternion[1]
				self.rotationy = obj.rotation_quaternion[2]
				self.rotationz = obj.rotation_quaternion[3]

		# Select object again
		scene = bpy.context.scene
		for ob in scene.objects:
			ob.select_set(False)
			if ob.type == 'MESH':
				bpy.context.view_layer.objects.active = ob
				obj = bpy.context.view_layer.objects.active

		return [self.locationx, self.locationy, self.locationz], [self.rotationw, self.rotationx, self.rotationy,
																  self.rotationz]

	def re_render_object_and_hand(self, obj_model, grasp_model, obj_cat_idx, cur_obj_class, location_xyz, pose_quaternion_wxyz, flip_box): #, hand_texture):
		"""
		"""
		# Import object
		bpy.ops.import_scene.gltf(filepath=obj_model)
		# Flip box with 50% percent change
		if obj_cat_idx == 0:
			print("yup this is a box")
			if flip_box:
				# Get object
				for ob in bpy.data.objects:
					if ob.type == 'MESH':
						print("this mesh will be flipped:", ob.name)
						ob.rotation_mode = 'XYZ'
						ob.rotation_euler[2] = math.radians(180)
						# Apply
						bpy.ops.object.transform_apply(rotation=True)

		# Import hand
		bpy.ops.import_scene.gltf(filepath=grasp_model)
		# Align the forearm with the principle axis of the camera, pointing towards the camera
		self.align_forearm_with_pos_yaxis(draw=False)

		# Load random texture path
		all_tex_path = config.paths['textures']
		all_texs = os.listdir(all_tex_path)
		random_tex_path = random.choice(all_texs)
		print("\nTEXTURE={}\n".format(random_tex_path))
		random_tex = bpy.data.images.load(os.path.join(all_tex_path, random_tex_path))
		#all_tex_path = config.paths['textures']
		#print("\nTEXTURE={}\n".format(hand_texture))

		print("current object class:", cur_obj_class)

		### Set random hand material and pass indices
		for o in bpy.data.objects:
			if o.name == "f_avg":

				# Set pass index to 4
				o.pass_index = config.obj2id['hand']
				o.select_set(True)

				for m_slot in o.material_slots:
					mat = m_slot.material
					mat_nodes = mat.node_tree.nodes
					mat_links = mat.node_tree.links
					for n in mat_nodes:
						if n.name == "Material Output":
							mat_output_node = n
						if n.name == "Principled BSDF":
							princip_node = n

					# Set new node - image texture
					tex_node = mat_nodes.new('ShaderNodeTexImage')
					# Set image
					tex_node.image = random_tex
					# Set new link
					mat_links.new(tex_node.outputs['Color'], princip_node.inputs['Base Color'])

				o.select_set(False)
			elif o.name == 'f_avg.001':  # if second hand
				o.pass_index = config.obj2id['hand']
			elif o.name != 'Camera' and o.name != 'Light':  # if syn-object
				o.pass_index = config.obj2id[cur_obj_class]
			else:
				pass
		###

		# Loop over meshes, set the 6D pose
		scene = bpy.context.scene
		for obj in scene.objects:
			obj.select_set(False)
			# if a mesh
			if obj.type == 'MESH':
				# Place object at location
				obj.location[0] = location_xyz[0]
				obj.location[1] = location_xyz[1]
				obj.location[2] = location_xyz[2]

				obj.rotation_mode = 'QUATERNION'
				obj.rotation_quaternion[0] = pose_quaternion_wxyz[0]
				obj.rotation_quaternion[1] = pose_quaternion_wxyz[1]
				obj.rotation_quaternion[2] = pose_quaternion_wxyz[2]
				obj.rotation_quaternion[3] = pose_quaternion_wxyz[3]

				self.locationx = obj.location[0]
				self.locationy = obj.location[1]
				self.locationz = obj.location[2]

				self.rotationw = obj.rotation_quaternion[0]
				self.rotationx = obj.rotation_quaternion[1]
				self.rotationy = obj.rotation_quaternion[2]
				self.rotationz = obj.rotation_quaternion[3]

		hand_objects = []
		# Select object again
		scene = bpy.context.scene
		for ob in scene.objects:
			ob.select_set(False)
			if ob.type == 'MESH':
				if ob.name != "f_avg" or ob.name != "f_avg.001":
					bpy.context.view_layer.objects.active = ob
					obj = bpy.context.view_layer.objects.active
				if ob.name == "f_avg" or ob.name == "f_avg.001":
					print("ADDING:", ob.name)
					hand_objects.append(ob)
					ob.select_set(True)
					bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)
					ob.select_set(False)

		return hand_objects, [self.locationx, self.locationy, self.locationz], [self.rotationw, self.rotationx,
																				self.rotationy,
																				self.rotationz], flip_box #, hand_texture

	def get_location_on_table(self, config, cur_mask_bg, cur_depth_bg):
		
		# Open mask 
		mask_im = Image.open(cur_mask_bg).convert('L')
		mask_ar = np.array(mask_im)
		
		# If depth is zero, resample
		z = 0
		while(z == 0):
			# Get random pixel location on table
			y_idx, x_idx = np.where(mask_ar!=0)
			rand_idx = np.random.randint(len(y_idx))
			table_y = y_idx[rand_idx] 
			table_x = x_idx[rand_idx]

			# Get depth of that pixel
			image_og = Image.open(cur_depth_bg)
			data_og = np.asarray(image_og)
			#data_og = cv2.imread(self.cur_depth_bg, cv2.IMREAD_ANYDEPTH) # buggy
			z = data_og[table_y][table_x]
		# Get 3d coord 
		x = (table_x - config.camera_params['cx']) * z / config.camera_params['fx']
		y = (table_y - config.camera_params['cy']) * z / config.camera_params['fy']

		return x,y,z

	def get_object(self, subset):
		"""Gets a random ShapeNet object 

		Returns : model path and correct scale factor.
		"""

		# get path
		objs_path = os.path.join(config.paths['objects']) # ,subset
		objs_nocs_path = os.path.join(config.paths['objects_nocs']) # ,subset

		# get random category. options: ["stem", "non-stem", "box"]
		rnd_obj_cat = random.choice(config.data_settings['object_categories'])
		#rnd_obj_cat = "box"
		self.cur_obj_class = rnd_obj_cat

		# get all objects of this category
		cur_objects = [_ for _ in os.listdir(os.path.join(objs_path, rnd_obj_cat)) if _.endswith(".glb")]
		
		# pick random one
		rnd_obj = random.choice(cur_objects)
		print("Object = {}".format(rnd_obj))

		# get full image path
		rnd_obj_path = os.path.join(objs_path, rnd_obj_cat, rnd_obj)

		# update nocs global
		self.cur_nocs_obj_path = os.path.join(objs_nocs_path, rnd_obj_cat, rnd_obj)
		#self.cur_nocs_obj_path = os.path.join(objs_path, rnd_obj_cat, rnd_obj)
		
		# update texture space path
		self.cur_texspace_path = os.path.join(config.paths['texture_spaces'], rnd_obj_cat, rnd_obj[:-4])
		
		# Save the correct scales of this object to this image
		txt_path = os.path.join(config.paths['scales'], rnd_obj_cat, rnd_obj[:-4]+".txt")
		scales_array = np.loadtxt(txt_path)
		np.savetxt( os.path.join(config.paths['scales_dir'], 
					f"{self.im_count:06d}.txt"), 
					scales_array, 
					header= rnd_obj_cat + " " + rnd_obj + " " + self.cur_rgb_bg)

		return rnd_obj_path

	def place_object_and_hand(self, obj_model, grasp_model, obj_cat_idx, cur_obj_class, 
							  cur_depth_bg, cur_mask_bg, cur_bg,
							  normal_json, add_height=True):
		"""Loads an object + hand mesh and places it in the correct location, 
		with the correct rotation and scale.
		
		Parameters
		----------
		model : string
			The path to the model you want to import and place
		add_height : boolean
			Whether to render objects above the table
		"""

		# Import object
		bpy.ops.import_scene.gltf(filepath=obj_model)
		# Flip box with 50% percent change
		if obj_cat_idx == 0:
			print("yup this is a box")
			coinflip = random.uniform(0,1)
			if coinflip <= 0.5:
				# Get object
				for ob in bpy.data.objects:
					if ob.type == 'MESH':
						print("this mesh will be flipped:", ob.name)
						ob.rotation_mode = 'XYZ'
						ob.rotation_euler[2] = math.radians(180)
						# Apply
						bpy.ops.object.transform_apply(rotation=True)

		# Import hand
		bpy.ops.import_scene.gltf(filepath=grasp_model)
		# Align the forearm with the principle axis of the camera, pointing towards the camera
		self.align_forearm_with_pos_yaxis(draw=False)

		# Load random texture path
		all_tex_path = config.paths['textures']
		all_texs = os.listdir(all_tex_path)
		random_tex_path = random.choice(all_texs)
		print("\nTEXTURE={}\n".format(random_tex_path))
		random_tex = bpy.data.images.load(os.path.join(all_tex_path,random_tex_path))

		print("current object class:", cur_obj_class)

		### Set random hand material and pass indices
		for o in bpy.data.objects:
			if o.name == "f_avg":

				# Set pass index to 4
				o.pass_index = config.obj2id['hand']
				o.select_set(True)
				# if flip_bool:
				#     bpy.ops.transform.mirror(orient_type="LOCAL", constraint_axis=(True, False, False))

				#bpy.data.worlds["World"].cycles_visibility.diffuse = False
				for m_slot in o.material_slots:
					mat = m_slot.material
					mat_nodes = mat.node_tree.nodes
					mat_links = mat.node_tree.links
					for n in mat_nodes:
						if n.name == "Material Output":
							mat_output_node = n
						if n.name == "Principled BSDF":
							princip_node = n
							# n.inputs[0].default_value = 0,0,0,1
							# # remove old link
							# link = n.inputs['Emission'].links[0]
							# mat.node_tree.links.remove(link)
					
					# Set new node - image texture
					tex_node = mat_nodes.new('ShaderNodeTexImage')
					# Set image
					tex_node.image = random_tex
					# Set new link
					#mat_links.new(tex_node.outputs['Color'], princip_node.inputs['Emission'])     
					mat_links.new(tex_node.outputs['Color'], princip_node.inputs['Base Color'])     

				o.select_set(False)
			elif o.name == 'f_avg.001': # if second hand
				o.pass_index = config.obj2id['hand']
			elif o.name != 'Camera' and o.name != 'Light': # if syn-object
				o.pass_index = config.obj2id[cur_obj_class]
			else:
				pass
		###

		# Get location
		x,y,z = self.get_location_on_table(config, cur_mask_bg, cur_depth_bg)
		# Set location
		if add_height:
			# Get random height in mm
			rand_height = float(np.random.randint(config.random_params["min_height"], config.random_params["max_height"]))
			# init new height
			heightened_y = -y + rand_height
			# set final 3d coordinate
			self.coord = x, z, heightened_y
		# Just render object+hand on the table
		else:
			self.coord = x, z, -y


		# Set some random variables
		rand_hand_rot = math.radians(np.random.randint(-45,52))
		x_rot = math.radians(random.uniform(-1 * config.random_params["x_rotation"], config.random_params["x_rotation"]))
		y_rot = math.radians(random.uniform(-1 * config.random_params["y_rotation"], config.random_params["y_rotation"]))
		z_rot = math.radians(np.random.randint(config.random_params["z_rotation"])) # for stem & non-stem

		# Load x and y rotation, based on the table normal
		xAngle, yAngle = utils_table.load_rotation_based_on_normal(normal_json, cur_bg)
		
		# Loop over meshes
		scene = bpy.context.scene
		for obj in scene.objects:
			obj.select_set(False)
			# if a mesh
			if obj.type == 'MESH':

				# Place object at location
				obj.location[0] = x / 1000 
				obj.location[1] = z / 1000 
				if add_height:
					obj.location[2] = heightened_y / 1000
				else:
					obj.location[2] = -y / 1000 

				# TODO: freely rotate about yaw axis, for stem and non-stem

				if add_height:
					# First rotation to rotation matrix
					r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), rand_hand_rot], degrees=False)
					rot_matrix1 = r1.as_matrix()
					quat1 = r1.as_quat()
					# Second rotation to rotation matrix
					r2 = R.from_euler("YXZ", [y_rot, x_rot, 0], degrees=False)
					rot_matrix2 = r2.as_matrix()
					# Both
					rot_matrix12 = rot_matrix1 @ rot_matrix2
					# Convert to quaternion
					r12 = R.from_matrix(rot_matrix12)
					# X,Y,Z,W
					quat12 = r12.as_quat()
					obj.rotation_mode = 'QUATERNION'
					obj.rotation_quaternion[0] = quat12[3]
					obj.rotation_quaternion[1] = quat12[0]
					obj.rotation_quaternion[2] = quat12[1]
					obj.rotation_quaternion[3] = quat12[2]
				
				else: # On the table
					# First rotation to rotation matrix
					r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), rand_hand_rot], degrees=False)
					rot_matrix1 = r1.as_matrix()
					quat1 = r1.as_quat()
					obj.rotation_mode = 'QUATERNION'
					obj.rotation_quaternion[0] = quat1[3]
					obj.rotation_quaternion[1] = quat1[0]
					obj.rotation_quaternion[2] = quat1[1]
					obj.rotation_quaternion[3] = quat1[2]
				# else:
				# 	use_euler = False
				# 	# USING EULER
				# 	if use_euler:
				# 		# First, transformation is: 
				# 		obj.rotation_mode = 'ZXY' # means we should do first Y, then X, then Z
				# 		# First, yAngle
				# 		obj.rotation_euler[1] = yAngle
				# 		# Then, xAngle
				# 		obj.rotation_euler[0] = xAngle - math.radians(90)
				# 		# Then, z
				# 		obj.rotation_euler[2] = rand_hand_rot

				# 		# set
				# 		obj.select_set(True)
				# 		bpy.ops.object.transforms_to_deltas(mode='ROT') 
				# 		obj.select_set(False)
						
	def place_object(self, obj_model, obj_cat_idx, cur_obj_class, 
						   cur_depth_bg, cur_mask_bg, cur_bg,
						   normal_json):
		"""Loads an object places it in the correct location, 
			with the correct rotation and scale.
		"""

		# Import object
		bpy.ops.import_scene.gltf(filepath=obj_model)
		print("current object class:", cur_obj_class)

		### Set pass indices
		for o in bpy.data.objects:
			if o.name != 'Camera' and o.name != 'Light': # if syn-object
				o.pass_index = config.obj2id[cur_obj_class]
			else:
				pass

		location_xyz, pose_quaternion_wxyz = self.get_random_pose(False, config, cur_mask_bg, cur_depth_bg, cur_bg, normal_json)

		# # Get location
		# x,y,z = self.get_location_on_table(config, cur_mask_bg, cur_depth_bg)
		# self.coord = x, z, -y

		# # Set some random variables
		# z_rot = math.radians(np.random.randint(config.random_params["z_rotation"])) # for stem & non-stem

		# # Load x and y rotation, based on the table normal
		# xAngle, yAngle = utils_table.load_rotation_based_on_normal(normal_json, cur_bg)
		
		# Loop over meshes, set the 6D pose
		scene = bpy.context.scene
		for obj in scene.objects:
			obj.select_set(False)
			# if a mesh
			if obj.type == 'MESH':
				# Place object at location
				obj.location[0] = location_xyz[0] / 1000 
				obj.location[1] = location_xyz[1] / 1000 
				obj.location[2] = location_xyz[2] / 1000 

				obj.rotation_mode = 'QUATERNION'
				obj.rotation_quaternion[0] = pose_quaternion_wxyz[0]
				obj.rotation_quaternion[1] = pose_quaternion_wxyz[1]
				obj.rotation_quaternion[2] = pose_quaternion_wxyz[2]
				obj.rotation_quaternion[3] = pose_quaternion_wxyz[3]
					
				self.locationx = obj.location[0]
				self.locationy = obj.location[1]
				self.locationz = obj.location[2]
				
				self.rotationw = obj.rotation_quaternion[0]
				self.rotationx = obj.rotation_quaternion[1]
				self.rotationy = obj.rotation_quaternion[2]
				self.rotationz = obj.rotation_quaternion[3]

		# # Loop over meshes
		# scene = bpy.context.scene
		# for obj in scene.objects:
		# 	obj.select_set(False)
		# 	# if a mesh
		# 	if obj.type == 'MESH':

		# 		# Place object at location
		# 		obj.location[0] = x / 1000 
		# 		obj.location[1] = z / 1000 
		# 		obj.location[2] = -y / 1000 

		# 		# First rotation to rotation matrix
		# 		r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), z_rot], degrees=False)
		# 		rot_matrix1 = r1.as_matrix()
		# 		quat1 = r1.as_quat()
		# 		obj.rotation_mode = 'QUATERNION'
		# 		obj.rotation_quaternion[0] = quat1[3]
		# 		obj.rotation_quaternion[1] = quat1[0]
		# 		obj.rotation_quaternion[2] = quat1[1]
		# 		obj.rotation_quaternion[3] = quat1[2]
					
		# 		self.locationx = obj.location[0]
		# 		self.locationy = obj.location[1]
		# 		self.locationz = obj.location[2]
				
		# 		self.rotationw = obj.rotation_quaternion[0]
		# 		self.rotationx = obj.rotation_quaternion[1]
		# 		self.rotationy = obj.rotation_quaternion[2]
		# 		self.rotationz = obj.rotation_quaternion[3]
		
		# Select object again
		scene = bpy.context.scene
		for ob in scene.objects:
			ob.select_set(False)
			if ob.type == 'MESH':
				bpy.context.view_layer.objects.active = ob
				obj = bpy.context.view_layer.objects.active

		return [self.locationx, self.locationy, self.locationz], [self.rotationw, self.rotationx, self.rotationy, self.rotationz]

	def get_random_pose(self, hand_bool, config, cur_mask_bg, cur_depth_bg, cur_bg, normal_json):
		"""
		Computes the randomized 6D pose.
		"""
		location_xyz = None
		pose_quaternion_wxyz = None

		### First, set location
		x,y,z = self.get_location_on_table(config, cur_mask_bg, cur_depth_bg)
		if hand_bool:
			# Get random height in mm
			rand_height = float(np.random.randint(config.random_params["min_height"], config.random_params["max_height"]))
			# init new height
			heightened_y = -y + rand_height
			# set final 3d coordinate
			location_xyz = x, z, heightened_y
		# Just render object+hand on the table
		else:
			location_xyz = x, z, -y

		### Second, set rotation
		# Generate some random variables
		rand_hand_rot = math.radians(np.random.randint(-45,52))
		x_rot = math.radians(random.uniform(-1 * config.random_params["x_rotation"], config.random_params["x_rotation"]))
		y_rot = math.radians(random.uniform(-1 * config.random_params["y_rotation"], config.random_params["y_rotation"]))
		z_rot = math.radians(np.random.randint(config.random_params["z_rotation"])) # for stem & non-stem

		# Load x and y rotation, based on the table normal
		xAngle, yAngle = utils_table.load_rotation_based_on_normal(normal_json, cur_bg)

		if hand_bool:
			print("xrot:", math.degrees(x_rot), "yrot:", math.degrees(y_rot))
			# First rotation to rotation matrix
			r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), rand_hand_rot], degrees=False)
			rot_matrix1 = r1.as_matrix()
			quat1 = r1.as_quat()
			# Second rotation to rotation matrix
			r2 = R.from_euler("YXZ", [y_rot, x_rot, 0], degrees=False)
			rot_matrix2 = r2.as_matrix()
			# Both
			rot_matrix12 = rot_matrix1 @ rot_matrix2
			# Convert to quaternion
			r12 = R.from_matrix(rot_matrix12)
			# X,Y,Z,W
			quat12 = r12.as_quat()
			print("quat1:", quat1, "quat12:", quat12)
			pose_quaternion_wxyz = [quat12[3], quat12[0], quat12[1], quat12[2]]
			# obj.rotation_mode = 'QUATERNION'
			# obj.rotation_quaternion[0] = quat12[3]
			# obj.rotation_quaternion[1] = quat12[0]
			# obj.rotation_quaternion[2] = quat12[1]
			# obj.rotation_quaternion[3] = quat12[2]
		
		else: # On the table
			# First rotation to rotation matrix
			r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), rand_hand_rot], degrees=False)
			rot_matrix1 = r1.as_matrix()
			quat1 = r1.as_quat()
			pose_quaternion_wxyz = [quat1[3], quat1[0], quat1[1], quat1[2]]

		return location_xyz, pose_quaternion_wxyz

	def place_object_and_hand(self, obj_model, grasp_model, obj_cat_idx, cur_obj_class, 
							  cur_depth_bg, cur_mask_bg, cur_bg,
							  normal_json, add_height=True):
		"""Loads an object + hand mesh and places it in the correct location, 
		with the correct rotation and scale.
		
		Parameters
		----------
		model : string
			The path to the model you want to import and place
		add_height : boolean
			Whether to render objects above the table
		"""
		flip_box_flag = False

		# Import object
		bpy.ops.import_scene.gltf(filepath=obj_model)
		# Flip box with 50% percent change
		if obj_cat_idx == 0:
			print("yup this is a box")
			coinflip = random.uniform(0,1)
			if coinflip <= 0.5:
				flip_box_flag = True
				# Get object
				for ob in bpy.data.objects:
					if ob.type == 'MESH':
						print("this mesh will be flipped:", ob.name)
						ob.rotation_mode = 'XYZ'
						ob.rotation_euler[2] = math.radians(180)
						# Apply
						bpy.ops.object.transform_apply(rotation=True)

		# Import hand
		bpy.ops.import_scene.gltf(filepath=grasp_model)
		# Align the forearm with the principle axis of the camera, pointing towards the camera
		self.align_forearm_with_pos_yaxis(draw=False)

		# Load random texture path
		all_tex_path = config.paths['textures']
		all_texs = os.listdir(all_tex_path)
		random_tex_path = random.choice(all_texs)
		print("\nTEXTURE={}\n".format(random_tex_path))
		random_tex = bpy.data.images.load(os.path.join(all_tex_path,random_tex_path))

		print("current object class:", cur_obj_class)

		### Set random hand material and pass indices
		for o in bpy.data.objects:
			if o.name == "f_avg":

				# Set pass index to 4
				o.pass_index = config.obj2id['hand']
				o.select_set(True)
				# if flip_bool:
				#     bpy.ops.transform.mirror(orient_type="LOCAL", constraint_axis=(True, False, False))

				#bpy.data.worlds["World"].cycles_visibility.diffuse = False
				for m_slot in o.material_slots:
					mat = m_slot.material
					mat_nodes = mat.node_tree.nodes
					mat_links = mat.node_tree.links
					for n in mat_nodes:
						if n.name == "Material Output":
							mat_output_node = n
						if n.name == "Principled BSDF":
							princip_node = n
							# n.inputs[0].default_value = 0,0,0,1
							# # remove old link
							# link = n.inputs['Emission'].links[0]
							# mat.node_tree.links.remove(link)
					
					# Set new node - image texture
					tex_node = mat_nodes.new('ShaderNodeTexImage')
					# Set image
					tex_node.image = random_tex
					# Set new link
					#mat_links.new(tex_node.outputs['Color'], princip_node.inputs['Emission'])     
					mat_links.new(tex_node.outputs['Color'], princip_node.inputs['Base Color'])     

				o.select_set(False)
			elif o.name == 'f_avg.001': # if second hand
				o.pass_index = config.obj2id['hand']
			elif o.name != 'Camera' and o.name != 'Light': # if syn-object
				o.pass_index = config.obj2id[cur_obj_class]
			else:
				pass
		###

		location_xyz, pose_quaternion_wxyz = self.get_random_pose(True, config, cur_mask_bg, cur_depth_bg, cur_bg, normal_json)
		
		# Loop over meshes, set the 6D pose
		scene = bpy.context.scene
		for obj in scene.objects:
			obj.select_set(False)
			# if a mesh
			if obj.type == 'MESH':
				# Place object at location
				obj.location[0] = location_xyz[0] / 1000 
				obj.location[1] = location_xyz[1] / 1000 
				obj.location[2] = location_xyz[2] / 1000 

				obj.rotation_mode = 'QUATERNION'
				obj.rotation_quaternion[0] = pose_quaternion_wxyz[0]
				obj.rotation_quaternion[1] = pose_quaternion_wxyz[1]
				obj.rotation_quaternion[2] = pose_quaternion_wxyz[2]
				obj.rotation_quaternion[3] = pose_quaternion_wxyz[3]
					
				self.locationx = obj.location[0]
				self.locationy = obj.location[1]
				self.locationz = obj.location[2]
				
				self.rotationw = obj.rotation_quaternion[0]
				self.rotationx = obj.rotation_quaternion[1]
				self.rotationy = obj.rotation_quaternion[2]
				self.rotationz = obj.rotation_quaternion[3]

				#bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)

		# # Get location
		# x,y,z = self.get_location_on_table(config, cur_mask_bg, cur_depth_bg)
		# # Set location
		# if add_height:
		# 	# Get random height in mm
		# 	rand_height = float(np.random.randint(config.random_params["min_height"], config.random_params["max_height"]))
		# 	# init new height
		# 	heightened_y = -y + rand_height
		# 	# set final 3d coordinate
		# 	self.coord = x, z, heightened_y
		# # Just render object+hand on the table
		# else:
		# 	self.coord = x, z, -y


		# # Set some random variables
		# rand_hand_rot = math.radians(np.random.randint(-45,52))
		# x_rot = math.radians(random.uniform(-1 * config.random_params["x_rotation"], config.random_params["x_rotation"]))
		# y_rot = math.radians(random.uniform(-1 * config.random_params["y_rotation"], config.random_params["y_rotation"]))
		# z_rot = math.radians(np.random.randint(config.random_params["z_rotation"])) # for stem & non-stem

		# # Load x and y rotation, based on the table normal
		# xAngle, yAngle = utils_table.load_rotation_based_on_normal(normal_json, cur_bg)
		
		# # Loop over meshes
		# scene = bpy.context.scene
		# for obj in scene.objects:
		# 	obj.select_set(False)
		# 	# if a mesh
		# 	if obj.type == 'MESH':

		# 		# Place object at location
		# 		obj.location[0] = x / 1000 
		# 		obj.location[1] = z / 1000 
		# 		if add_height:
		# 			obj.location[2] = heightened_y / 1000
		# 		else:
		# 			obj.location[2] = -y / 1000 

		# 		# TODO: freely rotate about yaw axis, for stem and non-stem

		# 		if add_height:
		# 			# First rotation to rotation matrix
		# 			r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), rand_hand_rot], degrees=False)
		# 			rot_matrix1 = r1.as_matrix()
		# 			quat1 = r1.as_quat()
		# 			# Second rotation to rotation matrix
		# 			r2 = R.from_euler("YXZ", [y_rot, x_rot, 0], degrees=False)
		# 			rot_matrix2 = r2.as_matrix()
		# 			# Both
		# 			rot_matrix12 = rot_matrix1 @ rot_matrix2
		# 			# Convert to quaternion
		# 			r12 = R.from_matrix(rot_matrix12)
		# 			# X,Y,Z,W
		# 			quat12 = r12.as_quat()
		# 			obj.rotation_mode = 'QUATERNION'
		# 			obj.rotation_quaternion[0] = quat12[3]
		# 			obj.rotation_quaternion[1] = quat12[0]
		# 			obj.rotation_quaternion[2] = quat12[1]
		# 			obj.rotation_quaternion[3] = quat12[2]
				
		# 		else: # On the table
		# 			# First rotation to rotation matrix
		# 			r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), rand_hand_rot], degrees=False)
		# 			rot_matrix1 = r1.as_matrix()
		# 			quat1 = r1.as_quat()
		# 			obj.rotation_mode = 'QUATERNION'
		# 			obj.rotation_quaternion[0] = quat1[3]
		# 			obj.rotation_quaternion[1] = quat1[0]
		# 			obj.rotation_quaternion[2] = quat1[1]
		# 			obj.rotation_quaternion[3] = quat1[2]
				# else:
				# 	use_euler = False
				# 	# USING EULER
				# 	if use_euler:
				# 		# First, transformation is: 
				# 		obj.rotation_mode = 'ZXY' # means we should do first Y, then X, then Z
				# 		# First, yAngle
				# 		obj.rotation_euler[1] = yAngle
				# 		# Then, xAngle
				# 		obj.rotation_euler[0] = xAngle - math.radians(90)
				# 		# Then, z
				# 		obj.rotation_euler[2] = rand_hand_rot

				# 		# set
				# 		obj.select_set(True)
				# 		bpy.ops.object.transforms_to_deltas(mode='ROT') 
				# 		obj.select_set(False)
						
				# 		# Second transformation is: 
				# 		obj.rotation_mode = 'ZXY'
				# 		# First, Y
				# 		obj.rotation_euler[1] = y_rot
				# 		# Then, X
				# 		obj.rotation_euler[0] = x_rot
				# 		# Last, Z
				# 		obj.rotation_euler[2] = 0
				# 	else:


					
				# self.locationx = obj.location[0]
				# self.locationy = obj.location[1]
				# self.locationz = obj.location[2]
				
				# self.rotationw = obj.rotation_quaternion[0]
				# self.rotationx = obj.rotation_quaternion[1]
				# self.rotationy = obj.rotation_quaternion[2]
				# self.rotationz = obj.rotation_quaternion[3]

				#bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)
		
		hand_objects = []
		# Select object again
		scene = bpy.context.scene
		for ob in scene.objects:
			ob.select_set(False)
			if ob.type == 'MESH':
				if ob.name != "f_avg" or ob.name != "f_avg.001":
					bpy.context.view_layer.objects.active = ob
					obj = bpy.context.view_layer.objects.active
				if ob.name == "f_avg" or ob.name == "f_avg.001":
					print("ADDING:", ob.name)
					hand_objects.append(ob)
					ob.select_set(True)
					bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)
					ob.select_set(False)

		return hand_objects, [self.locationx, self.locationy, self.locationz], [self.rotationw, self.rotationx, self.rotationy, self.rotationz], flip_box_flag

	def align_forearm_with_pos_yaxis(self, draw=False):
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
				self.change_angle = -1 * angle  # In radians
				# Apply the changes
				ob.select_set(True)
				bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
				ob.select_set(False)

	def rotation_z_matrix(self, theta):
		rotation_matrix = [[np.cos(theta), -np.sin(theta),  0],
						   [np.sin(theta),  np.cos(theta),  0],
						   [0,                          0,  1]]
		return rotation_matrix

	def generate_nocs(self, N, cur_nocs_obj_path, texspace_size):
		"""Loads object with NOCS-map material and places it in the same location and rotation.
		"""

		# delete previous mesh
		utils_blender.clear_mesh()

		# import object
		bpy.ops.import_scene.gltf(filepath=cur_nocs_obj_path)

		# replace object with vertex object at same position
		# Select object
		scene = bpy.context.scene
		for ob in scene.objects:
			ob.select_set(False)
			if ob.type == 'MESH':
				bpy.context.view_layer.objects.active = ob
		obj = bpy.context.view_layer.objects.active

		# Load the texture space
		#texspace_size = np.loadtxt(self.cur_texspace_path)
		# Set the texture space size
		obj_mesh_name = obj.data.name
		obj.show_texture_space = True
		bpy.data.meshes[obj_mesh_name].use_auto_texspace = False
		bpy.data.meshes[obj_mesh_name].texspace_size = texspace_size, texspace_size, texspace_size
		
		# Remove other material
		obj.data.materials.clear()

		# Make a new material
		nocs_mat = bpy.data.materials.new('nocs_material')
		nocs_mat.use_nodes = True
		bpy.data.meshes[obj_mesh_name].materials.append(nocs_mat)
		
		# deactivate shadows
		nocs_mat.shadow_method = 'NONE'
		mat_nodes = nocs_mat.node_tree.nodes
		mat_links = nocs_mat.node_tree.links

		# Get default things in material
		for n in mat_nodes:
			if n.name == "Material Output":
				mat_output_node = n
			if n.name == "Principled BSDF":
				for link in n.inputs[0].links:
					nocs_mat.node_tree.links.remove(link)

		# Set texture node to create NOCS colors
		tex_node = mat_nodes.new('ShaderNodeTexCoord')
		# set new link - bypassing principle node
		mat_links.new(tex_node.outputs["Generated"], mat_output_node.inputs[0])        


		# TODO: combine change_angle with the location and quaternion

		# convert change_angle to rotation matrix
		rotation_sym_axis = self.rotation_z_matrix(self.change_angle); print(rotation_sym_axis)
		r_sym = R.from_matrix(rotation_sym_axis)
		r_sym = r_sym.as_matrix()
		print("rotation (sym) matrix", r_sym)

		# convert wxyz to rotation matrix
		quat_before = [self.rotationx, self.rotationy, self.rotationz, self.rotationw]; print("\nquat before:", quat_before)
		r_quat = R.from_quat([self.rotationx, self.rotationy, self.rotationz, self.rotationw]) # xyzw
		r_quat = r_quat.as_matrix()
		print("rotation (quat) matrix", r_quat)

		# combine both rotation matrices into one (note the order)
		r_combined = r_quat @ r_sym
		print("r_combined matrix", r_combined)

		# revert back to quaternion
		quat_combined = R.from_matrix(r_combined) #xyzw
		quat_combined = quat_combined.as_quat()
		print("quaternion combined (xyzw):", quat_combined, "\n\n")

		self.rotationw = quat_combined[3]
		self.rotationx = quat_combined[0]
		self.rotationy = quat_combined[1]
		self.rotationz = quat_combined[2]

		# ###################################### TA
		# # Apply the changes
		# for ob in bpy.data.objects:
		# 	if ob.type == 'MESH':
		# 		# Select object
		# 		ob.rotation_mode = 'XYZ'
		# 		ob.rotation_euler[2] = self.change_angle
		# 		# print("Change angle: ", self.change_angle)
		# 		#ob.select_set(True)
		# 		bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
		# 		#ob.select_set(False)
		# # if obj_class == "box":
		# # copy()
		# ########################################

		# set location
		obj.location[0] = self.locationx
		obj.location[1] = self.locationy
		obj.location[2] = self.locationz
		# set rotation
		obj.rotation_mode = 'QUATERNION' #'XYZ'
		obj.rotation_quaternion[0] = self.rotationw
		obj.rotation_quaternion[1] = self.rotationx
		obj.rotation_quaternion[2] = self.rotationy
		obj.rotation_quaternion[3] = self.rotationz
		print(self.locationx, self.locationy, self.locationz, self.rotationx, self.rotationy, self.rotationz)
		bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

		# go into material preview
		my_areas = bpy.context.workspace.screens[0].areas
		my_shading = 'MATERIAL'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'

		for area in my_areas:
			for space in area.spaces:
				if space.type == 'VIEW_3D':
					space.shading.type = my_shading

		# set dimensions and path of this scene
		sce = bpy.context.scene.name
		
		# Set NOCS node setup
		N.set_nocs_nodes()

		# Set unedited colors
		bpy.data.scenes[sce].view_settings.view_transform = "Standard" # Default is Filmic
		
		# Render NOCS
		bpy.data.scenes[sce].view_settings.view_transform = "Raw" # Default is Filmic
		bpy.data.scenes[sce].cycles.samples = 1
		bpy.data.scenes[sce].cycles.use_denoising = False
		bpy.ops.render.render(write_still=True)
		
		# Reverse settings back to standard
		bpy.data.scenes[sce].view_settings.view_transform = "Standard" # Default is Filmic
		bpy.data.scenes[sce].cycles.samples = 2048 # NOTE: can turn this down, or add time limit
		bpy.data.scenes[sce].cycles.use_denoising = True

		#"Current Frame, to update animation data from python frame_set() instead"
		current_frame = bpy.context.scene.frame_current
		# #"Set scene frame updating all objects immediately"
		bpy.context.scene.frame_set(current_frame + 1)

		# Set ORIGINAL node setup
		N.node_setting_init()
		bpy.data.scenes[sce].display_settings.display_device = "sRGB"

		bpy.data.scenes[sce].render.filepath = ""

		for block in bpy.data.images:
			bpy.data.images.remove(block)
		
		l = [self.locationx, self.locationy, self.locationz]
		p_q = [self.rotationw, self.rotationx, self.rotationy, self.rotationz]
		return l, p_q

