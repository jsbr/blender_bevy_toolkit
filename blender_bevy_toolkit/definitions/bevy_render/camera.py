from blender_bevy_toolkit.bevy_type.types import asColor
from blender_bevy_toolkit.bevy_type.bevy_scene import BevyComponent, EnumProp, RawValue, StructProp, DebugProp
import bpy

from blender_bevy_toolkit.bevy_type.enums import TONE_MAPPING
from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
)
from blender_bevy_toolkit.component_constructor import (
    ComponentDefinition,
    component_from_def,
)

import logging
from blender_bevy_toolkit.rust_types.ron import Struct, Tuple
from blender_bevy_toolkit.utils import jdict
from blender_bevy_toolkit.rust_types import F32, Option, Enum, EnumValue, Map

logger = logging.getLogger(__name__)


class CameraDescriptionProperties(bpy.types.PropertyGroup):
    hdr: bpy.props.BoolProperty(name="hdr", default=False)
    aspect_ratio: bpy.props.FloatProperty("aspect ration", default=1.0)
    clear_color: bpy.props.FloatVectorProperty("clear color", subtype="COLOR",
                                               size=4,
                                               min=0.0,
                                               max=1.0,
                                               default=(0.0, 0.0, 0.0, 1.0))
    tonemapping: bpy.props.EnumProperty(
        items=TONE_MAPPING, name="Tonemapping", default="BlenderFilmic")

    exposure: bpy.props.FloatProperty(default=0.0, name="exposure")
    gamma: bpy.props.FloatProperty(default=1.0, name="gamma")
    pre_saturation: bpy.props.FloatProperty(default=1.0, name="pre_saturation")
    post_saturation: bpy.props.FloatProperty(
        default=1.0, name="post_saturation")


@register_component
class Camera(ComponentBase):

    @staticmethod
    def encode(config, obj) -> BevyComponent:
        """Returns a Component representing this component"""
        print("encode Camera")

        return BevyComponent(
            "bevy_render::camera::camera::Camera",
            viewport=EnumProp("None"),
            order=0,
            is_active=True,
            hdr=obj.bevy_camera_description.hdr,
            msaa_writeback=True,
        )

    @staticmethod
    def is_present(obj):
        return obj.type == "CAMERA"

    @staticmethod
    def register():
        print("register Camera")
        bpy.utils.register_class(CameraDescriptionProperties)
        bpy.types.Object.bevy_camera_description = bpy.props.PointerProperty(
            type=CameraDescriptionProperties
        )
        bpy.utils.register_class(CameraPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(CameraPanel)
        bpy.utils.unregister_class(CameraDescriptionProperties)
        del bpy.types.Object.bevy_camera_description

    @staticmethod
    def can_add(obj):
        return False


class CameraPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_camera_properties"
    bl_label = "Bevy Camera"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return Camera.is_present(context.object) and not bpy.context.scene.bevy_option.hide_default

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.object.bevy_camera_description, "hdr", text="HDR")

        box = self.layout.box()
        row = box.row()
        row.label(text='Tonemapping')
        row = box.row()
        row.prop(context.object.bevy_camera_description,
                 "tonemapping", text="Tonemapping")

        box = self.layout.box()
        row = box.row()
        row.label(text='ColorGrading')
        row = box.row()
        row.prop(context.object.bevy_camera_description,
                 "exposure", text="Exposure")
        row.prop(context.object.bevy_camera_description, "gamma", text="Gamma")
        row = box.row()
        row.prop(context.object.bevy_camera_description,
                 "pre_saturation", text="Pre saturation")
        row.prop(context.object.bevy_camera_description,
                 "post_saturation", text="Post saturation")


register_component(
    component_from_def(
        ComponentDefinition(
            name="VisibleEntities",
            description="AUTO: Used by camera",
            id="camera_visible_entities",
            struct="bevy_render::view::visibility::VisibleEntities",
            fields=[],
        ),
        is_present_function=Camera.is_present,
    )
)

register_component(
    component_from_def(
        ComponentDefinition(
            name="Frustum",
            description="AUTO: Used by camera",
            id="camera_frustrum",
            struct="bevy_render::primitives::Frustum",
            fields=[],
        ),
        is_present_function=Camera.is_present,
    )
)


