import bpy
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper
from bpy.utils import register_class, unregister_class
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
import os


# main class
class GI_PT_Layout(Panel):
    bl_label = "Genshin Addon"
    bl_idname = "GI_PT_Layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Genshin"

    def draw(self, context):
        layout = self.layout


# menu panel
class GI_PT_Menu(Panel):
    bl_label = "Menu Panel"
    bl_idname = "GI_PT_Menu"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "GI_PT_Layout"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box1 = layout.box()
        box.label(text="Tools", icon="TOOL_SETTINGS")
        box.operator("file.genshin_import_materials", text="Append Materials", icon="MATERIAL_DATA").action = "append_mat"
        box.operator("assing.material", text="Assing Materials", icon="NODE_MATERIAL").action = "assing_mat"
        box.operator("file.genshin_import", text="Import Textures (Linear)",
                     icon="FILEBROWSER").action = "Import_TexLinear"
        box1.label(text="Json Data", icon="CONSOLE")


def findDressMaterialName(matName):
    for material in bpy.data.materials:
        if matName in material.name:
            x = material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[
                0].from_node.image.name_full
            return x.replace('Tex_', "").split('_')[::-1][1]


# Contributed by Modder4869 - assing all materials
class GI_OT_Assing_Mat(Operator):
    bl_label = "Assing Material"
    bl_idname = "assing.material"
    action: EnumProperty(
        items=[
            ('assing_mat', '', '')
        ]
    )

    def execute(self, context):
        if self.action == 'assing_mat':
            bpy.ops.object.select_all(action='DESELECT')
            # set body to active
            bpy.context.view_layer.objects.active = bpy.data.objects["Body"]
            # select body
            bpy.data.objects["Body"].select_set(state=True, view_layer=None)
            meshes = ["Body", "EyeStar", "EffectMesh"]
            # select anything thats not Body, EyeStar, EffectMesh
            for object in bpy.context.scene.objects:
                if not object.name in meshes and object.type == "MESH":
                    object.select_set(state=True, view_layer=None)
            # join mesh
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
                            elif "Dress" in materialSlot.name:  # is it Body or Hair i have no idea
                                matName = materialSlot.name.split('_')[-1]
                                dressMaterial = bpy.data.materials[
                                    "miHoYo - Genshin " + findDressMaterialName(matName)].copy()
                                dressMaterial.name = "miHoYo - Genshin " + matName
                                materialSlot.material = bpy.data.materials["miHoYo - Genshin " + matName]
                    pass
            except Exception as e:
                self.report({'WARNING'}, "Make sure to append file first")
                raise
            # select all empty objects
            bpy.ops.object.select_by_type(type="EMPTY")
            if 'Face Light Direction' in bpy.data.objects:
                bpy.data.objects['Face Light Direction'].select_set(state=False, view_layer=None)
            if 'Head Driver' in bpy.data.objects:
                bpy.data.objects['Head Driver'].select_set(state=False, view_layer=None)
            if 'Main Light Direction' in bpy.data.objects:
                bpy.data.objects['Main Light Direction'].select_set(state=False, view_layer=None)
            if 'Head Forward' in bpy.data.objects:
                bpy.data.objects['Head Forward'].select_set(state=False, view_layer=None)
            if 'Head Up' in bpy.data.objects:
                bpy.data.objects['Head Up'].select_set(state=False, view_layer=None)

                # delete them
            bpy.ops.object.delete()

            # hides EyeStar and EffectMesh
            if 'EffectMesh' in bpy.data.objects:
                bpy.data.objects['EffectMesh'].hide_set(True)
            if 'EyeStar' in bpy.data.objects:
                bpy.data.objects['EyeStar'].hide_set(True)

            # set view transform to standard
            bpy.context.scene.view_settings.view_transform = 'Standard'
            # rotate it (not sure about the values yet)
            bpy.ops.object.select_all(action='DESELECT')
            for object in bpy.data.objects:
                if object.type == 'ARMATURE':
                    print(object.name)
                    object.select_set(state=True)
            bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL',
                                     orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                     constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False,
                                     proportional_edit_falloff='SMOOTH', proportional_size=1,
                                     use_proportional_connected=False, use_proportional_projected=False)
            self.report({'INFO'}, "Assigned materials")
        return {'FINISHED'}


