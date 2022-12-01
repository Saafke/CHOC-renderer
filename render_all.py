"""Renders images w/ labels.

Written by Xavier Weber

Example run commands:
	$ blender --background --python render_all.py -- ./data
	$ blender --python render_all.py -- /media/xavier/DATA/SOM_renderer_DATA /media/xavier/DATA/SOM_renderer_DATA
"""
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

# NOTE: change this to your python directories
sys.path.append('/home/xavier/anaconda3/envs/choc-render-env/lib/python3.10/site-packages')
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
# Libraries that are in the python3.10 folder
import cv2
import config
from PIL import Image
from scipy.spatial.transform import Rotation as R

# My imports
import node
import utils_blender
import utils_cam_light
import utils_object
import utils_projection
import utils_table

# NOTE: To not print out blender stuff, only python prints, uncomment the following line:
#sys.stdout = sys.stderr
# and run this command:
# $ blender --background --python run_render.py 1> nul



class Render :

	def __init__(self, data_folder, render_out_folder):
		self.im_count = 1
		
		self.locationx, self.locationy, self.locationz = 0,0,0
		self.rotationx, self.rotationy, self.rotationz = 0,0,0
		self.coord = [0,0,0]

		self.cur_bg = ""
		self.cur_depth_bg = ""
		self.cur_mask_bg = ""
		self.cur_rgb_bg = ""
		
		self.cur_nocs_obj_path = ""
		self.cur_texspace_path = ""
		self.cur_obj_class = ""

		self.set_data_paths(data_folder, render_out_folder)

		with open(config.paths["table_normals"]) as f:
			self.normal_json = json.load(f)

	def correct_mask(self):

		# Load image
		seg_og = Image.open(os.path.join(syn_mask_folder, f"{self.im_count:06d}old.png"))
		data_og = np.asarray(seg_og)

		# -- Correct image 
		classId = obj2id[cur_obj_class]
		
		#Where True, yield x, otherwise yield y.
		mask = np.where(data_og!=0, classId, data_og) # replace segmentation mask with class id
		mask = np.where(mask==0, 255, mask) # set background to white

		# set unsigned integer 8-bit
		im = np.uint8(mask)

		# Save image
		cv2.imwrite(os.path.join(syn_mask_folder, f"{self.im_count:06d}.png"), im)

		# Delete old
		os.remove(os.path.join(syn_mask_folder, f"{self.im_count:06d}old.png"))

	def scene_setting_init(self, use_gpu):
		"""Initializes blender setting configurations."""
		sce = bpy.context.scene.name
		bpy.data.scenes[sce].render.engine = config.blender_param['engine_type']
		bpy.context.scene.render.film_transparent = True
		bpy.data.scenes[sce].cycles.film_transparent = config.blender_param['film_transparent']
		bpy.data.scenes[sce].render.use_overwrite = config.blender_param['depth_use_overwrite']

		# Render dimensions
		bpy.data.scenes[sce].render.resolution_x = config.blender_param['resolution_x']
		bpy.data.scenes[sce].render.resolution_y = config.blender_param['resolution_y']
		bpy.data.scenes[sce].render.resolution_percentage = config.blender_param['resolution_percentage']
		# Alpha threshold for enabling z-pass (depth) map for transparent objects
		bpy.data.scenes[sce].view_layers["ViewLayer"].pass_alpha_threshold = 0
		# Use Z-pass (depth)
		bpy.data.scenes[sce].view_layers["ViewLayer"].use_pass_z = True
		# Activate object index pass to create segmentation masks
		bpy.data.scenes[sce].view_layers["ViewLayer"].use_pass_object_index = True
		if use_gpu:
			prefs = bpy.context.preferences.addons['cycles'].preferences
			devices = prefs.get_devices()
			print(devices)
			#prefs.compute_device_type = 'CUDA'
			#devices[0][0].use = True
			bpy.data.scenes[sce].render.engine = 'CYCLES' #only cycles engine can use gpu
			bpy.data.scenes[sce].cycles.device = 'GPU'

			# To speed up the rendering, while keeping the realism
			bpy.data.scenes[sce].cycles.max_bounces = 6
			bpy.data.scenes[sce].cycles.tile_size = 65536 #(256*256)

		
		else:
			bpy.data.scenes[sce].render.engine = 'BLENDER_EEVEE'
			# bpy.data.scenes[sce].eevee.use_soft_shadows = False
			# bpy.data.scenes[sce].eevee.use_taa_reprojection = False
			# bpy.data.scenes[sce].eevee.use_volumetric_lights = False
			# bpy.data.scenes[sce].eevee.sss_jitter_threshold = 0
			# bpy.data.scenes[sce].grease_pencil_settings.antialias_threshold = 0

	def set_background(self, background_name):
		# get full image path to rgb and depth
		rgb_bg = os.path.join(DATA_FOLDER, 'backgrounds/rgb', background_name)
		depth_bg = os.path.join(DATA_FOLDER, 'backgrounds/depth', background_name)
		mask_bg = os.path.join(DATA_FOLDER, 'backgrounds/plane_seg', background_name)
		# set global current rgb, segmentation and depth backgrounds
		self.cur_bg = background_name
		self.cur_rgb_bg = rgb_bg
		self.cur_mask_bg = mask_bg
		self.cur_depth_bg = depth_bg
		# Load background image 
		image_node = bpy.context.scene.node_tree.nodes[4]
		image_node.image = bpy.data.images.load(rgb_bg)
		
	def render(self):
		"""Performs check and renders the scene"""
		sce = bpy.context.scene.name
		bpy.data.scenes[sce].view_settings.view_transform = "Standard" # Default is Filmic
		bpy.data.scenes[sce].cycles.samples = 2048# 4096/2 # NOTE: can turn this down, or add time limit
		bpy.data.scenes[sce].cycles.use_denoising = True
		bpy.data.scenes[sce].cycles.use_adaptive_sampling = True
		bpy.data.scenes[sce].cycles.pixel_filter_type = "BLACKMAN_HARRIS"
		bpy.data.scenes[sce].cycles.filter_width = 1.5
		bpy.data.scenes[sce].render.film_transparent = True

		# Checks to see if object is at correct position.
		scene = bpy.context.scene
		for ob in scene.objects:
			ob.select_set(False)
			print("object name:", ob.name)
			if ob.type == 'MESH' and ob.name != "Table Normal":
				print("checking")
				# print("Actual object location = {}, {}, {}".format(ob.location[0]*1000, ob.location[1]*1000, ob.location[2]*1000))
				# print("Preferred object location = {}".format(coord))
				# math.isclose(ob.location[0] * 1000, self.coord[0], abs_tol=10**-3)
				#assert math.isclose(ob.location[1] * 1000, self.coord[1], abs_tol=10**-3)
				#assert math.isclose(ob.location[2] * 1000, self.coord[2], abs_tol=10**-3)
				bpy.context.view_layer.objects.active = ob
		obj = bpy.context.view_layer.objects.active

		# Render the images
		bpy.ops.render.render(write_still=True)

	def correct_depth(self, combine=False):
		"""Takes the saved output from Blender (EXR), and converts to PNG.
		It then deletes the EXR image.
		Parameters
		----------
		combine : boolean
			Whether you want to combine the object's depth with the depth from the background image.
		"""

		cur_frame = bpy.context.scene.frame_current
		# Load original depth in mm
		depth_og = Image.open(self.cur_depth_bg)
		data_og = np.asarray(depth_og)
		# Load object depth in mm
		im = cv2.imread( os.path.join(config.paths['depth_dir'], f"{self.im_count:06d}.exr"), -1) #-1 unchanged, 0 grayscale
		
		# Set non-object to zeros
		im[im>5000] = 0
		# Remove infinite values
		im = np.where( np.isinf(im), 0, im )
		# Set format to unsigned 16-bit integers
		im = np.uint16(im)
		
		# Write new png JUST TO CHECK, REMOVE THIS LINE AFTER
		#cv2.imwrite("./new.png", im)

		if combine:
		# Combine object and background depth. Function: (Where True, yield x, otherwise yield y.)
			combined = np.where(im == 0, data_og, im)
			combined = np.uint16(combined)
			im = combined
		cv2.imwrite(os.path.join(config.paths['depth_dir'],f"{self.im_count:06d}.png"), im)
		# Remove .exr file
		os.remove(os.path.join(config.paths['depth_dir'], f"{self.im_count:06d}.exr"))

	def render_depth(self, N):
		
		N.set_depth_nodes()
		# Settings
		sce = bpy.context.scene.name
		bpy.data.scenes[sce].cycles.use_denoising = False
		bpy.data.scenes[sce].cycles.use_adaptive_sampling = False
		bpy.data.scenes[sce].cycles.samples = 1
		bpy.data.scenes[sce].cycles.pixel_filter_type = "GAUSSIAN"
		bpy.data.scenes[sce].cycles.filter_width = 0.01
		bpy.data.scenes[sce].render.film_transparent = False
		bpy.ops.render.render(write_still=True)

	def re_render_loop(self, subtype, subset):
		"""
		Loops over the saved images, and re-renders them.
		"""
		
		# Initialise the nodes setup
		N.node_setting_init()
		# Get background files
		background_folder = os.path.join(DATA_FOLDER, 'backgrounds', 'rgb')
		background_rgbs = os.listdir(background_folder)
		background_rgbs.sort()
		# objectINFO
		f = open(os.path.join(DATA_FOLDER, 'objects', 'object_datastructure.json'))
		object_info = json.load(f)
		f = open(os.path.join(DATA_FOLDER, 'objects', 'object_string2id.json'))
		object_string2id = json.load(f)
		object_folder = os.path.join(DATA_FOLDER, 'objects', 'centered')
		object_paths = os.listdir(object_folder)
		# Get grasp files
		grasp_folder = os.path.join(DATA_FOLDER, 'grasps', 'meshes')
		grasps = os.listdir(grasp_folder)
		grasps.sort()
		# GraspID 2 ObjectID mapping
		f = open(os.path.join(DATA_FOLDER, 'grasps', 'graspId_2_objectId.json'))
		graspID_to_objectID = json.load(f)
		# GraspINFO
		f = open(os.path.join(DATA_FOLDER, 'grasps', 'grasp_datastructure.json'))
		grasps_info = json.load(f)
	
		# Loop over the JSON files
		json_dir = os.path.join(RENDER_OUT_FOLDER, subtype, subset, 'info')
		json_files = os.listdir(json_dir)
		json_files.sort()
		for js in json_files:
			f = open(os.path.join(json_dir, js))
			image_info = json.load(f)

			# Extract the information about this image to re-render it
			bg = image_info['background_id']
			grasp_id = image_info['grasp_id']
			location_xyz = image_info['location_xyz']
			object_id = image_info['object_id']
			pose_quaternion_wxyz = image_info['pose_quaternion_wxyz']
			image_id = js[:-4]
			
			# Reset directory im count
			self.im_count = start_idx
			# Reset blender im count
			current_frame = bpy.context.scene.frame_current
			bpy.context.scene.frame_set(start_idx)

			# Clear scene of mesh and light objects
			utils_blender.clear_mesh()
			utils_blender.clear_lights()
			# Set background and corresponding lights
			self.set_background(bg)
			CL.set_psuedo_realistic_light_per_background(bg)

			# TODO: change both functions so that we can input the location and pose_quat
			if grasp_id == None:
				# place object on table
				location, pose_quat = O.place_object(
									model_path, 
									object_cat_idx, 
									self.cur_obj_class, 
									self.cur_depth_bg,
									self.cur_mask_bg,
									self.cur_bg,
									self.normal_json)
			else:
				# place object and hand
				hand_objects, location, pose_quat = O.place_object_and_hand(model_path, 
										grasp_path,
										object_cat_idx, 
										self.cur_obj_class, 
										self.cur_depth_bg,
										self.cur_mask_bg,
										self.cur_bg,
										self.normal_json,
										add_height=True)

			# Generate rgb, mask
			self.render()
			# Generate depth
			self.render_depth(N)
			# Remove .exr, save as png
			self.correct_depth()
			# # Generate NOCS
			O.generate_nocs(N, self.cur_nocs_obj_path, object_texspace_size)
			# Generate annotation file
			self.generate_annotation_for_current_generated_image(None, object_id, bg, pose_quat, location)
			# update counters
			self.im_count += 1
			counterrr += 1
			# progress print
			print("{}: {}/{}\n".format(subset, self.im_count, len(json_files)))

	def loop_for_without_grasp(self, N, O, CL, start_idx, stop_idx, subtype="no_hand"):
		"""
		The loop that renders the desired number of CHOC mixed-reality images.
		- Loop over each object 					48
		 - Loop over each background				30
		   - Sample poses  							6
		----------------------------------------------
		Total number of images 					 8,640 
		"""
		b_name = None
		loop_counter = 1
		# Reset directory im count
		self.im_count = start_idx
		# Reset blender im count
		current_frame = bpy.context.scene.frame_current
		bpy.context.scene.frame_set(start_idx)
		self.set_parent_paths(subtype=subtype)

		# Get background files
		background_folder = os.path.join(DATA_FOLDER, 'backgrounds', 'rgb')
		background_rgbs = os.listdir(background_folder)
		background_rgbs.sort()

		# objectINFO
		f = open(os.path.join(DATA_FOLDER, 'object_models', 'object_datastructure.json'))
		object_info = json.load(f)
		f = open(os.path.join(DATA_FOLDER, 'object_models', 'object_string2id.json'))
		object_string2id = json.load(f)
		object_folder = os.path.join(DATA_FOLDER, 'object_models', 'meshes')
		object_paths = os.listdir(object_folder)
		
		# Loop over the objects (48)
		for obj_path in object_paths:
			
			# Get corresponding info of this object by looking into the JSON
			object_string = obj_path[:-4]
			object_id = object_string2id[object_string]
			object_texspace_size = object_info['objects'][int(object_id)]['texture_space_variable']
			object_cat_idx = object_info['objects'][object_id]['category']
			object_cat_name = object_info['categories'][object_cat_idx]['name']
			self.cur_obj_class = object_cat_name

			# Loop over the backgrounds (30)
			for bg in background_rgbs:
			
				# Sample random poses above table (6)
				for i in range(0,6):
					

					# Stop running the program after 1000 images are generated
					print("loop_counter:", loop_counter)
					if loop_counter >= stop_idx:
						print("Reached the stop_idx, so stop.")
						exit()
					
					# Set the batchname folder
					if (self.im_count-1) % 1000 == 0:
						b_name = "b_{:06d}_{:06d}".format(self.im_count, (self.im_count+999))

					# Check if image is already generated
					def check_if_images_already_exists(im_count, b):
						
						# Check if all images exists already, otherwise return False
						for xxx in ["rgb", "depth", "nocs", "mask"]:
							path_to_check = os.path.join(config.paths['renders'], subtype, xxx, b, "{:06d}.png".format(im_count))
							if not os.path.exists(path_to_check):
								return False
						# Check if info file exists already, otherwise return False
						path_to_check = os.path.join(config.paths['renders'], subtype, 'info', b, "{:06d}.json".format(im_count))
						if not os.path.exists(path_to_check):
							return False
						return True

					# def check_if_image_already_exists(im_count, b):
					# 	path_to_check = os.path.join(config.paths['renders'], subtype, 'rgb', b, "{:06d}.png".format(im_count))
					# 	return os.path.exists(path_to_check)
					
					if check_if_images_already_exists(self.im_count, b_name):
						print(self.im_count, "already exists! moving on...")
						self.im_count += 1
					else:
						# # Change save folders based on current_image_count
						# if (self.im_count-1) % 1000 == 0:
						# 	batch_foldername = "b_{:06d}_{:06d}".format(self.im_count, (self.im_count+999))
						# 	self.set_batch_paths(subtype, batch_foldername)
						bpy.context.scene.frame_set(self.im_count)
						self.set_batch_paths(subtype, b_name)
						
						N.node_setting_init()
						# Clear scene of mesh and light objects
						utils_blender.clear_mesh()
						utils_blender.clear_lights()

						# Set background and corresponding lights
						self.set_background(bg)
						CL.set_psuedo_realistic_light_per_background(bg)

						# Get the object path
						print("obj_path:", obj_path)
						model_path = os.path.join(DATA_FOLDER, 'object_models', 'meshes', obj_path)
						self.cur_nocs_obj_path = os.path.join(DATA_FOLDER, 'objects', 'nocs_y-up', obj_path)

						location, pose_quat = O.place_object(model_path, 
															object_cat_idx, 
															self.cur_obj_class, 
															self.cur_depth_bg,
															self.cur_mask_bg,
															self.cur_bg,
															self.normal_json)
						# Generate rgb, mask
						self.render()
						# Generate depth
						self.render_depth(N)
						# Remove .exr, save as png
						self.correct_depth()
						# # Generate NOCS
						O.generate_nocs(N, self.cur_nocs_obj_path, object_texspace_size)
						# Generate annotation file
						self.generate_annotation_for_current_generated_image(None, object_id, bg, pose_quat, location, flip_box_flag=False)
						# update counters
						self.im_count += 1
						loop_counter += 1
						# progress print
						print("{}/{}\n".format(self.im_count, 8640))

	def loop_for_with_grasp(self, N, O, CL, start_idx, stop_idx, subtype="hand"):
		"""
		The loop that renders the desired number of CHOC mixed-reality images.
		- Loop over each grasps 					288
		 - Loop over each background				30
		  - Loop over 3 areas						3
		   - Sample poses  							5
		-----------------------------------------------
		Total number of images 					 129600 
		"""
		loop_counter = 1

		b_name = None
		b_name = "b_{:06d}_{:06d}".format(start_idx, (start_idx+999))
		self.set_parent_paths(subtype=subtype)
		self.set_batch_paths(subtype, b_name)

		# if half == 'first':
		# 	start_idx = 1
		# elif half == 'second':
		# 	start_idx = 64801 #86401 64800
		# 	b_name = "b_{:06d}_{:06d}".format(64001, (64001+999))
		# 	self.set_parent_paths(subtype=subtype)
		# 	self.set_batch_paths(subtype, b_name)
		# else:
		# 	raise Exception("wrong half")
		
		# Reset directory im count
		self.im_count = start_idx
		# Reset blender im count
		current_frame = bpy.context.scene.frame_current
		bpy.context.scene.frame_set(start_idx)
		self.set_parent_paths(subtype=subtype)

		# Get grasp files
		grasp_folder = os.path.join(DATA_FOLDER, 'grasps', 'meshes')
		grasps = os.listdir(grasp_folder)
		grasps.sort()
		# if half == 'first':
		# 	grasps = grasps[:144]
		# 	print(grasps, len(grasps))
		# elif half == 'second':
		# 	grasps = grasps[144:]
		# 	print(grasps, len(grasps))
		# else:
		# 	raise Exception("wrong half")
		#random.shuffle(grasps)

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

		# Loop over the grasps (and therefore also objects) (288)
		for g in grasps:
			
			# Get the grasp path and index
			grasp_path = os.path.join(DATA_FOLDER, 'grasps', 'meshes', g)
			if g == "0000.glb":
				graspIdx = 0
			else:
				graspIdx = g[:-4].lstrip("0")
				graspIdx = int(graspIdx)
			# Get corresponding info of this grasp by looking into the JSON
			object_string = grasps_info['grasps'][graspIdx]['object_string']
			object_cat_idx = grasps_info['grasps'][graspIdx]['object_category']
			object_id = grasps_info['grasps'][graspIdx]['object_id']
			object_cat_name = grasps_info['categories'][object_cat_idx]['name']
			object_texspace_size = object_info['objects'][int(object_id)]['texture_space_variable']
			self.cur_obj_class = object_cat_name
			#print(object_id, object_string, object_cat_idx, object_cat_name, object_texspace_size)

			# Loop over the backgrounds (30)
			for bg in background_rgbs:
			

				# Sample random poses above table (15)
				for i in range(0, 15):
					
					# Stop running the program after 1000 images are generated
					print("Loop counter:", loop_counter)
					if loop_counter >= stop_idx:
						print("Reached the stop_idx, so stop.")
						exit()
					
					if (self.im_count-1) % 1000 == 0:
						b_name = "b_{:06d}_{:06d}".format(self.im_count, (self.im_count+999))

					# Check if images is already generated
					def check_if_images_already_exists(im_count, b):
						
						# Check if all images exists already, otherwise return False
						for xxx in ["rgb", "depth", "nocs", "mask"]:
							path_to_check = os.path.join(config.paths['renders'], subtype, xxx, b, "{:06d}.png".format(im_count))
							if not os.path.exists(path_to_check):
								return False
						# Check if info file exists already, otherwise return False
						path_to_check = os.path.join(config.paths['renders'], subtype, 'info', b, "{:06d}.json".format(im_count))
						if not os.path.exists(path_to_check):
							return False
						return True
					# def check_if_image_already_exists(im_count, b):
					# 	print(config.paths['renders'], subtype, 'rgb', b, "{:06d}.png".format(im_count), 'HERE DARLING')
					# 	path_to_check = os.path.join(config.paths['renders'], subtype, 'rgb', b, "{:06d}.png".format(im_count))
					# 	print("path_to_check:", path_to_check)
					# 	return os.path.exists(path_to_check)
					
					if check_if_images_already_exists(self.im_count, b_name):
						print(self.im_count, "already exists! moving on...")
						self.im_count += 1
					else:
						# Change save folders based on current_image_count
						# if (self.im_count-1) % 1000 == 0:
						# 	batch_foldername = "b_{:06d}_{:06d}".format(self.im_count, (self.im_count+999))
						# 	self.set_batch_paths(subtype, batch_foldername)
						#batch_foldername = "b_{:06d}_{:06d}".format(self.im_count, (self.im_count+999))
						bpy.context.scene.frame_set(self.im_count)
						self.set_batch_paths(subtype, b_name)
						N.node_setting_init()

						# Clear scene of mesh and light objects
						utils_blender.clear_mesh()
						utils_blender.clear_lights()

						# Set background and corresponding lights
						self.set_background(bg)
						CL.set_psuedo_realistic_light_per_background(bg)

						# Get the object path
						model_string = graspID_to_objectID[str(graspIdx)]
						model_path = os.path.join(DATA_FOLDER, 'object_models', 'meshes', "{}.glb".format(model_string))
						print("model_path", model_path)
						self.cur_nocs_obj_path = os.path.join(DATA_FOLDER, 'object_models', 'meshes_nocs_texture', "{}.glb".format(model_string))

						# Load object and hand (checking for collisions)
						_, table_points = utils_table.load_real_table(self.cur_mask_bg, self.cur_depth_bg)
						hand_objects, location, pose_quat, flip_box_flag = O.place_object_and_hand(model_path, 
																grasp_path,
																object_cat_idx, 
																self.cur_obj_class, 
																self.cur_depth_bg,
																self.cur_mask_bg,
																self.cur_bg,
																self.normal_json,
																add_height=True)
						while(utils_table.objectsOverlap(table_points, hand_objects) == True):
							print("Collision so re-sampling object and hand.")
							utils_blender.clear_mesh()
							hand_objects, location, pose_quat, flip_box_flag = O.place_object_and_hand(model_path, 
																grasp_path, 
																object_cat_idx,
																self.cur_obj_class, 
																self.cur_depth_bg,
																self.cur_mask_bg,
																self.cur_bg,
																self.normal_json,
																add_height=True)
						# Generate rgb, mask
						self.render()
						# Generate depth
						self.render_depth(N)
						# Remove .exr, save as png
						self.correct_depth()
						# # Generate NOCS
						O.generate_nocs(N, self.cur_nocs_obj_path, object_texspace_size)
						# Generate annotation file
						self.generate_annotation_for_current_generated_image(graspIdx, object_id, bg, pose_quat, location, flip_box_flag)
						# progress print
						print("{}/{}\n".format(self.im_count, 129600))
						self.im_count += 1

						loop_counter += 1


	def generate_annotation_for_current_generated_image(self, graspID, objectID, backgroundID, pose, location, flip_box_flag):
		info_dict = {}
		info_dict['grasp_id'] = graspID
		info_dict['object_id'] = objectID
		info_dict['background_id'] = backgroundID
		info_dict['pose_quaternion_wxyz'] = pose
		info_dict['location_xyz'] = location
		info_dict['flip_box'] = flip_box_flag
		with open(os.path.join(config.paths['info_dir'], "{:06d}.json".format(self.im_count)), 'w') as f:
			json.dump(info_dict, f, indent=4, sort_keys=True)

	def set_data_paths(self, data_folder, render_output_folder):
		config.paths['renders'] = render_output_folder
		config.paths['objects'] = os.path.join(data_folder, 'object_models/meshes')
		config.paths['object_nocs'] = os.path.join(data_folder, 'object_models/meshes_nocs_texture')
		config.paths['objects_json'] = os.path.join(data_folder, 'object_models/object_datastructure.json')
		
		config.paths['grasps'] = os.path.join(data_folder, 'grasps/meshes')
		config.paths['textures'] = os.path.join(data_folder, 'bodywithands/train')
		config.paths['backgrounds'] = os.path.join(data_folder, 'backgrounds')
		config.paths['table_normals'] = os.path.join(data_folder, 'backgrounds/normals.json')

	def set_parent_paths(self, subtype):
		
		def create_dir(path):
			if not os.path.exists(path):
				os.mkdir(path)
		render_dir = config.paths['renders']
		create_dir(render_dir)
		create_dir(os.path.join(render_dir, subtype))

		# Create sub-directories to store all different render outputs
		rgb_dir = os.path.join(render_dir, subtype, 'rgb')
		depth_dir = os.path.join(render_dir, subtype, 'depth')
		mask_dir = os.path.join(render_dir, subtype, 'mask')
		nocs_dir = os.path.join(render_dir, subtype, 'nocs')
		info_dir = os.path.join(render_dir, subtype, 'info')
		# Create these directories
		create_dir(rgb_dir)
		create_dir(depth_dir)
		create_dir(mask_dir)
		create_dir(nocs_dir)
		create_dir(info_dir)
	
	def set_batch_paths(self, subtype, batch_foldername):
		
		def create_dir(path):
			if not os.path.exists(path):
				os.mkdir(path)
		render_dir = config.paths['renders']

		batch_rgb_dir = os.path.join(render_dir, subtype, 'rgb', batch_foldername)
		batch_depth_dir = os.path.join(render_dir, subtype, 'depth', batch_foldername)
		batch_mask_dir = os.path.join(render_dir, subtype, 'mask', batch_foldername)
		batch_nocs_dir = os.path.join(render_dir, subtype, 'nocs', batch_foldername)
		batch_info_dir = os.path.join(render_dir, subtype, 'info', batch_foldername)

		# Create these directories
		create_dir(batch_rgb_dir)
		create_dir(batch_depth_dir)
		create_dir(batch_mask_dir)
		create_dir(batch_nocs_dir)
		create_dir(batch_info_dir)

		# Update config paths
		config.paths['rgb_dir'] = batch_rgb_dir
		config.paths['depth_dir'] = batch_depth_dir
		config.paths['mask_dir'] = batch_mask_dir
		config.paths['nocs_dir'] = batch_nocs_dir
		config.paths['info_dir'] = batch_info_dir

# Read arguments after "--"
argv = sys.argv
argv = argv[argv.index("--") + 1:] 
if len(argv) < 2:
	raise Exception("Please specify the path to the dataset folder AND the path to the output folder")
DATA_FOLDER = argv[0]
RENDER_OUT_FOLDER = argv[1]
#half = argv[2] # either first or second (to split the rendering over 2 computers)

# Import classes
R = Render(DATA_FOLDER, RENDER_OUT_FOLDER) 
N = node.Nodes()
CL = utils_cam_light.CamLightUtils()
O = utils_object.ObjectUtils()


# Initialise the scene
R.scene_setting_init(config.blender_param['gpu'])
utils_blender.clear_mesh()   # remove the mesh
utils_blender.clear_lights() # remove the light
CL.camera_init()			 # setup our camera

# start clock
start = time.time()

# render
R.loop_for_with_grasp(N, O, CL, start_idx=1, stop_idx=5, subtype="hand")
R.loop_for_without_grasp(N, O, CL, start_idx=1, stop_idx=5, subtype="no_hand")

# end clock 
end = time.time()
print("elapsed time:", end - start)
print("Ran succesfully.")