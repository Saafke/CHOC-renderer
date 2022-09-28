"""
Creates a JSON datastructure file for the grasps .glb files

# TYPE (bottom, natural, top)
# HAND (left, right)
# OBJECT-ID (<string>)
# OBJECT-STRING
# GRASP-ID
# OBJECT-CATEGORY
"""
import json
import os
import shutil
import random
from bs4 import BeautifulSoup

def id2objectIDstring(cat, grasp_string):
    print(grasp_string)
    if grasp_string[:4] == "left":
        grasp_string = "right" + grasp_string[4:]
    print(grasp_string)
    # Reading the data inside the xml
    # file to a variable under the name
    # data
    xml_path = os.path.join('/home/xavier/.graspit/worlds/', cat, "{}.xml".format(grasp_string))
    print(xml_path)
    
    with open(xml_path, 'r') as f:
        data = f.read()
    
    print(type(data))
    # Passing the stored data inside
    # the beautifulsoup parser, storing
    # the returned object
    Bs_data = BeautifulSoup(data, "xml")
    
    # Finding all instances of tag
    # `unique`
    b_unique = Bs_data.find_all('filename')
    
    temp1 = str(b_unique[0]); print("temp1:", temp1, type(temp1))
    result = temp1.split("/")[4].split(".")[0]
    print("objectID string:", result)
    return result

def buggy_id2objectIDstring(path="/home/xavier/Documents/ObjectPose/code-from-source/SOM_renderer/DATA/OBJECTS/centered",
                      cat=None,
                      id=1):
    # Get the objects from this category
    objects = os.listdir( os.path.join( path, cat))
    
    # BUG:
    #objects.sort()

    print(cat)
    print(objects)
    input("here")
    return objects[id-1]

grasps_folder = "DATA/NEW_GRASPS_FIXED"
data_structure = {}

objectID_to_graspIDs = {}

# Loop over the grasp .glb files
grasps = os.listdir(grasps_folder)
random.shuffle(grasps)

# Start the graspID counter
graspID = 0

# Init an array for the grasps
grasps_array = []


# Extract information from string
for grasp in grasps:
 

    # Extract info
    hand_side = grasp.split("_")[0]
    grasp_type = grasp.split("_")[2]
    category = grasp.split("_")[3]
    id_ = grasp.split("_")[-1][:-4].lstrip("0")
    
    object_string = id2objectIDstring(cat=category,grasp_string=grasp[:-4])
    #object_string = id2objectIDstring(cat=category,id=int(id_))[:-4]
    print(graspID, hand_side, grasp_type, category, id_, object_string)

    # Make info
    grasp_dict = {}
    grasp_dict["id"] = graspID
    grasp_dict["object_string"] = object_string
    grasp_dict["hand_side"] = 0 if hand_side == "right" else 1
    
    if grasp_type == "bottom":
        grasp_dict["grasp_type"] = 0
    elif grasp_type == "natural":
        grasp_dict["grasp_type"] = 1
    elif grasp_type == "top":
        grasp_dict["grasp_type"] = 2
    else:
        raise Exception

    if category == "box":
        grasp_dict["object_category"] = 0
    elif category == "nonstem":
        grasp_dict["object_category"] = 1
    elif category == "stem":
        grasp_dict["object_category"] = 2
    else:
        raise Exception

    # Save info
    grasps_array.append(grasp_dict)

    if object_string in objectID_to_graspIDs:
        objectID_to_graspIDs[object_string].append(graspID)
        print("Already some grasps here. After adding new one:", objectID_to_graspIDs[object_string])
    else:
        objectID_to_graspIDs[object_string] = [graspID]
        print("No grasps here. After adding one:", objectID_to_graspIDs[object_string])
    
    print("\n")

    new_filename = "{:04d}.glb".format(graspID)
    shutil.copy( os.path.join(grasps_folder, grasp), os.path.join("DATA/NEW_GRASPS_RENAMED", new_filename))
    graspID+=1


# GRASP TYPE
d1 = {}; d1["id"] = 0; d1["type"] = "bottom"
d2 = {}; d2["id"] = 1; d2["type"] = "natural"
d3 = {}; d3["id"] = 2; d3["type"] = "top"
data_structure["grasp_types"] = [d1,d2,d3]

# HAND SIDES
d1 = {}; d1["id"] = 0; d1["type"] = "right"
d2 = {}; d2["id"] = 1; d2["type"] = "left"
data_structure["hand_sides"] = [d1,d2]

# CATEGORY
d1 = {}; d1["id"] = 0; d1["name"] = "box"
d2 = {}; d2["id"] = 1; d2["name"] = "nonstem"
d3 = {}; d3["id"] = 2; d3["name"] = "stem"
data_structure["categories"] = [d1,d2,d3]

data_structure["grasps"] = grasps_array

with open(os.path.join('grasp_datastructure.json'), 'w') as f:
    json.dump(data_structure, f, indent=4, sort_keys=False)

with open(os.path.join('objectID_2_graspIDs.json'), 'w') as f:
    json.dump(objectID_to_graspIDs, f, indent=4, sort_keys=True)