# Contributed by Zekium - import textures
class GI_OT_GenshinImportTextures(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "file.genshin_import"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Genshin: Import Textures"
    action: EnumProperty(
        items=[
            ('Import_TexLinear', '', '')
        ]
    )

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the folder containing the files to import",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        directory = os.path.dirname(self.filepath)

        for name, folder, files in os.walk(directory):
            for file in files:
                # load the file with the correct alpha mode
                img_path = directory + "/" + file
                img = bpy.data.images.load(filepath=img_path, check_existing=True)
                img.alpha_mode = 'CHANNEL_PACKED'

                # declare body and face mesh variables
                body_var = bpy.context.scene.objects["Body"]
                # face_var = bpy.context.scene.objects["Face"]

                # Implement the texture in the correct node
                if "Hair_Diffuse" in file:
                    bpy.context.view_layer.objects.active = body_var
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes[
                        'Hair_Diffuse_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes[
                        'Hair_Diffuse_UV1'].image = img
                elif "Hair_Lightmap" in file:
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name = 'Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes[
                        'Hair_Lightmap_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes[
                        'Hair_Lightmap_UV1'].image = img
                elif "Hair_Normalmap" in file:
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name = 'Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes[
                        'Hair_Normalmap_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Hair').material.node_tree.nodes[
                        'Hair_Normalmap_UV1'].image = img
                elif "Hair_Shadow_Ramp" in file:
                    bpy.data.node_groups['Hair Shadow Ramp'].nodes['Hair_Shadow_Ramp'].image = img
                elif "Body_Diffuse" in file:
                    bpy.context.view_layer.objects.active = body_var
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes[
                        'Body_Diffuse_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes[
                        'Body_Diffuse_UV1'].image = img
                elif "Body_Lightmap" in file:
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name = 'Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes[
                        'Body_Lightmap_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes[
                        'Body_Lightmap_UV1'].image = img
                elif "Body_Normalmap" in file:
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name = 'Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes[
                        'Body_Normalmap_UV0'].image = img
                    bpy.context.object.material_slots.get('miHoYo - Genshin Body').material.node_tree.nodes[
                        'Body_Normalmap_UV1'].image = img
                elif "Body_Shadow_Ramp" in file:
                    bpy.data.node_groups['Body Shadow Ramp'].nodes['Body_Shadow_Ramp'].image = img
                elif "Body_Specular_Ramp" in file:
                    img.colorspace_settings.name = 'Non-Color'
                    bpy.data.node_groups['Body Specular Ramp'].nodes['Body_Specular_Ramp'].image = img
                elif "Face_Diffuse" in file:
                    bpy.context.view_layer.objects.active = body_var
                    bpy.context.object.material_slots.get('miHoYo - Genshin Face').material.node_tree.nodes[
                        'Face_Diffuse'].image = img
                elif "Face_Shadow" in file:
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name = 'Non-Color'
                    bpy.context.object.material_slots.get('miHoYo - Genshin Face').material.node_tree.nodes[
                        'Face_Shadow'].image = img
                elif "FaceLightmap" in file:
                    bpy.context.view_layer.objects.active = body_var
                    img.colorspace_settings.name = 'Non-Color'
                    bpy.data.node_groups['Face Lightmap'].nodes['Face_Lightmap'].image = img
                elif "MetalMap" in file:
                    bpy.data.node_groups['Metallic Matcap'].nodes['MetalMap'].image = img
                else:
                    pass
                fixDressTexture()
            self.report({'INFO'}, "Imported and assigned textures")
            return {'FINISHED'}

        def execute(self, context):
            if self.action == 'Import_TexLinear':
                execute()
            return {'FINISHED'}


