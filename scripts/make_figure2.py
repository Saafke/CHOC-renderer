"""
Let's loop over the dataset, and gather crops around the object.


We want: for each grasp_type, each hand_side, 6 different objects.
 - Each object has all 6 grasps.


All objects. Different backgrounds. 

$ python make_figure2.py --som_dir /media/DATA/SOM_NOCS_DATA/som
"""
import argparse
import os
import json
import cv2
import numpy as np
import random

parser = argparse.ArgumentParser()
parser.add_argument('--som_dir', type=str, default="Path to the SOM directory.")
args = parser.parse_args()

def get_square_crop_with_margin(x1,y1,x2,y2):
    """
    Inputs are coordinates for a tight rectangular crop.
    Let's make a square crop.
    """
    
    w = y2-y1
    h = x2-x1
    cx = x1+int(w/2) #centre X
    cy = y1+int(h/2) #centre Y

    # Get the biggest, height or width
    s = w
    if h > w:
        s = h
    
    # square size
    s = s+30
    if s % 2 != 0:
        s += 1

    x1 = cx - (s/2)
    x2 = cx + (s/2)
    y1 = cy - (s/2)
    y2 = cy + (s/2)
    
    print("x1,y1, x2,y2", x1,y1, x2,y2)
    return int(x1),int(y1), int(x2),int(y2)

def get_binary_object_mask(raw_mask):
    """
    """
    mask = raw_mask.copy()

    # Remove hand
    if np.unique(mask)[-1] == 200:
        mask[mask == 200] = 0
    if np.unique(mask)[-1] != 0 and np.unique(mask)[-1] != 200:
        objId = np.unique(mask)[-1]
        mask[mask==objId] = 1
    
    assert len(np.unique(mask)) == 2

    return mask

def get_bbox_around_object(mask_binary):
    """
    return x1,y1 (top left) x2,y2 (bottom right)
    """
    m = mask_binary.copy()

    horizontal_indicies = np.where(np.any(m, axis=0))[0]
    print("np.any(m, axis=0)",np.any(m, axis=0))
    print("p.where(np.any(m, axis=0))",np.where(np.any(m, axis=0)))
    vertical_indicies = np.where(np.any(m, axis=1))[0]

    if horizontal_indicies.shape[0]:

        x1, x2 = horizontal_indicies[[0, -1]]
        y1, y2 = vertical_indicies[[0, -1]]
        # x2 and y2 should not be part of the box. Increment by 1.
        x2 += 1
        y2 += 1
    else:
        # No mask for this instance. Might happen due to
        # resizing or cropping. Set bbox to zeros
        x1, x2, y1, y2 = 0, 0, 0, 0
            
    return x1,y1, x2,y2

def image_index_to_batch_folder(image_index):

	# remove leading zeros
	string = str(image_index).lstrip("0")
	x = int(string)

	if ((x % 1000) == 0):
		# get batch1 and batch2 
		b1 = x-999
		b2 = x
		foldername = "b_{:06d}_{:06d}".format(b1,b2)
	else:
		y = x - (x % 1000)
		# get batch1 and batch2 
		b1 = y+1
		b2 = y+1000
		foldername = "b_{:06d}_{:06d}".format(b1,b2)
	return foldername

grasp_type_names = ["bottom", "natural", "top"]
hand_side_names = ["right", "left"]

grasp_types = [0,1,2] #["bottom", "natural", "left"]
hand_sides = [0,1] #["right", "left"]

# Get info dicts
grasps_info_path = os.path.join(args.som_dir, "grasp_datastructure.json")
f = open(grasps_info_path)
grasps_info = json.load(f)


# Get all batches
batch_folders = os.listdir( os.path.join(args.som_dir, "all", "rgb"))
batch_folders.sort()

objects_already_used = []

# Loop over the hand_sides
for h in hand_sides:

    # Loop over the grasp types
    for g in grasp_types:

        found = 0

        # Loop over all images - could randomize this
        indices = list(range(1,138241))
        random.shuffle(indices)

        for i in indices:
            
            print("i:", i, end="\r")

            index_str = "{:06d}".format(i)

            # Load info
            img_path = os.path.join(args.som_dir, "all", "info", image_index_to_batch_folder(index_str), "{}.json".format(index_str))
            f = open(img_path)
            img_info = json.load(f)

            # Get IDs
            graspID = img_info["grasp_id"]
            objectID = img_info["object_id"]

            if graspID != None:
                
                # Get information about this specific graspID
                img_hand_side = grasps_info["grasps"][graspID]["hand_side"]
                img_grasp_type = grasps_info["grasps"][graspID]["grasp_type"]

                # Find any image with this grasp. Don't pick if already used this object.
                if (img_hand_side == h) and (img_grasp_type == g) and (objectID not in objects_already_used):
                    print("image:", index_str, "objID:", objectID, "hand:", h, "grasp:", g)

                    # Add object to already used
                    objects_already_used.append(objectID)

                    ### TODO - crop around RGB
                    
                    # # Load RGB 
                    rgb_path = os.path.join(args.som_dir, "all", "rgb", image_index_to_batch_folder(index_str), "{}.png".format(index_str))
                    rgb = cv2.imread(rgb_path)[:,:,::-1] # bgr to rgb

                    # Save this image
                    output_filename = os.path.join("/home/xavier/Desktop/Fig-2", "{}_{}".format(hand_side_names[h], grasp_type_names[g]), "{}.png".format(index_str))
                    print("outptu:", output_filename)
                    cv2.imwrite(output_filename, rgb[:,:,::-1])
                    
                    found += 1
                    if found == 6:
                        break
                    # # Load mask, only the object
                    # mask_path = os.path.join(args.som_dir, "all", "mask", image_index_to_batch_folder(index_str), "{}.png".format(index_str))
                    # raw_mask = cv2.imread(mask_path)[:,:,2] # get single channel
                    # # Remove hand and make binary
                    # mask_object_binary = get_binary_object_mask(raw_mask)

                    # # Get bounding box around mask, and the centre
                    # x1,y1, x2,y2 = get_bbox_around_object(mask_object_binary)

                    # # Get rectangular crop with margin
                    # x1,y1, x2,y2 = get_square_crop_with_margin(x1,y1,x2,y2)

                    # # Crop a rectangle, so size (X,X)
                    # crop = rgb[y1:y2, x1:x2]

                    # # 
                    # cv2.imshow("croppy", crop[:,:,::-1])
                    # cv2.waitKey(0) 
                    # cv2.destroyAllWindows()

                    #input("found, Enter.. for next")





