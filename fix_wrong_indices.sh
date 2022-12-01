#!/bin/bash

# I made the 'second' dataset starting from 64800, while it should have been 64801.
# Let's fix that.

# DIR="/home/xavier/Desktop/test2"

# ACTUAL_DIR="/media/DATA/downloads/renders/hand/rgb/b_064001_065000"

# for f in /home/xavier/Desktop/test2/src/*.png
# do
 
# 	echo "File Old: $f"
# 	index=${f:31:6}
#     temp=$(expr $index + 1)
#     new_index=$(printf "%06d" $temp)
#     new_filename=${f:0:27}"dest/"$new_index".png"
#     #echo "New Number: $new_index"
#     echo "File New: $new_filename"
#     echo " "

#     #mv $f $new_filename
# done

# NOTE: do depth, nocs, rgb, info, mask

src_folder="/media/DATA/downloads/renders/hand/info"
dest_folder="/media/DATA/downloads/renders_correct_index/hand/info"

# Let's loop over all batch folders
for f in $src_folder"/"*
do
    #echo "$f"

    # Extract the batch filename
    batch_f=${f:40:16}
    #echo "$batch_f"

    # Make new folder in the dest
    cd $dest_folder
    pwd
    mkdir $batch_f

    # Let's loop over all images in this batch
    for i in $src_folder"/"$batch_f"/"*
    do
        #echo "$i"

        # Get current image index
        image_name=${i:56:6}
        #echo "Current image index: $image_name"
        
        # Create new image index
        temp=$(expr $image_name + 1)
        new_image_name=$(printf "%06d" $temp)
        #echo "New image index: $new_image_name | batch: $batch_f"
        
        # Make destination batch depend on image name
        noleadingzeros=$((10#$image_name))
        if [ $(expr $noleadingzeros % 1000) == "0" ]; then
            
            xx=$(expr $image_name + 1000)
            xx0=$(printf "%06d" $xx)
            new_batch_f="b_"$new_image_name"_"$xx0
            mkdir $new_batch_f
            # Put this one in the next batch
            old_image_filename=$src_folder"/"$batch_f"/"$image_name".json"
            new_image_filename=$dest_folder"/"$new_batch_f"/"$new_image_name".json"

            # echo "New batch: $new_batch_f"
            echo "File Old: $old_image_filename"
            echo "File New: $new_image_filename"
            echo " "

            #sleep 1m

            cp $old_image_filename $new_image_filename

        else
            # Current batch is fine
            old_image_filename=$src_folder"/"$batch_f"/"$image_name".json"
            new_image_filename=$dest_folder"/"$batch_f"/"$new_image_name".json"

            echo "File Old: $old_image_filename"
            echo "File New: $new_image_filename"
            echo " "

            cp $old_image_filename $new_image_filename

        fi
        
        #cp $old_image_filename $new_image_filename

    done

done

####### extra code
 #new_batch_folder=$dest_folder"/"$batch_f
    #echo "$new_batch_folder"