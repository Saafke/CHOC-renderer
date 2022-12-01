# Render CORSMAL Hand-Occluded Containers (CHOC) in Blender

This is the code to render CHOC mixed-reality composite images using Blender and Python.

[[dataset](https://zenodo.org/record/5085801#.Y3zGQ9LP2V4)]
[[webpage](https://corsmal.eecs.qmul.ac.uk/pose.html)]
[[arxiv pre-print](https://arxiv.org/abs/2211.10470)]

## Table of Contents

1. [Installation](#installation)
    1. [Requirements](#requirements)
    2. [Instructions](#instructions)
2. [Running demo](#demo)
3. [Training](#training)
4. [Known issues](#issues)
5. [Enquiries, Question and Comments](#enquiries-question-and-comments)
6. [Licence](#licence)

## Installation <a name="installation"></a>

### Requirements <a name="requirements"></a>

This code has been tested on an Ubuntu 18.04 machine with Blender 3.3.

1. Install Blender

Download it from here: https://download.blender.org/release/Blender3.3/

Then run:
```
tar xf blender-3.3.0-linux-x64.tar.xz
```

Open via:
```
cd blender-3.3.0-linux-x64.tar.xz
./blender
```

Or if you want to install the latest version using snap:
`sudo snap install blender --classic`

#### Dependencies 

<details>
<summary> Install dependencies (via conda)</summary>

<br>

Create a conda environment:

`conda create --name choc-render-env python=3.10`

`conda activate choc-render-env`

`pip install Pillow opencv-python scipy`

Since this is a snap application, we need to tell it where our python dependencies are installed. So, to figure out where your python conda packages are installed, you can run in a terminal:

`conda info`

Then in the second row you will see something like:

`active env location : /home/user/anaconda3/envs/choc-render-env`

So, our conda environment is at "/home/user/anaconda3/envs/choc-render-env". We then extend this path to get the full path to the python libraries "/home/user/anaconda3/envs/choc-render-env/lib/python3.10/site-packages"

We then give this path at the top of each script, so that it knows where to look for these dependencies:

`sys.path.append('/home/user/anaconda3/envs/choc-render-env/lib/python3.10/site-package')`
</details>


## Downloading data

#### Backgrounds

#### Objects

#### Textures (hand and arm)
We need to download the textures for the hands and forearms. Please request access at [this](https://www.di.ens.fr/willow/research/obman/data/requestaccess.php) link. Once given access, download bodyandhands.zip. Then, unzip the contents in /DATA/GRASPS/TEXTURES/.

## Running

#### Configuration

You can change the settings in the config.py file.

#### Example run commands:

```blender --python render_all.py <DATA_FOLDER>``` 

or

```blender --background --python render_all.py <DATA_FOLDER>```

## Labelling the surface in the scene

#### Annotate with 
`labelme`

#### Convert segmentation masks
`labelme_json_to_dataset file.json -o a_folder_name`

## Creating Grasps

<details>
<summary> Installing and using GraspIt!</summary>

<br>

1. Install ROS Melodic (or another version). 

http://wiki.ros.org/melodic/Installation/Ubuntu

2. Install GraspIt!

First follow: https://graspit-simulator.github.io/build/html/installation_linux.html

Then follow: https://github.com/graspit-simulator/graspit_interface

3. Install ManoGrasp

Follow the steps ‘Install’ and ‘Model’ in https://github.com/ikalevatykh/mano_grasp

4. Open GraspIt!

`roslaunch graspit_interface graspit_interface.launch`

5. Load Object (container) & Table

File > Import Object > Look for the .OFF files! (change XML to OFF in the drop-down, just above the ‘Open’ button). After you load an object, zoom out, so you can actually see it.

6. Load the ManoHand

File > Import Robot > ManoHand (there are three versions, not sure if there's a difference). I loaded ManoHand.xml

7. Use the GUI to make the grasp. 

When you loaded all objects, they might interpenetrate. You can turn OFF the Collision via: Element tab > Collision. Then before grasping, turn collision back ON.

8. Save the world as .xml file.
</details>

#### Converting from GraspIt! to Blender

1. use scripts/GraspIt_to_MANOparams.py to extract the MANO parameters from the GraspIt! world files (.xml).
2. use scripts/MANOparams_to_Mesh.py to create from the MANO parameters the hand+forearm meshes.

## Notes

#### Objects used in this dataset
- The objects in this dataset are all downloaded from ShapeNetSem.
- They are rescaled. See the dimensions of each object in our paper. 
- They are centered such that the origin of the objects is at height 0 of the object, and in the center for the other two dimensions. You can use center.py to do this automatically.
- For some objects, the textures don't show up in Blender. To fix this, take a look at this answer: https://blender.stackexchange.com/questions/89010/materials-not-applied-after-importing-obj-shapenet/188192#188192 

#### Grasps created in this dataset

- For instructions, see grasp_instructions.md in this repo.

