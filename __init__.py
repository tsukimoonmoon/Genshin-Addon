bl_info = {
    "name": "Genshin-Addon",
    "description": "Description of this addon",
    "author": "M4urlcl0, Zekium, Modder4869, Festivize",
    "version": (1, 0),
    "blender": (3, 2, 0),
    "location": "View3D",
    "description": "This addon was created to ease/automate the shading process for characters.",
    "warning": "This addon is still in development.",
    "wiki_url": "https://github.com/m4urlclo0",
    "category": "Object"}


import bpy
from distutils.util import execute
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
import os

class GENSHIN_TP_mainlayout(bpy.types.Panel):
    bl_label = "Genshin-Addon"
    bl_idname = "Genshin_TP_mainlayout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Genshin"

    def draw(self, context):
        layout = self.layout

class GENSHIN_PT_Menu(bpy.types.Panel):
    bl_label = "Tools"
    bl_idname = "Genshin_PT_Menu"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "Genshin_TP_mainlayout"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="TOOLS")
        box.operator("asing.mat", text="Asing Material").action = "asing_mat"
        box.operator("file.genshin_import", text="Texture (Linear)").action = "Import_TexLinear"

#Contributed by Modder4869 
class GENSHIN_OT_asingmat(bpy.types.Operator):
    bl_label = "Asing Material"
    bl_idname = "asing.mat"
    action: EnumProperty(
        items = [
            ('asing_mat', '', '')
        ]
    )

    def execute(self, context):
        if self.action == 'asing_mat':
            def findDressMaterialName(matName):
                for material in bpy.data.materials:
                    if matName in material.name:
                        x = material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image.name_full
                        #split reverse string ]
                        #print(x)
                        return x.replace('Tex_',"").split('_')[::-1][1]
                    else:
                        pass
            bpy.ops.object.select_all(action='DESELECT')
            # set body to active 
            bpy.context.view_layer.objects.active = bpy.data.objects["Body"]
            #select body
            bpy.data.objects["Body"].select_set(state=True, view_layer=None)
            meshes = ["Body", "EyeStar", "EffectMesh"]
            # select anything thats not Body , EyeStar,EffectMesh
            for object in bpy.context.scene.objects:
                if not object.name in meshes and object.type == "MESH":
                    object.select_set(state=True, view_layer=None)
                    #join mesh
            bpy.ops.object.join()

            # link materials 
            try:
                for object in bpy.data.objects:
                    name = object.name
                    if "Body" in name:
                        for materialSlot in object.material_slots:
                            if "Body" in materialSlot.name:
                                materialSlot.material = bpy.data.materials["miHoYo - Genshin Body"]
                            elif "Face" in materialSlot.name:
                                materialSlot.material = bpy.data.materials["miHoYo - Genshin Face"]
                            elif "Hair" in materialSlot.name:
                                materialSlot.material = bpy.data.materials["miHoYo - Genshin Hair"]
                            elif "Dress" in materialSlot.name:#is it Body or Hair i have no idea
                                matName = materialSlot.name.split('_')[-1]
                                materialSlot.material = bpy.data.materials["miHoYo - Genshin " + findDressMaterialName(matName)]

                else:
                    pass
            except Exception as e:
                print("MAKE SURE TO APPEND FILE FIRST\n")
                raise

            # select all empty objects
            bpy.ops.object.select_by_type(type="EMPTY")
            if 'Face Light Direction' in bpy.data.objects:
                bpy.data.objects['Face Light Direction'].select_set(state=False,view_layer=None)
            if 'Head Driver' in bpy.data.objects:
                bpy.data.objects['Head Driver'].select_set(state=False,view_layer=None)
            if 'Main Light Direction' in bpy.data.objects:
                bpy.data.objects['Main Light Direction'].select_set(state=False,view_layer=None)
            if 'Head Forward' in bpy.data.objects:
                bpy.data.objects['Head Forward'].select_set(state=False,view_layer=None)
            if 'Head Up' in bpy.data.objects:
                bpy.data.objects['Head Up'].select_set(state=False,view_layer=None)
                
                # delete them
            bpy.ops.object.delete()

                #hides EyeStar and EffectMesh
            if 'EffectMesh' in bpy.data.objects:
                bpy.data.objects['EffectMesh'].hide_set(True)
            if 'EyeStar' in bpy.data.objects:
                bpy.data.objects['EyeStar'].hide_set(True)

            #set view transform to standard
            bpy.context.scene.view_settings.view_transform = 'Standard'
            #rotate it (not sure about the values yet)
            bpy.ops.object.select_all(action='DESELECT')
            for object in bpy.data.objects:
                if object.type == 'ARMATURE':
                    print(object.name)
                    object.select_set(state=True)
            bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False) 
        return {'FINISHED'}

#Contributed by Zekium
class GI_OT_GenshinImportTextures(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "file.genshin_import"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Genshin: Import Textures"
    action: EnumProperty(
        items = [
            ('Import_TexLinear', '', '')
        ]
    )

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name = "Path",
        description = "Path to the folder containing the files to import",
        default = "",
        subtype = 'DIR_PATH'
        )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        directory = os.path.dirname(self.filepath)
        
        for name, folder, files in os.walk(directory):
            for file in files :
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath = img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                # declare body and face mesh variables
                body_var = bpy.context.scene.objects["Body"]
                # face_var = bpy.context.scene.objects["Face"]
                
                # Implement the texture in the correct node
                if "Hair_Diffuse" in file :
                    bpy.context.view_layer.objects.active = body_var
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes['Hair_Diffuse_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes['Hair_Diffuse_UV1'].image = img
                elif "Hair_Lightmap" in file :
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name='Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes['Hair_Lightmap_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes['Hair_Lightmap_UV1'].image = img
                elif "Hair_Normalmap" in file :
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name='Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes['Hair_Normalmap_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes['Hair_Normalmap_UV0'].image = img
                elif "Hair_Shadow_Ramp" in file :
                    bpy.data.node_groups['Hair Shadow Ramp'].nodes['Hair_Shadow_Ramp'].image = img
                elif "Body_Diffuse" in file :
                    bpy.context.view_layer.objects.active = body_var
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes['Body_Diffuse_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes['Body_Diffuse_UV1'].image = img
                elif "Body_Lightmap" in file :
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name='Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes['Body_Lightmap_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes['Body_Lightmap_UV1'].image = img
                elif "Body_Normalmap" in file :
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name='Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes['Body_Normalmap_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes['Body_Normalmap_UV1'].image = img
                elif "Body_Shadow_Ramp" in file :
                    bpy.data.node_groups['Body Shadow Ramp'].nodes['Body_Shadow_Ramp'].image = img
                elif "Face_Diffuse" in file :
                    bpy.context.view_layer.objects.active = body_var
                    bpy.context.object.material_slots.get('miHoYo - Genshin Face').material.node_tree.nodes['Face_Diffuse'].image = img
                elif "Face_Shadow" in file :
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name='Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Face').material.node_tree.nodes['Face_Shadow'].image = img
                elif "FaceLightmap" in file :
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name='Non-Color'
                    bpy.data.node_groups['Face Lightmap'].nodes['Face_Lightmap'].image = img
                elif "MetalMap" in file :
                    bpy.data.node_groups['Metallic Matcap'].nodes['MetalMap'].image = img
                else:
                    pass
            return {'FINISHED'}

        def execute(self, context):
            if self.action == 'Import_TexLinear':
                execute()
            return {'FINISHED'}

classes = [GENSHIN_TP_mainlayout, GENSHIN_PT_Menu, GENSHIN_OT_asingmat, GI_OT_GenshinImportTextures]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
