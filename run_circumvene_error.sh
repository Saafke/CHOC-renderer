#!/bin/bash

# Activate conda
conda activate som-env

# Run Blender

for i in {1..64}
do
   echo "Bash loop number: $i"
   blender --python render_all.py \
        -- /mnt/storage/Xavier/data/SOM_renderer_DATA \
        /mnt/storage/Xavier/data/SOM_renderer_DATA/renders second
done

# blender --python render_all.py \
#         -- /mnt/storage/Xavier/data/SOM_renderer_DATA \
#         /mnt/storage/Xavier/data/SOM_renderer_DATA/renders second