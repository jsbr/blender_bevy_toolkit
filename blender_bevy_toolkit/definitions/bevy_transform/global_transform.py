from blender_bevy_toolkit.bevy_ype.types import Vec3, asQuat, asVec3, asMatrix
from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
    rust_types,
)
from bpy_extras.io_utils import axis_conversion
from blender_bevy_toolkit.bevy_ype.bevy_scene import BevyComponent, StructProp
from blender_bevy_toolkit.rust_types.ron import Struct, Tuple


@register_component
class GlobalTransform(ComponentBase):

    @staticmethod
    def encode(config, obj):
        transform = obj.matrix_world

        position, rotation, scale = transform.decompose()
        global_matrix = axis_conversion(from_forward="-Z",
                                        from_up="Y",
                                        ).to_4x4()
        return BevyComponent(
            "bevy_transform::components::global_transform::GlobalTransform",
            Tuple(Struct(
                # matrix3=asMatrix(obj.matrix_world),
                matrix3=asMatrix(global_matrix),
                translation=Vec3(0, 0, 0),
            ))
        )

    @staticmethod
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
