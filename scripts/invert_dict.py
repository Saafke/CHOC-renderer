"""
delete this after
"""
import json

new_filename = '/media/xavier/DATA/SOM_renderer_DATA/grasps/graspId_2_objectId.json'

# Opening JSON file
f = open('/media/xavier/DATA/SOM_renderer_DATA/grasps/objectId_2_graspIds.json')
my_map = json.load(f)

new_dict = {}
for k, v in my_map.items():
    print("key:", k, "value:", v)

    for graspIdx in v:
        new_dict[graspIdx] = k

print(new_dict)
with open(new_filename, 'w') as f:
    json.dump(new_dict, f, indent=4, sort_keys=True)
