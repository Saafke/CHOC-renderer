"""
We will compute the average normal of the tables in the BACKGROUNDS.

NOTE - issues:
- a background image can have more than one table. How to compute the normal of each plane?
	- [X] Let open3d find each separate plane. SEEMS TO WORK
	- [X] Let's draw the normal based on the plane.
	- [ ] Fix the labelme mask, so that each table has it's own mask + ID. Because of two reasons:
			1. Each plane needs to get segmented.
			2. Each plane might have a different normal.
"""
import os
import cv2
import open3d as o3d
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--vis', action='store_true')
args = parser.parse_args()

############################################################################
# FROM: https://stackoverflow.com/questions/59026581/create-arrows-in-open3d
def draw_geometries(pcds):
    """
    Draw Geometries
    Args:
        - pcds (): [pcd1,pcd2,...]
    """
    o3d.visualization.draw_geometries(pcds)
def get_o3d_FOR(origin=[0, 0, 0],size=10):
    """ 
    Create a FrameOfReference that can be added to the open3d point cloud
    """
    mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=size)
    mesh_frame.translate(origin)
    return(mesh_frame)
def vector_magnitude(vec):
    """
    Calculates a vector's magnitude.
    Args:
        - vec (): 
    """
    magnitude = np.sqrt(np.sum(vec**2))
    return(magnitude)
def calculate_zy_rotation_for_arrow(vec):
    """
    Calculates the rotations required to go from the vector vec to the 
    z axis vector of the original FOR. The first rotation that is 
    calculated is over the z axis. This will leave the vector vec on the
    XZ plane. Then, the rotation over the y axis. 

    Returns the angles of rotation over axis z and y required to
    get the vector vec into the same orientation as axis z
    of the original Frame Of Referene (FOR)
				 	-----------------

    Args:
        - vec (): 
    """
    # Rotation over z axis of the FOR
    gamma = np.arctan(vec[1]/vec[0]) # compute angle 
    Rz = np.array([[np.cos(gamma),-np.sin(gamma),0],
                   [np.sin(gamma),np.cos(gamma),0],
                   [0,0,1]])
    # Rotate vec to calculate next rotation
    vec = Rz.T@vec.reshape(-1,1)
    vec = vec.reshape(-1)
    # Rotation over y axis of the FOR
    beta = np.arctan(vec[0]/vec[2])
    Ry = np.array([[np.cos(beta),0,np.sin(beta)],
                   [0,1,0],
                   [-np.sin(beta),0,np.cos(beta)]])
    return(Rz, Ry)
def create_arrow(scale=10):
    """
    Create an arrow in for Open3D
    """
    cone_height = scale*0.2
    cylinder_height = scale*0.8
    cone_radius = scale/10
    cylinder_radius = scale/20
    mesh_frame = o3d.geometry.TriangleMesh.create_arrow(cone_radius=cone_radius,
        cone_height=cone_height,
        cylinder_radius=cylinder_radius,
        cylinder_height=cylinder_height)
    return(mesh_frame)
def get_arrow(origin=[0, 0, 0], end=None, vec=None):
    """
    Creates an arrow from an origin point to an end point,
    or create an arrow from a vector vec starting from origin.
    Args:
        - end (): End point. [x,y,z]
        - vec (): Vector. [i,j,k]
    """
    scale = 0.1
    Ry = Rz = np.eye(3)
    T = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    T[:3, -1] = origin
    if end is not None:
        vec = np.array(end) - np.array(origin)
    elif vec is not None:
        vec = np.array(vec)
    if end is not None or vec is not None:
        scale = vector_magnitude(vec)
        Rz, Ry = calculate_zy_rotation_for_arrow(vec)
    mesh = create_arrow(scale)
    # Create the arrow
    mesh.rotate(Ry, center=np.array([0, 0, 0]))
    mesh.rotate(Rz, center=np.array([0, 0, 0]))
    mesh.translate(origin)
    return(mesh)
###############################################################

def plane_segmentation(pcd, vis=True):

	plane_model, inliers = pcd.segment_plane(distance_threshold=0.01,
                                         ransac_n=3,
                                         num_iterations=1000)
	[a, b, c, d] = plane_model

	print(f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")

	inlier_cloud = pcd.select_by_index(inliers)
	outlier_cloud = pcd.select_by_index(inliers, invert=True)

	if vis:
		# Color points
		inlier_cloud.paint_uniform_color([0.2, 1.0, 0.2])
		outlier_cloud.paint_uniform_color([1, 0, 0])

		# Draw normal of the plane
		average_inlier = np.average(np.asarray(inlier_cloud.points), axis=0)
		#print("average inlier point:", average_inlier)
		#print("inlier points shape:", np.asarray(inlier_cloud.points).shape)
		magnitude = -1
		end_point = average_inlier + [magnitude*a, magnitude*b, magnitude*c]
		print("Arrow | origin: {}, end: {}".format(average_inlier, end_point))

		arrow = get_arrow(origin=average_inlier, end=end_point)
		arrow.paint_uniform_color([0.2, 0.2, 1])
		o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud, arrow])

	return a,b,c,d, inliers, inlier_cloud, outlier_cloud

def intrinsics2K(fx, fy, cx, cy):
	return np.array([   [fx,  0.0, cx],
						[0.0, fy,  cy],
						[0.0, 0.0, 0.0] ])

def dep_2_cld(dpt, K, scale=1000):
	"""
	Converts a depth image into a pointcloud, using the camera intrinsics.

	Arguments
	---------
	dpt : single-channel image
		depth image
	K : array (3x3)
		intrinsics matrix
	"""

	xmap = np.array([[j for i in range(640)] for j in range(480)])
	ymap = np.array([[i for i in range(640)] for j in range(480)])

	if len(dpt.shape) > 2:
		dpt = dpt[:, :, 0]
	msk_dp = dpt > 1e-6

	choose = msk_dp.flatten().nonzero()[0].astype(np.uint32)
	choose2D = np.transpose(msk_dp.nonzero()) # for the 2d locations

	dpt_mskd = dpt.flatten()[choose][:, np.newaxis].astype(np.float32)
	xmap_mskd = xmap.flatten()[choose][:, np.newaxis].astype(np.float32)
	ymap_mskd = ymap.flatten()[choose][:, np.newaxis].astype(np.float32)

	pt2 = dpt_mskd / scale
	cam_cx, cam_cy = K[0][2], K[1][2]
	cam_fx, cam_fy = K[0][0], K[1][1]
	pt0 = (ymap_mskd - cam_cx) * pt2 / cam_fx
	pt1 = (xmap_mskd - cam_cy) * pt2 / cam_fy
	cld = np.concatenate((-pt0, -pt1, pt2), axis=1)

	return choose2D, cld

def display_inlier_outlier(cloud, ind):
    inlier_cloud = cloud.select_by_index(ind)
    outlier_cloud = cloud.select_by_index(ind, invert=True)

    print("Showing outliers (red) and inliers (gray): ")
    outlier_cloud.paint_uniform_color([1, 0, 0])
    inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])

camera_intrinsics = dict(
	fx = 605.408875,
	fy = 604.509033,
	cx = 321.112396,
	cy = 251.401978
)

background_path = "/home/xavier/Desktop/new_background/mask"
background_mask_paths = os.listdir("/home/xavier/Desktop/new_background/mask/manual")

origin_axes = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=[0, 0, 0])

# Init dictionary to store the plane normals
normal_dict = {}

# Loop over the BACKGROUND masks
for bg_path in background_mask_paths:

	# read mask image
	print(os.path.join(background_path, bg_path))
	m_im = cv2.imread(os.path.join(background_path, "manual", bg_path))
	m_im = m_im.astype(bool)[:,:,2]
	print(np.unique(m_im))
	print(m_im.shape, "m_im")
		
	# read depth image
	d_im = cv2.imread(os.path.join("/home/xavier/Desktop/new_background/depth", bg_path), cv2.IMREAD_ANYDEPTH)
	print(d_im.shape)

	r_im = cv2.imread(os.path.join("/home/xavier/Desktop/new_background/rgb", bg_path))[:,:,::-1]

	# get all depth points inside mask
	K = intrinsics2K( camera_intrinsics["fx"], camera_intrinsics["fy"], camera_intrinsics["cx"], camera_intrinsics["cy"])
	depth_masked = m_im * d_im
	print("depth_masked:", depth_masked.shape)

	# Get the 3D pointcloud, with corresponding 2D pixel locations
	points2D, points3D = dep_2_cld(depth_masked, K)
	points2D = np.asarray(points2D) 
	points3D = np.asarray(points3D) 

	print("points2D:", points2D.shape)
	pointsRGB = np.asarray(r_im[points2D[:,0],points2D[:,1],:]) / 255.0
	print("pointsRGB:", pointsRGB.shape)
	print("pointsRGB:", pointsRGB)
	print("points3D:", points3D.shape)

	# Convert to Open3D format
	pcl = o3d.geometry.PointCloud()
	pcl.points = o3d.utility.Vector3dVector(points3D)
	pcl.colors = o3d.utility.Vector3dVector(pointsRGB)
	o3d.visualization.draw_geometries([pcl])
	a,b,c,d, inlier_indices, inlier_points, outlier_points = plane_segmentation(pcl, vis=args.vis)

	# These are the INLIERS of the POINTCLOUD
	print("inlier_indices:", inlier_indices)

	# Find the 2D image locations of these inlier points
	print("points2D.shape before:", points2D.shape)
	points2D_inliers = points2D[inlier_indices]
	print("points2D.shape before:", points2D_inliers.shape)

	# Mask these points
	new_mask = np.zeros((480,640))
	new_mask[points2D_inliers[:,0],points2D_inliers[:,1]] = 255

	print(background_path)
	print(bg_path)
	new_mask_filename = os.path.join(background_path, "plane_segmented", bg_path)
	print("new mask filename:", new_mask_filename)
	cv2.imwrite(new_mask_filename, new_mask)
	
	normal_dict[bg_path[:-4]] = [a,b,c]

# Save the dictionary containing the plane normal of each table to a JSON file
output_filename = os.path.join(background_path, "plane_segmented", "normals.json")
with open(output_filename, 'w') as fp:
    json.dump(normal_dict, fp, sort_keys=True, indent=4)