# Structure for file comes from a script initially written by Zekium from Discord
# Written by Mken from Discord - edited by me
class GI_OT_GenshinImportMaterials(Operator, ImportHelper):
    """Select Festivity's Shaders folder to import materials"""
    bl_idname = "file.genshin_import_materials"  # important since its how we chain file dialogs
    bl_label = "1_Genshin: Select Festivity Folder"
    action: EnumProperty(
        items=[
            ('append_mat', '', '')
        ]
    )

    # ImportHelper mixin class uses this
    filename_ext = "*.*"

    import_path: StringProperty(
        name="Path",
        description="Path to the folder of Festivity's Shaders project",
        default="",
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="*.*",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    next_step_idx: IntProperty()
    file_directory: StringProperty()

    def execute(self, context):
        if self.action == 'append_mat':
            BLEND_FILE_WITH_GENSHIN_MATERIALS = 'miHoYo - Genshin Impact.blend'
            MATERIAL_PATH_INSIDE_BLEND_FILE = 'Material'
            project_root_directory_file_path = self.file_directory if self.file_directory else os.path.dirname(self.filepath)

            DIRECTORY_WITH_BLEND_FILE_PATH = os.path.join(
                project_root_directory_file_path,
                BLEND_FILE_WITH_GENSHIN_MATERIALS,
                MATERIAL_PATH_INSIDE_BLEND_FILE
            )
            NAMES_OF_GENSHIN_MATERIALS = [
                {'name': 'miHoYo - Genshin Body'},
                {'name': 'miHoYo - Genshin Face'},
                {'name': 'miHoYo - Genshin Hair'},
                {'name': 'miHoYo - Genshin Outlines'}
            ]

            bpy.ops.wm.append(
                directory=DIRECTORY_WITH_BLEND_FILE_PATH,
                files=NAMES_OF_GENSHIN_MATERIALS
            )
            self.report({'INFO'}, "Imported Materials")
            return {'FINISHED'}


def fixDressTexture():
    for mat in bpy.data.materials:
        matName = mat.name.split('_')[-1]
        if (f'_{matName}' in mat.name) and ('Dress' in mat.name):
            dressname = findDressMaterialName(matName)
            dressMaterial = bpy.data.materials["miHoYo - Genshin " + matName]
            dressMaterial.node_tree.nodes[f'{dressname}_Lightmap_UV0'].image = \
                bpy.data.materials[f'miHoYo - Genshin {dressname}'].node_tree.nodes[f'{dressname}_Lightmap_UV0'].image
            dressMaterial.node_tree.nodes[f'{dressname}_Lightmap_UV1'].image = \
                bpy.data.materials[f'miHoYo - Genshin {dressname}'].node_tree.nodes[f'{dressname}_Lightmap_UV1'].image
            dressMaterial.node_tree.nodes[f'{dressname}_Diffuse_UV0'].image = \
                bpy.data.materials[f'miHoYo - Genshin {dressname}'].node_tree.nodes[f'{dressname}_Diffuse_UV0'].image
            dressMaterial.node_tree.nodes[f'{dressname}_Diffuse_UV1'].image = \
                bpy.data.materials[f'miHoYo - Genshin {dressname}'].node_tree.nodes[f'{dressname}_Diffuse_UV1'].image
            dressMaterial.node_tree.nodes[f'{dressname}_Normalmap_UV0'].image = \
                bpy.data.materials[f'miHoYo - Genshin {dressname}'].node_tree.nodes[f'{dressname}_Normalmap_UV0'].image
            dressMaterial.node_tree.nodes[f'{dressname}_Normalmap_UV1'].image = \
                bpy.data.materials[f'miHoYo - Genshin {dressname}'].node_tree.nodes[f'{dressname}_Normalmap_UV1'].image


classes = [GI_PT_Layout, GI_PT_Menu, GI_OT_Assing_Mat, GI_OT_GenshinImportTextures, GI_OT_GenshinImportMaterials]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)


if __name__ == "__main__":
    register()
