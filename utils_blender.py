import bpy

def deselect(scene):
    #scene = bpy.context.scene
    for obj in scene.objects:
        obj.select_set(False)

def clear_mesh():
    """
    Clears all meshes in the scene. Removes left-over materials.
    """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            # Remove materials and images to save memory
            if obj.data.materials != None:
                for i, mat in reversed(list(enumerate(obj.data.materials))):
                    if mat != None:
                        bpy.data.materials.remove(mat)
            bpy.ops.object.delete()
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

def clear_cameras():
    """
    Clears all lights in the scene. Removes left-over materials.
    """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            obj.select_set(True)
            bpy.ops.object.delete()
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

def clear_lights():
    """
    Clears all lights in the scene. Removes left-over materials.
    """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            obj.select_set(True)
            bpy.ops.object.delete()
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)