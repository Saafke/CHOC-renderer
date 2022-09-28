import bpy
import config
import os
import random
from PIL import Image
import numpy as np
import math
import utils_table
import utils_blender
from scipy.spatial.transform import Rotation as R

class ObjectUtils():
    
    def get_location_on_table(self, config, cur_mask_bg, cur_depth_bg):
        
        # Open mask 
        mask_im = Image.open(cur_mask_bg).convert('L')
        mask_ar = np.array(mask_im)
        
        # If depth is zero, resample
        z = 0
        while(z == 0):
            # Get random pixel location on table
            y_idx, x_idx = np.where(mask_ar!=0)
            rand_idx = np.random.randint(len(y_idx))
            table_y = y_idx[rand_idx] 
            table_x = x_idx[rand_idx]

            # Get depth of that pixel
            image_og = Image.open(cur_depth_bg)
            data_og = np.asarray(image_og)
            #data_og = cv2.imread(self.cur_depth_bg, cv2.IMREAD_ANYDEPTH) # buggy
            z = data_og[table_y][table_x]
        # Get 3d coord 
        x = (table_x - config.camera_params['cx']) * z / config.camera_params['fx']
        y = (table_y - config.camera_params['cy']) * z / config.camera_params['fy']

        return x,y,z

    def get_object(self, subset):
        """Gets a random ShapeNet object 

        Returns : model path and correct scale factor.
        """

        # get path
        objs_path = os.path.join(config.paths['objects']) # ,subset
        objs_nocs_path = os.path.join(config.paths['objects_nocs']) # ,subset

        # get random category. options: ["stem", "non-stem", "box"]
        rnd_obj_cat = random.choice(config.data_settings['object_categories'])
        #rnd_obj_cat = "box"
        self.cur_obj_class = rnd_obj_cat

        # get all objects of this category
        cur_objects = [_ for _ in os.listdir(os.path.join(objs_path, rnd_obj_cat)) if _.endswith(".glb")]
        
        # pick random one
        rnd_obj = random.choice(cur_objects)
        print("Object = {}".format(rnd_obj))

        # get full image path
        rnd_obj_path = os.path.join(objs_path, rnd_obj_cat, rnd_obj)

        # update nocs global
        self.cur_nocs_obj_path = os.path.join(objs_nocs_path, rnd_obj_cat, rnd_obj)
        #self.cur_nocs_obj_path = os.path.join(objs_path, rnd_obj_cat, rnd_obj)
        
        # update texture space path
        self.cur_texspace_path = os.path.join(config.paths['texture_spaces'], rnd_obj_cat, rnd_obj[:-4])
        
        # Save the correct scales of this object to this image
        txt_path = os.path.join(config.paths['scales'], rnd_obj_cat, rnd_obj[:-4]+".txt")
        scales_array = np.loadtxt(txt_path)
        np.savetxt( os.path.join(config.paths['scales_dir'], 
                    f"{self.im_count:06d}.txt"), 
                    scales_array, 
                    header= rnd_obj_cat + " " + rnd_obj + " " + self.cur_rgb_bg)

        return rnd_obj_path

    def place_object(self, model):
        """Loads an object and places it in the correct location, 
        with the correct rotation.
        
        Parameters
        ----------
        model : string
            The path to the model you want to import and place
        """
        
        # Import object
        bpy.ops.import_scene.gltf(filepath=model)

        # Select MESH object
        scene = bpy.context.scene
        for ob in scene.objects:
            ob.select_set(False)
            if ob.type == 'MESH':

                # Set active
                bpy.context.view_layer.objects.active = ob

                # Set pass for segmentation mask
                ob.pass_index = config.obj2id[self.cur_obj_class]

        # Assign the active object
        obj = bpy.context.view_layer.objects.active

        # Give object rotation and location (0,0,0), and scale 1
        bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

        # -- Set location, depends on pixel 
        # read segmentation image of background
        mask_im = Image.open(self.cur_mask_bg).convert('L')
        mask_ar = np.array(mask_im)

        # Here we will sample 3D locations on the table with the help of the segmented table mask and depth
        z = 0
        while(z == 0): # If the depth at this location is zero, resample location
            # get random pixel location on table
            y_idx, x_idx = np.where(mask_ar!=0)
            rand_idx = np.random.randint(len(y_idx))
            table_y = y_idx[rand_idx] 
            table_x = x_idx[rand_idx]

            # get depth of that pixel
            image_og = Image.open(self.cur_depth_bg)
            data_og_PIL = np.asarray(image_og)
            data_og_OPENCV = cv2.imread(self.cur_depth_bg, cv2.IMREAD_ANYDEPTH)
            print("PIL:", np.unique(data_og_PIL), "OpenCV:", np.unique(data_og_OPENCV))
            z = data_og_PIL[table_y][table_x]
        
        # get 3d coord (via backprojecting)
        x = (table_x - config.camera_params['cx']) * z / config.camera_params['fx']
        y = (table_y - config.camera_params['cy']) * z / config.camera_params['fy']

        # Set rotation to Euler angles representation
        obj.rotation_mode = 'XYZ'
        

        #### FOR OBJECTS ON TABLE

        # set final 3d coordinate
        self.coord = x, z, -y

        print("Object at location (x,z,-y):", x,z,-y)
        
        # set object at that location
        obj.location[0] = x / 1000 
        obj.location[1] = z / 1000 
        obj.location[2] = -y / 1000
        
        xAngle, yAngle = self.load_rotation_based_on_normal()

        # obj.rotation_mode = 'ZXY' #'YXZ'
        # obj.rotation_euler[0] = xAngle - math.radians(90)
        # obj.rotation_euler[1] = yAngle
        # obj.rotation_euler[2] = math.radians(360) # random yaw
        
        # First, align with the table, and hand with camera
        x_euler1 = xAngle - math.radians(90)
        y_euler1 = yAngle
        z_euler1 = math.radians(random.uniform(0,360))
        rot_matrix1 = R.from_euler('zxy', [x_euler1, y_euler1, z_euler1], degrees=False)
        
        if True: # use Euler
            eul = rot_matrix1.as_euler('xyz', degrees=False)
            print("myEuler:", [x_euler1, y_euler1, z_euler1], "\nR.Euler:", eul)
            obj.rotation_mode = 'XYZ' #'YXZ'
            obj.rotation_euler[0] = eul[0]
            obj.rotation_euler[1] = eul[1]
            obj.rotation_euler[2] = eul[2]
        else: # use Quaternion
            quat = rot_matrix1.as_quat() #x,y,z,w format
            print("quaternion:", quat)
            obj.rotation_mode = 'QUATERNION'
            # Blender has W,X,Y,Z. Scipy has X,Y,Z,W.
            obj.rotation_quaternion[0] = quat[3]
            obj.rotation_quaternion[1] = quat[0]
            obj.rotation_quaternion[2] = quat[1]
            obj.rotation_quaternion[3] = quat[2]

        

        self.locationx = obj.location[0]
        self.locationy = obj.location[1]
        self.locationz = obj.location[2]

        self.rotationx = obj.rotation_euler[0]
        self.rotationy = obj.rotation_euler[1]
        self.rotationz = obj.rotation_euler[2]

    def place_object_and_hand(self, obj_model, grasp_model, cur_obj_class, 
                              cur_depth_bg, cur_mask_bg, cur_bg,
                              normal_json, add_height=True):
        """Loads an object + hand mesh and places it in the correct location, 
        with the correct rotation and scale.
        
        Parameters
        ----------
        model : string
            The path to the model you want to import and place
        add_height : boolean
            Whether to render objects above the table
        """

        # Import object
        bpy.ops.import_scene.gltf(filepath=obj_model)
        
        # Import hand
        bpy.ops.import_scene.gltf(filepath=grasp_model)

        # Load random texture path
        all_tex_path = config.paths['textures']
        all_texs = os.listdir(all_tex_path)
        random_tex_path = random.choice(all_texs)
        print("\nTEXTURE={}\n".format(random_tex_path))
        random_tex = bpy.data.images.load(os.path.join(all_tex_path,random_tex_path))

        print("current object class:", cur_obj_class)

        ### Set random hand material and pass indices
        for o in bpy.data.objects:
            if o.name == "f_avg":

                # Set pass index to 4
                o.pass_index = config.obj2id['hand']
                o.select_set(True)
                # if flip_bool:
                #     bpy.ops.transform.mirror(orient_type="LOCAL", constraint_axis=(True, False, False))

                #bpy.data.worlds["World"].cycles_visibility.diffuse = False
                for m_slot in o.material_slots:
                    mat = m_slot.material
                    mat_nodes = mat.node_tree.nodes
                    mat_links = mat.node_tree.links
                    for n in mat_nodes:
                        if n.name == "Material Output":
                            mat_output_node = n
                        if n.name == "Principled BSDF":
                            princip_node = n
                            # n.inputs[0].default_value = 0,0,0,1
                            # # remove old link
                            # link = n.inputs['Emission'].links[0]
                            # mat.node_tree.links.remove(link)
                    
                    # Set new node - image texture
                    tex_node = mat_nodes.new('ShaderNodeTexImage')
                    # Set image
                    tex_node.image = random_tex
                    # Set new link
                    #mat_links.new(tex_node.outputs['Color'], princip_node.inputs['Emission'])     
                    mat_links.new(tex_node.outputs['Color'], princip_node.inputs['Base Color'])     

                o.select_set(False)
            elif o.name == 'f_avg.001': # if second hand
                o.pass_index = config.obj2id['hand']
            elif o.name != 'Camera' and o.name != 'Light': # if syn-object
                o.pass_index = config.obj2id[cur_obj_class]
            else:
                pass
        ###

        # Get location
        x,y,z = self.get_location_on_table(config, cur_mask_bg, cur_depth_bg)
        # Set location
        if add_height:
            # Get random height in mm
            rand_height = float(np.random.randint(config.random_params["min_height"], config.random_params["max_height"]))
            # init new height
            heightened_y = -y + rand_height
            # set final 3d coordinate
            self.coord = x, z, heightened_y
        # Just render object+hand on the table
        else:
            self.coord = x, z, -y


        # Set some random variables
        rand_hand_rot = math.radians(np.random.randint(-45,52))
        x_rot = math.radians(random.uniform(-1 * config.random_params["x_rotation"], config.random_params["x_rotation"]))
        y_rot = math.radians(random.uniform(-1 * config.random_params["y_rotation"], config.random_params["y_rotation"]))
        z_rot = math.radians(np.random.randint(config.random_params["z_rotation"])) # for stem & non-stem
        flip_box = random.uniform(0, 1)

        # Load x and y rotation, based on the table normal
        xAngle, yAngle = utils_table.load_rotation_based_on_normal(normal_json, cur_bg)
        
        # Loop over meshes
        scene = bpy.context.scene
        for obj in scene.objects:
            obj.select_set(False)
            # if a mesh
            if obj.type == 'MESH':

                #obj.rotation_mode = 'XYZ'

                # Place object at location
                obj.location[0] = x / 1000 
                obj.location[1] = z / 1000 
                if add_height:
                    obj.location[2] = heightened_y / 1000
                else:
                    obj.location[2] = -y / 1000 

                # set rotation to align with table
                #obj.select_set(True)
                
                # TODO: freely rotate about yaw axis, for stem and non-stem
                # TODO: flip about yaw, for boxes

                if not add_height: # On the table
                    # First rotation to rotation matrix
                    r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), rand_hand_rot], degrees=False)
                    rot_matrix1 = r1.as_matrix()
                    quat1 = r1.as_quat()
                    obj.rotation_mode = 'QUATERNION'
                    obj.rotation_quaternion[0] = quat1[3]
                    obj.rotation_quaternion[1] = quat1[0]
                    obj.rotation_quaternion[2] = quat1[1]
                    obj.rotation_quaternion[3] = quat1[2]
                else:
                    use_euler = False
                    # USING EULER
                    if use_euler:
                        # First, transformation is: 
                        obj.rotation_mode = 'ZXY' # means we should do first Y, then X, then Z
                        # First, yAngle
                        obj.rotation_euler[1] = yAngle
                        # Then, xAngle
                        obj.rotation_euler[0] = xAngle - math.radians(90)
                        # Then, z
                        obj.rotation_euler[2] = rand_hand_rot

                        # set
                        obj.select_set(True)
                        bpy.ops.object.transforms_to_deltas(mode='ROT') 
                        obj.select_set(False)
                        
                        # Second transformation is: 
                        obj.rotation_mode = 'ZXY'
                        # First, Y
                        obj.rotation_euler[1] = y_rot
                        # Then, X
                        obj.rotation_euler[0] = x_rot
                        # Last, Z
                        obj.rotation_euler[2] = 0
                    else:
                        print("yAngle:", math.degrees(yAngle), "xAngle:", math.degrees(xAngle - math.radians(90)), "rand_hand_rot:", math.degrees(rand_hand_rot))
                        print("y_rot", math.degrees(y_rot), "x_rot", math.degrees(x_rot))
                        xx=json54
                        # First rotation to rotation matrix
                        r1 = R.from_euler("YXZ", [yAngle, xAngle - math.radians(90), rand_hand_rot], degrees=False)
                        rot_matrix1 = r1.as_matrix()
                        quat1 = r1.as_quat()
                        
                        # Second rotation to rotation matrix
                        r2 = R.from_euler("YXZ", [y_rot, x_rot, 0], degrees=False)
                        rot_matrix2 = r2.as_matrix()
                        
                        # Both
                        rot_matrix12 = rot_matrix1 @ rot_matrix2
                        
                        # Convert to quaternion
                        r12 = R.from_matrix(rot_matrix12)
                        # X,Y,Z,W
                        quat12 = r12.as_quat()

                        print("quat12:", quat12)

                        obj.rotation_mode = 'QUATERNION'
                        obj.rotation_quaternion[0] = quat12[3]
                        obj.rotation_quaternion[1] = quat12[0]
                        obj.rotation_quaternion[2] = quat12[1]
                        obj.rotation_quaternion[3] = quat12[2]

                    
                self.locationx = obj.location[0]
                self.locationy = obj.location[1]
                self.locationz = obj.location[2]
                
                self.rotationw = obj.rotation_quaternion[0]
                self.rotationx = obj.rotation_quaternion[1]
                self.rotationy = obj.rotation_quaternion[2]
                self.rotationz = obj.rotation_quaternion[3]

                #bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)
        
        hand_objects = []
        # Select object again
        scene = bpy.context.scene
        for ob in scene.objects:
            ob.select_set(False)
            if ob.type == 'MESH':
                if ob.name != "f_avg" or ob.name != "f_avg.001":
                    bpy.context.view_layer.objects.active = ob
                    obj = bpy.context.view_layer.objects.active
                if ob.name == "f_avg" or ob.name == "f_avg.001":
                    print("ADDING:", ob.name)
                    hand_objects.append(ob)
                    ob.select_set(True)
                    bpy.ops.object.transform_apply(rotation=True, location=True, scale=True)
                    ob.select_set(False)

        return hand_objects, [self.locationx, self.locationy, self.locationz], [self.rotationw, self.rotationx, self.rotationy, self.rotationz]

    def generate_nocs(self, N, cur_nocs_obj_path, texspace_size):
        """Loads object with NOCS-map material and places it in the same location and rotation.
        """

        # delete previous mesh
        utils_blender.clear_mesh()

        # import object
        bpy.ops.import_scene.gltf(filepath=cur_nocs_obj_path)

        # replace object with vertex object at same position
        # Select object
        scene = bpy.context.scene
        for ob in scene.objects:
            ob.select_set(False)
            if ob.type == 'MESH':
                bpy.context.view_layer.objects.active = ob
        obj = bpy.context.view_layer.objects.active

        # Load the texture space
        #texspace_size = np.loadtxt(self.cur_texspace_path)
        # Set the texture space size
        obj_mesh_name = obj.data.name
        obj.show_texture_space = True
        bpy.data.meshes[obj_mesh_name].use_auto_texspace = False
        bpy.data.meshes[obj_mesh_name].texspace_size = texspace_size, texspace_size, texspace_size
        
        # Remove other material
        obj.data.materials.clear()

        # Make a new material
        nocs_mat = bpy.data.materials.new('nocs_material')
        nocs_mat.use_nodes = True
        bpy.data.meshes[obj_mesh_name].materials.append(nocs_mat)
        
        # deactivate shadows
        nocs_mat.shadow_method = 'NONE'
        mat_nodes = nocs_mat.node_tree.nodes
        mat_links = nocs_mat.node_tree.links

        # Get default things in material
        for n in mat_nodes:
            if n.name == "Material Output":
                mat_output_node = n
            if n.name == "Principled BSDF":
                for link in n.inputs[0].links:
                    nocs_mat.node_tree.links.remove(link)

        # Set texture node to create NOCS colors
        tex_node = mat_nodes.new('ShaderNodeTexCoord')
        # set new link - bypassing principle node
        mat_links.new(tex_node.outputs["Generated"], mat_output_node.inputs[0])        

        # set location
        obj.location[0] = self.locationx
        obj.location[1] = self.locationy
        obj.location[2] = self.locationz
        # set rotation
        obj.rotation_mode = 'QUATERNION' #'XYZ'
        obj.rotation_quaternion[0] = self.rotationw
        obj.rotation_quaternion[1] = self.rotationx
        obj.rotation_quaternion[2] = self.rotationy
        obj.rotation_quaternion[3] = self.rotationz
        print(self.locationx, self.locationy, self.locationz, self.rotationx, self.rotationy, self.rotationz)
        bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

        # go into material preview
        my_areas = bpy.context.workspace.screens[0].areas
        my_shading = 'MATERIAL'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'

        for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = my_shading

        # set dimensions and path of this scene
        sce = bpy.context.scene.name
        
        # Set NOCS node setup
        N.set_nocs_nodes()

        # Set unedited colors
        bpy.data.scenes[sce].view_settings.view_transform = "Standard" # Default is Filmic
        
        # Render NOCS
        bpy.data.scenes[sce].view_settings.view_transform = "Raw" # Default is Filmic
        bpy.data.scenes[sce].cycles.samples = 1
        bpy.data.scenes[sce].cycles.use_denoising = False
        bpy.ops.render.render(write_still=True)
        
        # Reverse settings back to standard
        bpy.data.scenes[sce].view_settings.view_transform = "Standard" # Default is Filmic
        bpy.data.scenes[sce].cycles.samples = 2048 # NOTE: can turn this down, or add time limit
        bpy.data.scenes[sce].cycles.use_denoising = True

        #"Current Frame, to update animation data from python frame_set() instead"
        current_frame = bpy.context.scene.frame_current
        # #"Set scene frame updating all objects immediately"
        bpy.context.scene.frame_set(current_frame + 1)

        # Set ORIGINAL node setup
        N.node_setting_init()
        bpy.data.scenes[sce].display_settings.display_device = "sRGB"

        bpy.data.scenes[sce].render.filepath = ""

        for block in bpy.data.images:
            bpy.data.images.remove(block)

