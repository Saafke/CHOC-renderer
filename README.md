# CHOC render blender

This is the code to render CORSMAL Hand-Occluded Containers (CHOC) mixed-reality composite images using Blender and Python.

<p float="left">
  <img src="/images/000692.png"/>
  <img src="/images/016165.png"/> 
  <img src="/images/016995.png"/>
</p>

[[dataset](https://zenodo.org/record/5085801#.Y3zGQ9LP2V4)]
[[webpage](https://corsmal.eecs.qmul.ac.uk/pose.html)]
[[arxiv pre-print](https://arxiv.org/abs/2211.10470)]

## Table of Contents

1. [Installation](#installation)
    1. [Requirements](#requirements)
    2. [Instructions](#instructions)
2. [Downloading data](#downloading-data)
3. [Running code](#run)
4. [Tooling](#tooling)
    1. [Labelling the surface in the scene](#labelling-the-surface-in-the-scene)
    2. [Generating grasps](#creating-grasps)
    3. [Creating NOCS textures](#creating-nocs-maps)
5. [Notes](#notes)
6. [Enquiries, Question and Comments](#enquiries-question-and-comments)
7. [Licence](#licence)

## Installation <a name="installation"></a>

### Requirements <a name="requirements"></a>

This code has been tested on an Ubuntu 18.04 machine with Blender 3.3.0, with the following dependencies.

Dependencies:
- Python 3.10
- Conda 4.13.0
- Pillow 9.3.0
- OpenCV 4.6.0
- SciPy 1.9.3

### Instructions

1. Install Blender

Download it from here: https://download.blender.org/release/Blender3.3/

Then run:
```
tar xf blender-3.3.0-linux-x64.tar.xz
```

To open Blender you can run the _blender_ file:
```
cd blender-3.3.0-linux-x64.tar.xz
./blender
```

Alternative: if you want to, you can install the latest version using snap:
`sudo snap install blender --classic` (Note: if you do this, this repository might not function properly anymore)


2. Install dependencies (via conda)

Create and activate a conda environment:

```
conda create --name choc-render-env python=3.10
conda activate choc-render-env
```

Install dependencies:
```
pip install Pillow opencv-python scipy
```

Because of the interaction between Blender and Python it is necessary to explicitly show Blender where our Python dependencies are installed. So, to figure out where your Python Conda packages are installed, you can run in a terminal:

```
conda info
```

Then in the second row you will see something like:

```
active env location : /home/user/anaconda3/envs/choc-render-env
```

So, our conda environment is at "/home/user/anaconda3/envs/choc-render-env". We then extend this path to get the full path to the python libraries "/home/user/anaconda3/envs/choc-render-env/lib/python3.10/site-packages"

Then give your path at the top of the _render\_all.py_ script, so that the script knows where to look for these dependencies:

`render_all.py (line 22)`
```diff
+ sys.path.append('/home/user/anaconda3/envs/choc-render-env/lib/python3.10/site-package')
```

## Downloading data <a name="downloading-data"></a>

Here we will explain how to download and unzip the necessary data to render CHOC images. The resulting file structure will look as follows:
```
CHOC-renderer
  |--data
  |   |--backgrounds
  |   |--object_models
  |   |--bodywithhands
  |   |--assets
  |   |--grasps
  | ...
```

First, in _CHOC-renderer_, make a local folder called _data_:
```
mkdir data
```

#### Backgrounds, objects and grasps

You can download _backgrounds.zip_ (8.3 MB), _object\_models.zip_ (14.6 MB) and grasps (1.3 GB) \[optional\] from the [CHOC dataset](https://zenodo.org/record/5085801#.Y4iEytLP2V4) on Zenodo. Unzip the files in _data_.

#### Textures (hand and arm)
We need to download the textures for the hands and forearms. Please request access [here](https://www.di.ens.fr/willow/research/obman/data/requestaccess.php) link. Once given access, download _bodyandhands.zip_ (267.2 MB). Then, unzip the contents (_bodywithhand_ and _assets_) in _data_.


## Running code <a name="run"></a>

Here we will explain how to run the code. For more information about how Blender works through the Python API, see [here](https://docs.blender.org/api/current/info_overview.html#:~:text=Python%20in%20Blender,Blender's%20internal%20tools%20as%20well.).

The general command to run the code is:
```
blender --python render_all.py -- <datafolder> <outputfolder>
```

Arguments (we need to give them in order after `--`):

1. path to the data folder
2. path to the output folder (where we will save the renders)

We can make an _outputs_ folder as follows:
```
mkdir outputs
```

#### Example run commands:

To run the code, with opening the Blender GUI:

```
blender-3.3.0-linux-x64.tar.xz/blender --python render_all.py -- ./data ./outputs
``` 

or to run the code, without opening the Blender GUI:

```
blender-3.3.0-linux-x64.tar.xz/blender --background --python render_all.py -- ./data ./outputs
```

#### Configuration

You can change the settings in the config.py file.


## Labelling the surface in the scene <a name="labelling-the-surface-in-the-scene"></a>

We used [labelme](https://github.com/wkentaro/labelme) to first manually segment the table. Then, we used a [3D plane segmentation algorithm](http://www.open3d.org/docs/latest/tutorial/Basic/pointcloud.html#Plane-segmentation) via Open3D, to compute the normal of the flat surface, and remove outlier points from the table.

#### Annotate using the GUI
```
labelme
```

#### Convert segmentation masks
```
labelme_json_to_dataset file.json -o a_folder_name
```

#### Plane segmentation

Have a look at:

```
scripts/compute_table_normals.py
```

## Creating Grasps <a name="creating-grasps"></a>

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

## Notes <a name="notes"></a>

#### Objects used in this dataset
- The objects in this dataset are all downloaded from [ShapeNetSem](https://shapenet.org/).
- They are rescaled. See the dimensions of each object in our [webpage](https://corsmal.eecs.qmul.ac.uk/pose.html). 
- They are centered such that the origin of the objects is at height 0 of the object, and in the center for the other two dimensions. You can use scripts/center.py to do this automatically.
- For the original object files, sometimes the textures don't show up in Blender. Therefore, we converted the files to .glb format (see: https://blender.stackexchange.com/questions/89010/materials-not-applied-after-importing-obj-shapenet/188192#188192)


## Enquiries, Question and Comments <a name="enquiries-question-and-comments"></a>

If you have any further enquiries, question, or comments, or you would like to file a bug report or a feature request, use the Github issue tracker. 

## Licence <a name="license"></a>

This work is licensed under the MIT License. To view a copy of this license, see [LICENSE](LICENSE).