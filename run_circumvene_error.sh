#!/bin/bash

# Activate conda
conda activate som-env

# Run Blender

for i in {1..7}
do
   echo "Bash loop number: $i"
   blender --python render_all.py \
        -- /media/DATA/SOM_renderer_DATA \
        /media/DATA/downloads/renders second
done

# blender --python render_all.py \
#         -- /mnt/storage/Xavier/data/SOM_renderer_DATA \
#         /mnt/storage/Xavier/data/SOM_renderer_DATA/renders second
