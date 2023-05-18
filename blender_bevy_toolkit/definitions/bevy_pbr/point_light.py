from blender_bevy_toolkit.bevy_type.types import asColor
from blender_bevy_toolkit.bevy_type.bevy_scene import BevyComponent
from blender_bevy_toolkit.rust_types.ron import Bool
import bpy
from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
)

from blender_bevy_toolkit.component_constructor import (
    ComponentDefinition,
    component_from_def,
)


import logging
from blender_bevy_toolkit.utils import jdict
from blender_bevy_toolkit.rust_types import F32, RgbaLinear, Map

logger = logging.getLogger(__name__)


@register_component
class PointLight(ComponentBase):

    @staticmethod
    def encode_old(config, obj):
        assert PointLight.is_present(obj)

        return Map(
            type="bevy_pbr::light::PointLight",
            strCubemapFrustauct=Map(
                color=RgbaLinear(obj.data.color),
                illuminance=F32(obj.data.energy),
                range=F32(obj.data.cutoff_distance),
                radius=F32(obj.data.shadow_soft_size),
                shadows_enabled=Bool(obj.data.use_shadow),
                shadow_depth_bias=F32(obj.data.shadow_buffer_bias),
                shadow_normal_bias=F32(
                    obj.bevy_point_light_properties.shadow_normal_bias
                ),
            ),
        )

    @staticmethod
    def encode(config, obj) -> BevyComponent:
        """Returns a Component representing this component"""

        return BevyComponent(
            "bevy_pbr::light::PointLight",

            color=asColor(obj.data.color),
            intensity=F32(obj.data.energy),
            range=F32(obj.data.cutoff_distance),
            radius=F32(obj.data.shadow_soft_size),
            shadows_enabled=Bool(obj.data.use_shadow),
            shadow_depth_bias=F32(obj.data.shadow_buffer_bias),
            shadow_normal_bias=F32(
                obj.bevy_point_light_properties.shadow_normal_bias),

        )

    @staticmethod
    def can_add(obj):
        False

    @staticmethod
    def is_present(obj):
        return obj.type == "LIGHT" and obj.data.type == "POINT"

    @staticmethod
    def register():
        bpy.utils.register_class(PointLightPanel)
        bpy.utils.register_class(PointLightProperties)
        bpy.types.Object.bevy_point_light_properties = bpy.props.PointerProperty(
            type=PointLightProperties
        )

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(PointLightPanel)
        bpy.utils.unregister_class(PointLightProperties)
        del bpy.types.Object.bevy_point_light_properties


class PointLightPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_point_light_properties"
    bl_label = "BevyPointLight"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return PointLight.is_present(context.object)

    @staticmethod
    def draw(self, context):
        row = self.layout.row()
        row.label(text="Provider of omnidirectional illumination")

        row = self.layout.row()
        row.prop(context.object.data, "color")
        row = self.layout.row()
        row.prop(context.object.data, "energy")
        row = self.layout.row()
        row.prop(context.object.data, "cutoff_distance",
                 text="Range")  # Bevy Range
        row = self.layout.row()
        row.prop(context.object.data, "shadow_soft_size",
                 text="Radius")  # Bevy Radius
        row = self.layout.row()
        row.prop(context.object.data, "use_shadow", text="Enable Shadow")

        shadow_enabled = context.object.data.use_shadow
        row = self.layout.row()
        row.active = shadow_enabled
        row.prop(context.object.data, "shadow_buffer_bias")  # Bevy Depth Bias
        row = self.layout.row()
        row.active = shadow_enabled
        row.prop(context.object.bevy_point_light_properties,
                 "shadow_normal_bias")


class PointLightProperties(bpy.types.PropertyGroup):
    shadow_normal_bias: bpy.props.FloatProperty(
        name="Shadow Normal Bias", default=0.6)


register_component(
    component_from_def(
        ComponentDefinition(
            name="CubemapVisibleEntities",
            description="AUTO: Used by point light sources",
            id="cubemap_visible_entities",
            struct="bevy_pbr::bundle::CubemapVisibleEntities",
            fields=[],
        ),
        is_present_function=PointLight.is_present,
    )
)

register_component(
    component_from_def(
        ComponentDefinition(
            name="CubemapFrusta",
            description="AUTO: Used by point light sources",
            id="cubemap_frustra",
            struct="bevy_render::primitives::CubemapFrusta",
            fields=[],
        ),
        is_present_function=PointLight.is_present,
    )
)
