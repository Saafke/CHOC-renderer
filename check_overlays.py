""" This script visualises the overlay of the RGB image with the rendered segmentation mask, depth map, NOCS map and affordance mask.  """
import argparse
import glob
import numpy as np
import cv2
import os


def retrieve_nocs_mask(nocs):
	nocs_mask = np.zeros([nocs.shape[0], nocs.shape[1]])
	nocs_mask_zeros = nocs != np.array([0, 0, 0])
	nocs_mask[nocs_mask_zeros[:, :, 0]] = 1
	nocs_mask[nocs_mask_zeros[:, :, 1]] = 1
	nocs_mask[nocs_mask_zeros[:, :, 2]] = 1
	return nocs_mask


def to_uint8(img):
	min_val = np.amin(img)
	max_val = np.amax(img)
	return (((255 - 0) / (max_val - min_val)) * (img.copy() - min_val)).astype(np.uint8)


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--rgb_dir', default="...", type=str,
						help='Data directory containing annotation')
	parser.add_argument('--nocs_dir', default="...", type=str,
						help='Directory containing the rendered segmentation mask, depth map, NOCS map and affordance mask')
	return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	path_to_rgb = args.rgb_dir
	path_to_nocs = args.nocs_dir

	visualise = True

	# Retrieve all folders
	folders = os.listdir(path_to_rgb)
	folders.sort()
	
	for idx, folder in enumerate(folders):
		nocs_list = glob.glob(os.path.join(path_to_nocs, folder, '*.png'))
		nocs_list.sort()
		if len(nocs_list) == 0:
			continue

		print("folder_idx", idx)
		if idx < 1:
			continue
		
		# Start from the generated affordance mask
		for i in range(0, len(nocs_list)):
			# Print image name
			print(os.path.basename(nocs_list[i]))

			# Read RGB and NOCS images
			image = cv2.imread(os.path.join(path_to_rgb, folder, os.path.basename(nocs_list[i])))
			nocs = cv2.imread(os.path.join(path_to_nocs, folder, os.path.basename(nocs_list[i])))
			# nocs_fixed = utils.fix_background_nocs(nocs)
			# nocs_mask = retrieve_nocs_mask(nocs_fixed)
			# mask = cv2.imread(os.path.join(path_to_masks, folder, os.path.basename(aff_mask_list[i])), cv2.IMREAD_GRAYSCALE)
			# depth = cv2.imread(os.path.join(path_to_depths, folder, os.path.basename(aff_mask_list[i])), cv2.IMREAD_ANYDEPTH)

			# Visualise overlay
			if visualise:
				image_vis = image.copy()

				# Segmentation mask
				# colormap = np.zeros_like(image_vis)
				# colormap[mask == 200] = np.array([0, 0, 255])
				# colormap[mask == 50] = np.array([0, 255, 0])
				# colormap[mask == 150] = np.array([0, 255, 0])
				# colormap[mask == 100] = np.array([0, 255, 0])
				# mask_vis = cv2.addWeighted(image.copy(), 0.5, colormap, 0.9, 0.0)

				# Depth map
				# depth_vis = cv2.applyColorMap(to_uint8(depth.copy()), cv2.COLORMAP_JET)
				# depth_vis = cv2.addWeighted(image.copy(), 1.0, depth_vis, 0.7, 0.0)

				# Affordance mask
				# colormap = np.zeros_like(image_vis)
				# colormap[aff_mask == 1] = np.array([0, 0, 255])
				# colormap[aff_mask == 2] = np.array([0, 255, 0])
				# colormap[aff_mask == 3] = np.array([255, 0, 0])
				# aff_vis = cv2.addWeighted(image.copy(), 0.5, colormap, 0.9, 0.0)

				# NOCS map
				nocs_vis = cv2.addWeighted(image.copy(), 0.5, nocs, 0.9, 0.0)

				# Horizontal stack of resized images
				dim = (int(image.shape[1] * 0.75), int(image.shape[0] * 0.75))
				cv2.imshow("Check annotation", np.hstack([cv2.resize(image_vis, dim, interpolation=cv2.INTER_AREA),
														  cv2.resize(nocs_vis, dim, interpolation=cv2.INTER_AREA)]))
				cv2.waitKey(0)