# Loop over object_datastructure.json
import json

# Opening JSON file
f = open('object_models/object_datastructure.json')
data = json.load(f)

object_data = data['objects']

mapping_dict_STRING2ID = {}
for o in object_data:
    ID = o['id']
    object_string = o['shapenet_name']
    print("ID:", ID, "STRING:", object_string)
    mapping_dict_STRING2ID[object_string] = ID

new_filename = 'object_models/object_string2id.json'
with open(new_filename, 'w') as f:
    json.dump(mapping_dict_STRING2ID, f, indent=4, sort_keys=True)
