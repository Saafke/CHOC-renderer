import bpy
import math
import config
import random
import json
import os

class CamLightUtils():

	# def __init__(self, config):
	# 	self.config = config

	def set_light_data_variables(self, obj, data):

		light_type = data['type']
		
		if light_type == 'POINT':
			obj.energy = data['power'][0]
			obj.shadow_soft_size = data['shadow_soft_size'][0]  # meters
		if light_type == 'SUN':	
			obj.energy = data['energy'][0]
			obj.angle = data['angle'][0]    			 	 # angular diameter of the sun as seen from Earth
		if light_type == 'AREA':
			obj.energy = data['energy'][0]
			obj.shape = data['shape'][0]			 	 # RECTANGLE, SQUARE, DISK, ELIPSE
			obj.size = data['size'][0]  				 # meter
			obj.size_y = data['size_y'][0] 				 # meter
			obj.cycles.is_portal = data['is_portal'][0]  # boolean
			obj.spread = data['spread'][0]  			 # degrees
		if light_type == 'SPOT':
			obj.energy = data['energy'][0]
			obj.shadow_soft_size = data['shadow_soft_size'][0] # meters
			obj.spot_size = data['spot_size'][0] 				# degrees (angle of the spotlight beam)
			obj.spot_blend = data['spot_blend'][0] 			# softeness of the spotlight edge
			obj.show_cone = data['show_cone'][0] 				# boolean
	
	def set_light_object_variables(self, obj, data):

		# Set information of the annotated light source
		obj.color[0] = data['colorR']
		obj.color[1] = data['colorG']
		obj.color[2] = data['colorB']
		obj.cycles.max_bounces = data['max_bounce']
		obj.cycles.cast_shadow = data['cast_shadow']
		obj.cycles.use_multiple_importance_sampling = data['use_multiple_importance_sampling']
		obj.cycles.is_caustics_light = data['is_caustics_light']
		# Light location
		obj.location[0] = data['location_x']
		obj.location[1] = data['location_y']
		obj.location[2] = data['location_z']
		# Light rotation
		obj.rotation_mode = "AXIS_ANGLE"
		obj.rotation_axis_angle[0] = data['rotation_w']
		obj.rotation_axis_angle[1] = data['rotation_x']
		obj.rotation_axis_angle[2] = data['rotation_y']
		obj.rotation_axis_angle[3] = data['rotation_z']
		# Light scale
		obj.scale[0] = data['scale_x']
		obj.scale[1] = data['scale_y']
		obj.scale[2] = data['scale_y']

	def set_psuedo_realistic_light_per_background(self, background):
		
		# Open the lights info JSON
		lights_json_path = os.path.join(config.paths["backgrounds"], "lights", "{}.json".format(background[:-4]))
		with open(lights_json_path) as f:
			lights_annotation = json.load(f)

		# Create the lights
		light_counter = 1
		for light_annot in lights_annotation:
			
			# Create light datablock
			light_data = bpy.data.lights.new(name="light_{}".format(light_counter), type=light_annot["type"])
			self.set_light_data_variables(light_data, light_annot)

			# Create new object, pass the light data 
			light_object = bpy.data.objects.new(name="my-light", object_data=light_data)
			self.set_light_object_variables(light_object, light_annot)

			# Link object to collection in context
			bpy.context.collection.objects.link(light_object)

			# Change light position
			light_object.location = (0, 0, 3)

			light_counter += 1

	def set_light(self):
		"""Sets the light in a scene
		
		SpotLight is a directional light source
		PointLIght is an omni-directional light source 
		"""

		# initialize the light source
		bpy.data.lights["Light"].type = "POINT"
		bpy.data.lights["Light"].energy = 1000
		bpy.data.lights["Light"].shadow_soft_size = 1

		# set random location
		bpy.data.objects["Light"].location[0] = float(random.randrange(-300, 300))/100
		bpy.data.objects["Light"].location[1] = float(random.randrange(-300, 300))/100
		bpy.data.objects["Light"].location[2] = float(random.randrange(50, 500))/100

	def camera_init(self):
		"""Initalizes the camera in the scene, with the Intel RealSense D435i parameters.
		"""
		# Initialize camera
		cam_obj = bpy.data.objects['Camera']
		cam_obj.rotation_mode = config.blender_param['rotation_mode']
		
		cam = bpy.data.cameras['Camera']
		cam.lens = config.camera_params["focal_mm"] # mm
		cam.sensor_width = config.camera_params["sensor_width"] # mm # 2.688 # mm
		cam.sensor_height = config.camera_params["sensor_height"] # mm # 1.792 # mm
		#cam.sensor_fit = "HORIZONTAL" # default is "AUTO"

		# Set its location
		cam_obj.location[0] = 0
		cam_obj.location[1] = 0
		cam_obj.location[2] = 0

		# Set its rotation
		cam_obj.rotation_euler[0] = math.radians(90)
		cam_obj.rotation_euler[1] = 0
		cam_obj.rotation_euler[2] = 0