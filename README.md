# CHOC renderer

Official software to automatically render composite images of handheld containers (synthetic objects, hands and forearms) over real backgrounds 
using Blender and Python. The software was used to generate the mixed-reality set of the CORSMAL Hand-Occluded Containers (CHOC) dataset that consists of RGB images, segmentation masks (object, hand+forearm), depth maps, 6D object poses, and Normalised Object Coordinate Space ([NOCS](https://geometry.stanford.edu/projects/NOCS_CVPR2019/)) maps.

<p float="middle">
  <img src="/images/000692.png" width="32%"/>
  <img src="/images/016165.png" width="32%"/> 
  <img src="/images/016995.png" width="32%"/>
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
    3. [Creating NOCS textures](#creating-nocs-textures)
5. [Notes](#notes)
6. [Enquiries, Question and Comments](#enquiries-question-and-comments)
7. [Licence](#license)

## Installation <a name="installation"></a>

The following instructions are meant for a Linux-based machine.

### Requirements <a name="requirements"></a>

This code has been tested on an Ubuntu 18.04 machine with the following dependencies:

- Blender 3.3.0
- Python 3.10
- Conda 4.13.0
- Pillow 9.3.0
- OpenCV 4.6.0
- SciPy 1.9.3

### Setting up Blender

1. Download [Blender 3.3.0](https://download.blender.org/release/Blender3.3/)
2. Run:
```
tar xf blender-3.3.0-linux-x64.tar.xz
```

3. Open Blender:
```
cd blender-3.3.0-linux-x64
./blender
```

Alternative (latest version using snap):
`sudo snap install blender --classic` (Note: if you do this, this repository might not function properly anymore)


### Setting up a Conda environment

1. Create and activate a conda environment:

```
conda create --name choc-render-env python=3.10
conda activate choc-render-env
```

2. Install dependencies:
```
pip install Pillow opencv-python scipy
```

### Linking Blender with Python dependencies

Add the path of the conda packages at the top of the _render\_all.py_ script:
`render_all.py (line 22)`
```diff
+ sys.path.append('/home/user/anaconda3/envs/choc-render-env/lib/python3.10/site-package')
```

To find the path, run 
```
conda info
```
and you should see it in the second row of the terminal:

```
active env location : /home/user/anaconda3/envs/choc-render-env
```
The full path to the Python libraries is: "/home/user/anaconda3/envs/choc-render-env/lib/python3.10/site-packages"


## Downloading data <a name="downloading-data"></a>

To render mixed-reality images, you need background images, object files, and optionally grasps+textures. Here we will explain how to download and unzip these data that were used for CHOC. The resulting file structure will look as follows:
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

1. Make a local folder called _data_ in _CHOC-renderer_:
```
mkdir data
```
2. From the [CHOC dataset](https://zenodo.org/record/5085801#.Y4iEytLP2V4), download:
* _backgrounds.zip_ (8.3 MB)
* _object\_models.zip_ (14.6 MB)
* grasps (1.3 GB) \[optional\] 

3. Request access [here](https://www.di.ens.fr/willow/research/obman/data/requestaccess.php) to download textures for the hands and forearms (grasps):
_bodyandhands.zip_ (267.2 MB) \[optional\].

4. Unzip all the zip files and their contents in _data_.


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

To run the code, with opening the Blender Graphical User Interface (GUI):

```
blender-3.3.0-linux-x64/blender --python render_all.py -- ./data ./outputs
``` 

or to run the code, without opening the Blender GUI, add the `--background` argument:

```
blender-3.3.0-linux-x64/blender --background --python render_all.py -- ./data ./outputs
```

#### Configuration

You can change the settings, such as the camera and randomization parameters in the [config.py](config.py) file.


## Tooling <a name="tooling"></a>

Here we highlight some instructions on how to label the flat surface in the scene, manually create grasps, and create NOCS textures in Blender.

### Labelling the surface in the scene <a name="labelling-the-surface-in-the-scene"></a>

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

To segment the plane in 3D, and compute its surface-normal, see [compute_table_normals.py](scrips/compute_table_normals.py).

### Creating Grasps <a name="creating-grasps"></a>

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

7. Use the GraspIt! GUI to make the grasp. 

Note: when all objects are loaded, interpenetration is possible, preventing any movement. You can turn OFF the Collision via: Element tab > Collision. Then before grasping, turn collision back ON.

8. Save the world as .xml file.
</details>

#### Converting from GraspIt! to Blender

1. Use [GraspIt_to_MANOparams.py](scripts/GraspIt_to_MANOparams.py) to extract the MANO parameters from the GraspIt! world files (.xml).
2. Use [MANOparams_to_Mesh.py](scripts/MANOparams_to_Mesh.py) to generate the hand+forearm meshes from the MANO parameters.

### Creating NOCS textures <a name="creating-nocs-textures"></a>

To create the NOCS textures in Blender, we used the [Texture Space](https://docs.blender.org/manual/en/latest/modeling/meshes/uv/uv_texture_spaces.html#texture-space) function. This allows you to create a bounding box around the object, and give each vertex of the object an RGB color based on its coordinate in that bounding box (exactly like the NOCS space). This vertex coloring can then be converted into the object's material/texture. For the code, see [create_nocs.py](scripts/create_nocs.py).

## Notes <a name="notes"></a>

#### Objects used in this dataset
- All objects in this dataset are downloaded from [ShapeNetSem](https://shapenet.org/).
- The objects are rescaled. See the dimensions of each object on our [webpage](https://corsmal.eecs.qmul.ac.uk/pose.html). 
- The objects are centered such that the origin of the objects is at height 0 of the object, and in the center for the other two dimensions. This is automatised by using [center.py](scripts/center.py).
- For the original object files, sometimes the textures don't show up in Blender. Therefore, we converted the files to .glb format (see: https://blender.stackexchange.com/questions/89010/materials-not-applied-after-importing-obj-shapenet/188192#188192)


## Enquiries, Question and Comments <a name="enquiries-question-and-comments"></a>

If you have any further enquiries, question, or comments, or you would like to file a bug report or a feature request, use the Github issue tracker or send an email to corsmal-challenge@qmul.ac.uk or eey138@qmul.ac.uk. 

## Licence <a name="license"></a>

This work is licensed under the MIT License. To view a copy of this license, see [LICENSE](LICENSE).