@register_component
class PerspectiveProjection(ComponentBase):
    """
    Controls for Perspective projection matrix
    """

    @staticmethod
    def encode(config, obj):
        value = Struct(
            aspect_ratio=1.0,
            near=F32(obj.data.clip_start),
            far=F32(obj.data.clip_end),
            fov=F32(obj.data.angle),
        )
        return BevyComponent(
            "bevy_render::camera::projection::Projection", EnumValue("Perspective", Tuple(value)))  # review

    @staticmethod
    def is_present(obj):
        return Camera.is_present(obj) and obj.data.type == "PERSP"

    @staticmethod
    def register():
        bpy.utils.register_class(PerspectiveProjectionPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(PerspectiveProjectionPanel)

    @staticmethod
    def can_add(obj):
        return False


class PerspectiveProjectionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_projection_properties"
    bl_label = "BevyPerspectiveProjectionMatrix"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return PerspectiveProjection.is_present(context.object) and not bpy.context.scene.bevy_option.hide_default

    def draw(self, context):
        row = self.layout.row()
        row.label(text="Computes a projection matrix from a set of properties")

        row = self.layout.row()
        row.prop(context.object.bevy_camera_description,
                 "aspect_ratio", text="aspect ratio")
        row = self.layout.row()
        row.prop(context.object.data, "angle", text="FOV")
        row = self.layout.row()
        row.prop(context.object.data, "clip_start", text="Near")
        row = self.layout.row()
        row.prop(context.object.data, "clip_end", text="Far")

        if context.object.data.sensor_fit != "VERTICAL":
            row = self.layout.row()
            row.label(text="Camera sensor fit should be vertical:", icon="ERROR")
            row = self.layout.row()
            row.prop(context.object.data, "sensor_fit")


@register_component
class OrthographicProjection(ComponentBase):

    @staticmethod
    def encode(config, obj):
        return Map(
            type="bevy_render::camera::projection::OrthographicProjection",
            struct=Map(
                left=F32(-1.0),
                right=F32(1.0),
                bottom=F32(-1.0),
                top=F32(1.0),
                near=F32(obj.data.clip_start),
                far=F32(obj.data.clip_end),
                window_origin=Enum(
                    "bevy_render::camera::projection::WindowOrigin",
                    EnumValue("Center"),
                ),
                scaling_mode=Enum(
                    "bevy_render::camera::projection::ScalingMode",
                    EnumValue("FixedVertical"),
                ),
                scale=F32(obj.data.ortho_scale / 2.0),
                depth_calculation=Enum(
                    "bevy_render::camera::camera::DepthCalculation",
                    EnumValue("Distance"),
                ),
            ),
        )

    @staticmethod
    def is_present(obj):
        return Camera.is_present(obj) and obj.data.type == "ORTHO"

    @staticmethod
    def register():
        bpy.utils.register_class(OrthographicProjectionPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(OrthographicProjectionPanel)

    @staticmethod
    def can_add(obj):
        return False


class OrthographicProjectionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_orthographic_projection_properties"
    bl_label = "BevyOrthographicProjectionMatrix"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return OrthographicProjection.is_present(context.object) and not bpy.context.scene.bevy_option.hide_default

    def draw(self, context):
        row = self.layout.row()
        row.label(text="Computes a projection matrix from a set of properties")

        row = self.layout.row()
        row.prop(context.object.data, "ortho_scale", text="Scale")
        row = self.layout.row()
        row.prop(context.object.data, "clip_start", text="Near")
        row = self.layout.row()
        row.prop(context.object.data, "clip_end", text="Far")

        if context.object.data.sensor_fit != "VERTICAL":
            # Technically not required, but then I'd need to implement both enum options
            # in the OrthographicProjection.encode() function
            row = self.layout.row()
            row.label(text="Camera sensor fit should be vertical:", icon="ERROR")
            row = self.layout.row()
            row.prop(context.object.data, "sensor_fit")


@register_component
class Camera3d(ComponentBase):
    @staticmethod
    def encode(config, obj):
        return BevyComponent(
            "bevy_core_pipeline::core_3d::camera_3d::Camera3d",
            clear_color=DebugProp("Default"),
            depth_load_op=EnumProp("Clear", 0.0),
        )

    @staticmethod
    def is_present(obj):
        return obj.type == "CAMERA"

    @staticmethod
    def register():
        bpy.utils.register_class(Camera3dPanel)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(Camera3dPanel)

    @staticmethod
    def can_add(obj):
        return False


class Camera3dPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_camera3d_properties"
    bl_label = "Camera 3D properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return Camera3d.is_present(context.object) and not bpy.context.scene.bevy_option.hide_default

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.object.bevy_camera_description, "clear_color",
                 text="Clear color")
        row = self.layout.row()
        row.prop(context.object.data, "clip_start", text="Near")


@register_component
class DebandDither(ComponentBase):
    @staticmethod
    def encode(config, obj):
        return BevyComponent(
            "bevy_core_pipeline::tonemapping::DebandDither", RawValue(
                "Enabled")
        )

    @staticmethod
    def is_present(obj):
        return obj.type == "CAMERA"

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass

    @staticmethod
    def can_add(obj):
        return False


@register_component
class ColorGrading(ComponentBase):
    @staticmethod
    def encode(config, obj):
        # see https://bevyengine.org/news/bevy-0-10/#more-tonemapping-choices

        return BevyComponent(
            "bevy_render::view::ColorGrading", Struct(
                exposure=obj.bevy_camera_description.exposure,
                gamma=obj.bevy_camera_description.gamma,
                pre_saturation=obj.bevy_camera_description.pre_saturation,
                post_saturation=obj.bevy_camera_description.post_saturation,
            ))

    @staticmethod
    def is_present(obj):
        return obj.type == "CAMERA"

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass

    @staticmethod
    def can_add(obj):
        return False


@register_component
class Tonemapping(ComponentBase):
    @staticmethod
    def encode(config, obj):
        # see https://bevyengine.org/news/bevy-0-10/#more-tonemapping-choices
        return BevyComponent(
            "bevy_core_pipeline::tonemapping::Tonemapping", RawValue(obj.bevy_camera_description.tonemapping)
        )

    @staticmethod
    def is_present(obj):
        return obj.type == "CAMERA"

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass

    @staticmethod
    def can_add(obj):
        return False


@register_component
class CameraRenderGraph(ComponentBase):
    @staticmethod
    def encode(config, obj):
        # see https://bevyengine.org/news/bevy-0-10/#more-tonemapping-choices

        return BevyComponent(
            "bevy_render::camera::camera::CameraRenderGraph", Tuple("core_3d")
        )

    @staticmethod
    def is_present(obj):
        return obj.type == "CAMERA"

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass

    @staticmethod
    def can_add(obj):
        return False
