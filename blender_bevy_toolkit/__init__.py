"""
Bevy is a game engine written in RUST, but it crrently lacks any sort of
scene editor. Blender is a 3D graphics program that seems like it would
be a good fit. This exporter converts from a blender file into a .scn file
that can be loaded into bevy.
"""
import os
import sys
import logging

import bpy
from bpy.app.handlers import persistent  # pylint: disable=E0401
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

from .export_data import export_data
from .toml_component import find_component
from .utils import jdict
from . import components
from . import operators
from . import component_base
from . import export

logger = logging.getLogger(__name__)

bl_info = {
    "name": "Bevy Game Engine Toolkit",
    "blender": (2, 90, 0),
    "category": "Game",
}


class BevyGlobalOptions(bpy.types.PropertyGroup):
    hide_default: bpy.props.BoolProperty(name="Hide Default", default=True)


class BevyComponentsPanel(bpy.types.Panel):
    """The panel in which buttons that add/remove components are shown"""

    bl_idname = "OBJECT_PT_bevy_components_panel"
    bl_label = "Bevy Components"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    def draw(self, context):
        """Create the UI for the panel"""
        row = self.layout.row()
        row.prop(context.scene.bevy_option, "hide_default")
        row = self.layout.row()
        row.operator("object.add_bevy_component")
        # row.operator("object.remove_bevy_component")


def register():
    """Blender needs to know about all our classes and UI panels
    so that it can draw/store things"""

    logger.info(jdict(event="registering_bevy_addon", state="start"))
    bpy.utils.register_class(BevyComponentsPanel)
    bpy.utils.register_class(operators.RemoveBevyComponent)
    bpy.utils.register_class(operators.AddBevyComponent)
    bpy.utils.register_class(ExportBevy)
    bpy.utils.register_class(BevyGlobalOptions)
    bpy.types.Scene.bevy_option = bpy.props.PointerProperty(
        type=BevyGlobalOptions
    )

    bpy.app.handlers.load_post.append(load_handler)

    bpy.types.TOPBAR_MT_file_export.append(menu_func)
    logger.info(jdict(event="registering_bevy_addon", state="end"))


def unregister():
    """When closing blender or uninstalling the addon we should leave
    things nice and clean...."""
    logger.info(jdict(event="unregistering_bevy_addon", state="start"))
    bpy.utils.unregister_class(BevyComponentsPanel)
    bpy.utils.unregister_class(operators.RemoveBevyComponent)
    bpy.utils.unregister_class(operators.AddBevyComponent)
    bpy.utils.unregister_class(ExportBevy)
    # bpy.utils.unregister_class(ExportBevyOption)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.utils.unregister_class(BevyGlobalOptions)
    del bpy.types.Object.bevy_option

    for component in component_base.COMPONENTS:
        logger.info(jdict(event="unregistering_component",
                    component=str(component)))
        component.unregister()
    logger.info(jdict(event="unregistering_bevy_addon", state="end"))


@persistent
def load_handler(_dummy):
    print("load_handler")
    """Scan the folder of the blend file for components to add"""
    for component in component_base.COMPONENTS:
        component.unregister()

    components.generate_component_list()
    find_component()
    operators.update_all_component_list()
    for component in component_base.COMPONENTS:
        logger.info(jdict(event="registering_component",
                    component=str(component)))
        component.register()


def menu_func(self, _context):
    """Add export operation to the menu"""
    self.layout.operator(ExportBevy.bl_idname, text="Bevy Engine (.scn)")


class ExportBevy(bpy.types.Operator, ExportHelper):
    """Selection to Godot"""

    bl_idname = "export_bevy.scn"
    bl_label = "Export to Bevy"
    bl_options = {"PRESET"}

    filename_ext = ".scn"
    filter_glob: bpy.props.StringProperty(default="*.scn", options={"HIDDEN"})

    gltf: bpy.props.BoolProperty(
        default=True, name="Use GLB for mesg/material")

    def execute(self, _context):
        """Begin the export"""

        if not self.filepath:
            raise Exception("filepath not set")

        do_export(
            {
                "output_filepath": self.filepath,
                "mesh_output_folder": "meshes",
                "material_output_folder": "materials",
                "texture_output_folder": "textures",
                "make_duplicates_real": False,
                "gltf": self.gltf,
            }
        )

        export_data.reset()
        bpy.ops.export_scene.gltf(filepath=self.filepath + '.glb', check_existing=True, convert_lighting_mode='SPEC',
                                  gltf_export_id='',
                                  export_format='GLB', ui_tab='GENERAL', export_copyright='',
                                  export_image_format='AUTO', export_texture_dir='', export_jpeg_quality=75,
                                  export_keep_originals=False, export_texcoords=True, export_normals=True,
                                  export_draco_mesh_compression_enable=False, export_draco_mesh_compression_level=6,
                                  export_draco_position_quantization=14, export_draco_normal_quantization=10,
                                  export_draco_texcoord_quantization=12, export_draco_color_quantization=10,
                                  export_draco_generic_quantization=12, export_tangents=False,
                                  export_materials='EXPORT', export_original_specular=False, export_colors=True,
                                  export_attributes=False, use_mesh_edges=False, use_mesh_vertices=False,
                                  export_cameras=False, use_selection=False, use_visible=False, use_renderable=False,
                                  use_active_collection_with_nested=True, use_active_collection=False,
                                  use_active_scene=False, export_extras=False, export_yup=True, export_apply=False,
                                  export_animations=True, export_frame_range=True, export_frame_step=1,
                                  export_force_sampling=True, export_nla_strips=True,
                                  export_nla_strips_merged_animation_name='Animation', export_def_bones=False,
                                  export_optimize_animation_size=False, export_anim_single_armature=True,
                                  export_reset_pose_bones=True, export_current_frame=False, export_skins=True,
                                  export_all_influences=False, export_morph=True, export_morph_normal=True,
                                  export_morph_tangent=False, export_lights=False, will_save_settings=False,
                                  filter_glob='*.glb')

        return {"FINISHED"}


def do_export(config):
    """Start the export. This is a global function to ensure it can be called
    both from the operator and from external scripts"""
    export.export_all(config)
