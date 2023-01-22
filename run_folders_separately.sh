#!/bin/bash

pwd

conda activate /mnt/c7dd8318-a1d3-4622-a5fb-3fc2d8819579/CORSMAL/envs/choc-render-env

for i in {1..5}
do
	echo "Starting $i"
	/home/weber/Downloads/blender-3.3.0-linux-x64/blender \
	 --background --python render_all.py -- \
	 /media/weber/Seagate\ Portable\ Drive/CHOC/data \
	 /media/weber/Seagate\ Portable\ Drive/CHOC/outputs \
	 $i
done
