from blender_bevy_toolkit.component_base import (
    register_component,
    ComponentBase,
)
from blender_bevy_toolkit import rust_types
from blender_bevy_toolkit.bevy_type.bevy_scene import BevyComponent


@register_component
class Label(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component"""
        return BevyComponent(
            "blender_bevy_toolkit::blend_label::BlendLabel",
            name=rust_types.Str(obj.name),
        )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return hasattr(obj, "name")

    def can_add(obj):
        return False

    @staticmethod
    def register():
        pass

    @staticmethod
    def unregister():
        pass
