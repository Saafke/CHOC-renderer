""" 
Configuration file to store setting parameters

# NOTE: Memory
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


random_params = dict(
    x_rotation = 45,    # degrees
    y_rotation = 45,    # degrees
    z_rotation = 360,   # degrees
    min_height = 100,   # millimeter
    max_height = 400,   # millimeter

)

# NOTE:
# This is how to compute focal length F in millimeters (mm): F (mm) = F (pixels) *  ( Sensorwidth (mm) / Imagewidth (pixels) )
# We know the Sensorwidth of Intel RealSense 435i is 3.855 (source: https://en.wikipedia.org/wiki/Intel_RealSense)
# Therefore: F (mm) = 605 * (3.855 / 640) = 3.6441796875
camera_params = dict(
    fx = 605.408875,         # pixels
    fy = 604.509033,         # pixels
    cx = 320,                # cx = 321.112396, # pixels
    cy = 240,                # cy = 251.401978, # pixels
    focal_mm = 3.6441796875, # millimeters
    sensor_width = 3.855,    # millimeters
    sensor_height = 2.919    # millimeters
)

paths = dict(

    objects = '',
    objects_nocs = '',
    objects_json = '',
    
    grasps = '',
    
    textures = '',
    
    renders = '',
    
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


