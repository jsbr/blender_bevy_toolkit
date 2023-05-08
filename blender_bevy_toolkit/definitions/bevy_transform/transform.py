import mathutils
from blender_bevy_toolkit.bevy_ype.types import asQuat, asVec3
from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
    rust_types,
)
from blender_bevy_toolkit.bevy_ype.bevy_scene import BevyComponent

from bpy_extras.io_utils import axis_conversion


@register_component
class Transform(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component

        {
            "type": "bevy_transform::components::transform::Transform",
            "struct": {
                "translation": {
                    "type": "glam::vec3::Vec3",
                    "value": (0.0, 0.0, 0.0),
                },
                "rotation": {
                    "type": "glam::quat::Quat",
                    "value": (0.0, 0.0, 0.0, 1.0),
                },
                "scale": {
                    "type": "glam::vec3::Vec3",
                    "value": (1.0, 1.0, 1.0),
                },
        }
        """
        # axis_basis_change = mathutils.Matrix.Identity(4)
        # if export_settings['gltf_yup']:
        axis_basis_change = mathutils.Matrix(
            ((1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, -1.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0)))

        if obj.parent is None:
            transform = obj.matrix_world @ axis_basis_change
        else:
            transform = obj.matrix_local @ axis_basis_change

        position, rotation, scale = transform.decompose()
        s = mathutils.Vector((scale[0], scale[2], scale[1]))
        rot = mathutils.Quaternion(
            (rotation[0], rotation[1], rotation[3], -rotation[2]))
        p = mathutils.Vector((position[0], position[2], -position[1]))
        r = [rot[1], rot[2], rot[3], rot[0]]
        # s = scale
        # r = rotation
        # p = position

        return BevyComponent(
            "bevy_transform::components::transform::Transform",

            translation=asVec3(p),
            rotation=asQuat(r),
            scale=asVec3(s),
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return hasattr(obj, "matrix_world")

    def can_add(obj):
        return False

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass
