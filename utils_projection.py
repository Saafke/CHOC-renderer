import numpy as np

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

	# print("X: min,max |", np.min(pt0), np.max(pt0))
	# print("Y: min,max |", np.min(pt1), np.max(pt1))
	# print("Z: min,max |", np.min(pt2), np.max(pt2))

	return choose2D, cld