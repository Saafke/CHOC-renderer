import bpy, bmesh
from PIL import Image
import numpy as np
import config
import utils_projection
import utils_blender
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def load_real_table(mask, depth, load_table_scene=False):
    """
    Loads the table from the depth images into the scene.
    """
    # Load mask
    mask_im = Image.open(mask).convert('L') # Means only Luminance, i.e. grayscale
    mask_ar = np.array(mask_im) / 255.0

    # Load depth
    depth_im = Image.open(depth)
    #depth_ar = cv2.imread(self.cur_depth_bg, cv2.IMREAD_ANYDEPTH)
    depth_ar = np.asarray(depth_im)

    # Mask the depth
    K = utils_projection.intrinsics2K(config.camera_params["fx"], config.camera_params["fy"], 
                            config.camera_params["cx"], config.camera_params["cy"])
    depth_masked = mask_ar * depth_ar
    # Get the 3D pointcloud, with corresponding 2D pixel locations
    points2D, points3D = utils_projection.dep_2_cld(depth_masked, K)
    points2D = np.asarray(points2D) 
    points3D = np.asarray(points3D)

    # From -X-YZ to XZ-Y
    points3D = points3D[:,[0,2,1]] 
    points3D[:,0] *= -1

    # Create mesh object based on the arrays above
    if load_table_scene:
        mesh = bpy.data.meshes.new(name='created mesh')
        mesh.from_pydata(points3D, [], [])
        mesh.update()
        mesh.validate()

        # create the object with the mesh just created
        obj = bpy.data.objects.new('table (from realsense)', mesh)

        # add the Object to the scene
        bpy.context.scene.collection.objects.link(obj)
    else:
        obj = None

    return obj, points3D

def load_rotation_based_on_normal(normal_json, cur_bg, draw=False):
    """
    Computes the rotation of X and Y, based on the normal of the table.
    Inspiration: http://www.fundza.com/mel/axis_to_vector/index.html
        Due to different coordinate system: [theirs] -> [ours]
        xylength -> yzlength
        zAngle -> xAngle
        xAngle -> yAngle
        first xAngle, then zAngle -> first yAngle, then zAngle
    """
    
    # Load normal of TABLE
    table_normal = normal_json[cur_bg[:-4]]
    table_normal = [-table_normal[0], -table_normal[1], table_normal[2]] # (X,Y,Z)   -> (-X,-Y,Z)
    table_normal = [table_normal[0], table_normal[2], -table_normal[1]]  # (-X,-Y,Z) -> (-X,Z,Y)

    ### Draw LINE from object location to NORMAL direction
    if draw:
        start = [ (x/1000) , (z/1000), (-y/1000) ]
        end =  [ (x/1000)+table_normal[0], (z/1000)+table_normal[1], (-y/1000)+table_normal[2]]
        line_mesh = bpy.data.meshes.new(name='Normal Line Mesh')
        line_mesh.from_pydata([start,end], [[0,1]], [])
        line_mesh.update()
        line_mesh.validate()
        # create the object with the line_mesh just created
        line_obj = bpy.data.objects.new('Table Normal', line_mesh)
        # add the Object to the scene
        bpy.context.scene.collection.objects.link(line_obj)

    # My up-axis is Z
    xx = table_normal[0]
    yy = table_normal[1]
    zz = table_normal[2]

    # Check if normal is a unit vector
    assert math.isclose(np.linalg.norm(table_normal), 1.0, abs_tol=10**-3) 

    # Angles are returned in RADIANS
    yzLength = math.sqrt(yy*yy + zz*zz)
    xAngle = math.acos(yy / yzLength)
    vecLength = 1
    yAngle = math.acos(yzLength / vecLength)

    print("xAngle:", math.degrees(xAngle), "yAngle:", math.degrees(yAngle))
    return xAngle, yAngle

def objectsOverlap(table_points, hand_objects):
    def collision(points, bm):
        rpoints = []
        addp = rpoints.append
        bvh = BVHTree.FromBMesh(bm, epsilon=0.0001)
        # return points on polygons
        for point in points:
            fco, normal, _, _ = bvh.find_nearest(point)
            if np.linalg.norm( np.asarray(fco) - np.asarray(point) ) < (1/1000): # 1mm
                return True
        return False
    
    """Check overlap between table points and hand(s)"""
    collision_flag = False
    for hand_object in hand_objects:
        scene = bpy.context.scene
        for ob in scene.objects:
            ob.select_set(False)
            if ob.type == 'MESH':
                if ob.name == hand_object.name:
                    ob.select_set(True)
                    bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(hand_object.data)
        collision_flag = collision(table_points, bm)
        bpy.ops.object.mode_set(mode="OBJECT")
        utils_blender.deselect(scene)
    return collision_flag