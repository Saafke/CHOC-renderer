import json

# Loop over grasp_datastructure
f = open('/media/xavier/DATA/SOM_renderer_DATA/grasps/grasp_datastructure.json')
data = json.load(f)

f = open('/media/xavier/DATA/SOM_renderer_DATA/objects/object_string2id.json')
mapping = json.load(f)

grasp_data = data['grasps']

for gd in grasp_data:

    # get object string
    object_string = gd['object_string']

    # get object id
    object_id = mapping[object_string]

    # Add object id to gd
    print(object_id)
    gd['object_id'] = object_id

# save new
new_filename = '/media/xavier/DATA/SOM_renderer_DATA/grasps/grasp_datastructure_new.json'
with open(new_filename, 'w') as f:
    json.dump(data, f, indent=4, sort_keys=True)