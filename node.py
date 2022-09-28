import bpy
import config

class Nodes():

    def node_setting_init(self):
        """Initializes the node setup for rendering 
            the combined RGB image, segmentation mask and depth map.
        """

        # Use nodes
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # Remove default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        

        # -- Initialize nodes
        # both
        render_layer_node = tree.nodes.new('CompositorNodeRLayers')
        
        # # depth
        multiply_node = tree.nodes.new('CompositorNodeMath')
        multiply_node.operation = 'MULTIPLY'
        multiply_node.inputs[1].default_value = 1000 # meter to millimeter
        set_alpha_node = tree.nodes.new('CompositorNodeSetAlpha')
        # depth output
        file_output_depth_node = tree.nodes.new('CompositorNodeOutputFile')
        file_output_depth_node.base_path = config.paths['depth_dir']
        file_output_depth_node.format.file_format = "OPEN_EXR"
        file_output_depth_node.format.color_mode = "RGB"
        file_output_depth_node.format.color_depth = "16"
        file_output_depth_node.file_slots[0].path = '######.exr' # blender placeholder #
        
        # rgb
        image_node = tree.nodes.new('CompositorNodeImage')
        alpha_over_node = tree.nodes.new('CompositorNodeAlphaOver')
        # rgb output
        file_output_rgb_node = tree.nodes.new('CompositorNodeOutputFile')
        file_output_rgb_node.base_path = config.paths['rgb_dir']
        file_output_rgb_node.format.file_format = "PNG" # default is "PNG"
        file_output_rgb_node.format.color_mode = "RGB"	# default is "BW"
        file_output_rgb_node.format.color_depth = "8"   # default is 8
        file_output_rgb_node.format.compression = 0	    # default is 15
        file_output_rgb_node.file_slots[0].path = '######.png' # blender placeholder #
        
        # segmentation mask output
        file_output_mask_node = tree.nodes.new('CompositorNodeOutputFile')
        file_output_mask_node.base_path = config.paths['mask_dir']
        file_output_mask_node.format.color_mode = "BW"	# default is "BW"
        file_output_mask_node.file_slots[0].path = '######.png' # blender placeholder #
        divide_node = tree.nodes.new('CompositorNodeMath')
        divide_node.operation = 'DIVIDE'
        divide_node.inputs[1].default_value = 255

        # -- Set node links
        # for rgb
        links.new(render_layer_node.outputs["Image"], alpha_over_node.inputs[2])
        links.new(image_node.outputs["Image"], alpha_over_node.inputs[1])
        links.new(alpha_over_node.outputs["Image"], file_output_rgb_node.inputs["Image"])
        # # for depth
        links.new(render_layer_node.outputs["Alpha"], set_alpha_node.inputs["Alpha"])
        links.new(render_layer_node.outputs["Depth"], multiply_node.inputs[0])
        links.new(multiply_node.outputs["Value"], set_alpha_node.inputs["Image"])
        links.new(set_alpha_node.outputs["Image"], file_output_depth_node.inputs["Image"])
        # for mask
        #links.new(render_layer_node.outputs["IndexOB"], file_output_mask_node.inputs["Image"])
        links.new(render_layer_node.outputs["IndexOB"], divide_node.inputs[0])
        links.new(divide_node.outputs["Value"], file_output_mask_node.inputs["Image"])

    def set_depth_nodes(self):

        # Use nodes
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links
        # Remove all previous nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        render_layer_node = tree.nodes.new('CompositorNodeRLayers')

        # depth
        multiply_node = tree.nodes.new('CompositorNodeMath')
        multiply_node.operation = 'MULTIPLY'
        multiply_node.inputs[1].default_value = 1000 # meter to millimeter
        set_alpha_node = tree.nodes.new('CompositorNodeSetAlpha')
        # depth output
        file_output_depth_node = tree.nodes.new('CompositorNodeOutputFile')
        file_output_depth_node.base_path = config.paths['depth_dir']
        file_output_depth_node.format.file_format = "OPEN_EXR"
        file_output_depth_node.format.color_mode = "RGB"
        file_output_depth_node.format.color_depth = "16"
        file_output_depth_node.file_slots[0].path = '######.exr' # blender placeholder #
        # for depth
        links.new(render_layer_node.outputs["Alpha"], set_alpha_node.inputs["Alpha"])
        links.new(render_layer_node.outputs["Depth"], multiply_node.inputs[0])
        links.new(multiply_node.outputs["Value"], set_alpha_node.inputs["Image"])
        links.new(set_alpha_node.outputs["Image"], file_output_depth_node.inputs["Image"])


    def set_nocs_nodes(self):
        """Initializes the node setup for rendering 
        the NOCS maps (i.e. normalised 3D coordinates)
        """
        # Use nodes
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # Remove all previous nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        
        # -- Initialize nodes
        render_layer_node = tree.nodes.new('CompositorNodeRLayers')

        alpha_convert_node = tree.nodes.new(type='CompositorNodePremulKey')
        alpha_convert_node.mapping = 'PREMUL_TO_STRAIGHT'

        file_output_nocs_node = tree.nodes.new('CompositorNodeOutputFile')
        file_output_nocs_node.base_path = config.paths['nocs_dir']
        file_output_nocs_node.format.file_format = "PNG" # default is "PNG"
        file_output_nocs_node.format.color_mode = "RGB"	# default is "BW"
        file_output_nocs_node.format.color_depth = "8"   # default is 8
        file_output_nocs_node.format.compression = 0	    # default is 15
        #file_output_nocs_node.file_slots[0].path = f"{global_im_count:06d}.png"
        file_output_nocs_node.file_slots[0].path = "######.png"

        # -- Set links
        links.new(render_layer_node.outputs["Image"], alpha_convert_node.inputs["Image"])
        links.new(alpha_convert_node.outputs["Image"], file_output_nocs_node.inputs["Image"])