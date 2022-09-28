""" Configuration file to store setting parameters

# NOTE: 
To not print out blender stuff, only python prints, uncomment the following line:
sys.stdout = sys.stderr
# and run this command:
# blender --background --python run_render.py 1> nul

NOTE: Memory
Pipeline to fix objects:
  - put textures .jpg into folder where .obj and .mtl are (go into .mtl to find which textures are needed)
  - obj2gltf
  - open .gltf in blender, fix scale and centre
  - save .glb
  - put old .gltf in 'old' folder 
"""

# CORSMAL backgrounds
# camera_intrinsics1 = dict(
#     fx = 923,
#     fy = 923,
#     cx = 640,
#     cy = 360
# )

# Inside/Outside campus backgrounds
# Focal F in millimeters (mm) computation:
# F (mm) = F (pixels) *  ( Sensorwidth (mm) / Imagewidth (pixels) )
# Sensorwidth of Intel RealSense 435i is 3.855 (https://en.wikipedia.org/wiki/Intel_RealSense)
# F (mm) = 605 * (3.855 / 640) = 3.6441796875

random_params = dict(
    x_rotation = 45,    # degrees
    y_rotation = 45,    # degrees
    z_rotation = 360,   # degrees
    min_height = 100,   # millimeter
    max_height = 400,   # millimeter

)

camera_params = dict(
    fx = 605.408875, # pixels
    fy = 604.509033, # pixels
    cx = 320, #cx = 321.112396, # pixels
    cy = 240, #251.401978, # pixels
    focal_mm = 3.6441796875, # millimeters
    sensor_width = 3.855,    # millimeters
    sensor_height = 2.919    # millimeters
)

paths = dict(

    # update these to your folders
    # data = '/media/xavier/DATA/SOM_renderer_DATA',
    
    # objects = '/media/xavier/DATA/SOM_renderer_DATA/objects/centered',
    # objects_nocs = '/media/xavier/DATA/SOM_renderer_DATA/objects/nocs_y-up',
    # objects_json = '/media/xavier/DATA/SOM_renderer_DATA/objects/object_datastructure.json',
    # #scales = '/media/xavier/DATA/SOM_renderer_DATA/scales',
    # #texture_spaces = '/media/xavier/DATA/SOM_renderer_DATA/texture_spaces',
    # grasps = '/media/xavier/DATA/SOM_renderer_DATA/grasps/meshes',
    # textures = "/media/xavier/DATA/SOM_renderer_DATA/assets/bodywithands/train",
    # renders = "./renders",
    # backgrounds = "/media/xavier/DATA/SOM_renderer_DATA/backgrounds",
    # table_normals = "/media/xavier/DATA/SOM_renderer_DATA/backgrounds/normals.json", 
    # #shapenet_path = '/home/weber/Documents/QMUL/Project/data/models-for-blender/obj',

    objects = '',
    objects_nocs = '',
    objects_json = '',
    
    grasps = '',
    
    textures = '',
    
    renders = "./renders",
    
    backgrounds = '',
    table_normals = '', 
    
    rgb_dir = '',
    depth_dir = '',
    mask_dir = '',
    nocs_dir = '',
    info_dir = ''
)   

blender_param = dict(
    rotation_mode = "XYZ",
    film_transparent = True, # Boolean to set non-objects to transparent

    # Engine type
    engine_type = 'CYCLES',
    gpu = True,

    # Dimensions
    resolution_x = 640, #1280,
    resolution_y = 480, #720, 
    resolution_percentage = 100,

    #if you are using gpu render, recommand to set hilbert spiral to 256 or 512
    #default value for cpu render is fine
    hilbert_spiral = 512,

    depth_use_overwrite = True,
    depth_use_file_extension = True
)

obj2id = {
    "box" : 50,
    "nonstem" : 100,
    "stem" : 150,
    "hand" : 200
}

data_settings = dict(
    camera_views = ["c1", "c2", "c3"],
    object_categories = ["stem", "nonstem", "box"],
)

# import bpy
# import sys

# # Import additional libraries: link to existing files or go to (whereisblender) python executable: ./python3.7m -m pip install 'package'
# sys.path.append("/home/weber/.local/lib/python3.7/site-packages")
# #sys.path.append("/usr/local/lib/python3.6/dist-packages/")
# from PIL import Image
# import cv2
# import numpy as np
# import pandas as pd

# # RGB output
# rgb_output_settings = bpy.types.ImageFormatSettings
# rgb_output_settings.color_mode = "RGB"  # default is "BW"
# rgb_output_settings.compression = 0     # default is 15

# # DEPTH output
# depth_output_settings = bpy.types.ImageFormatSettings
# depth_output_settings.color_mode = "RGB"        # default is "BW"
# depth_output_settings.compression = 0           # default is 15
# depth_output_settings.color_depth = "16"        # default is 8
# depth_output_settings.file_format = "OPEN_EXR"  # default is "PNG"

# global_vars = dict(
#     im_count = 1,
#     cur_depth_bg = "",
#     cur_mask_bg = "",
#     cur_rgb_bg = "",
#     cur_nocs_obj_path = "",
#     cur_texspace_path = "",
#     cur_obj_class = "",
#     locationx = 0,
#     locationy = 0,
#     locationz = 0,
#     rotationx = 0,
#     rotationy = 0,
#     rotationz = 0,
#     coord = [0,0,0]
# )


