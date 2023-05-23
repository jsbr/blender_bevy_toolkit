from blender_bevy_toolkit.bevy_type.bevy_scene import BevyComponent
from blender_bevy_toolkit.bevy_type.types import asVec3
from blender_bevy_toolkit.component_base import (
    ComponentBase,
    register_component,
    rust_types,
)
import bpy
import struct
import collections

# Used to define the different bounds. Each bound
# has a name (displayed in teh enum), a function
# that turns an object into bytes
# and draw_type defines how bounds are drawn in the viewport.
BoundsType = collections.namedtuple("BoundsType", ["name", "encoder", "draw_type"])


def encode_sphere_collider_data(obj):
    if obj.type == "EMPTY":
        radius = obj.empty_display_size
    elif obj.type == "MESH":
        radius = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z) / 2.0
    else:
        print("Unable to figure out radius for {}", obj.name)
        radius = 1.0

    return struct.pack("<f", radius)


def encode_capsule_collider_data(obj):
    if obj.type == "MESH":
        radius = max(obj.dimensions.x, obj.dimensions.y) / 2.0
        half_height = max(obj.dimensions.z - radius, 0.0) / 2.0
    else:
        print("Unable to figure out capsule dimensions for {}", obj.name)
        radius = 1.0
        half_height = 1.0
    return struct.pack("<ff", half_height, radius)


def encode_box_collider_data(obj):
    if obj.type == "MESH":
        dims = [obj.dimensions.x / 2.0, obj.dimensions.y / 2.0, obj.dimensions.z / 2.0]
    else:
        print("Unable to figure out box dimensions for {}", obj.name)
        dims = [1.0, 1.0, 1.0]
    return struct.pack("<fff", *dims)


# Physics shapes and a function to encode that shape provided an object
# Be cautious about inserting to the beginning/middle of this list or
# removing an item as it will break existing blend files.
COLLIDER_SHAPES = [
    BoundsType(name="Sphere", encoder=encode_sphere_collider_data, draw_type="SPHERE"),
    BoundsType(
        name="Capsule", encoder=encode_capsule_collider_data, draw_type="CAPSULE"
    ),
    BoundsType(name="Box", encoder=encode_box_collider_data, draw_type="BOX"),
    BoundsType(name="Mesh", encoder=encode_box_collider_data, draw_type="BOX"),
]


class ColliderComponenetRemove(bpy.types.Operator):
    bl_idname = "scene.remove_colider"
    bl_label = "X"

    def execute(self, context):
        ColliderDescription.remove(context.object)
        return {'FINISHED'}


@register_component
class ColliderDescription(ComponentBase):
    def encode(config, obj):
        """Returns a Component representing this component"""

        # The collider_data field is dependant on the collider_shape, so we have to do some
        # derivation here
        collider_shape = int(obj.rapier_collider_description.collider_shape)

        encode_function = COLLIDER_SHAPES[collider_shape].encoder
        raw_data = encode_function(obj)
        data = list(raw_data)

        field_dict = {}
        field_dict["collider_shape"] = collider_shape
        field_dict["size_x"] = obj.rapier_collider_description.size_x
        field_dict["size_y"] = obj.rapier_collider_description.size_y
        field_dict["size_z"] = obj.rapier_collider_description.size_z

        return BevyComponent("blender_bevy_toolkit::rapier_physics::ColliderDescription",
                             friction=rust_types.F32(obj.rapier_collider_description.friction),
                             restitution=rust_types.F32(obj.rapier_collider_description.restitution),
                             is_sensor=obj.rapier_collider_description.is_sensor,
                             centroid_translation=asVec3(obj.rapier_collider_description.translation),
                             density=rust_types.F32(obj.rapier_collider_description.density),
                             **field_dict
                             )

    def is_present(obj):
        """Returns true if the supplied object has this component"""
        return obj.rapier_collider_description.present or "colider" in obj.components.components

    def can_add(obj):
        return True

    @staticmethod
    def add(obj):
        obj.rapier_collider_description.present = True
        update_value(obj)
        obj.components.components += "colider,"
        update_draw_bounds(obj)

    @staticmethod
    def remove(obj):
        obj.rapier_collider_description.present = False
        obj.components.components = obj.components.components.replace("colider,", "")
        update_draw_bounds(obj)

    @staticmethod
    def register():
        bpy.utils.register_class(ColliderDescriptionPanel)
        bpy.utils.register_class(ColliderComponenetRemove)
        bpy.utils.register_class(ColliderDescriptionProperties)
        bpy.types.Object.rapier_collider_description = bpy.props.PointerProperty(
            type=ColliderDescriptionProperties
        )

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(ColliderDescriptionPanel)
        bpy.utils.unregister_class(ColliderComponenetRemove)
        bpy.utils.unregister_class(ColliderDescriptionProperties)
        del bpy.types.Object.rapier_collider_description


class ButtonOperator(bpy.types.Operator):
    bl_idname = "scene.button_operator"
    bl_label = "X"

    def execute(self, context):
        context.object.rapier_collider2_description.present = False
        return {'FINISHED'}


class ColliderDescriptionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_rapier_collider_description"
    bl_label = "ColliderDescription"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return ColliderDescription.is_present(context.object)

    def draw_header(self, context):
        self.layout.operator("scene.remove_colider")

    def draw(self, context):
        row = self.layout.row()
        row.label(
            text="A collider so this object can collide with things (when coupled with a rigidbody somewhere)"
        )

        fields = ["collider_shape", ["friction", "restitution"], ["is_sensor", "density"], "translation", "rotation"]

        for field in fields:
            if isinstance(field, list):
                row = self.layout.row()
                for f in field:
                    row.prop(context.object.rapier_collider_description, f)
            else:
                row = self.layout.row()
                row.prop(context.object.rapier_collider_description, field)

        obj = context.object
        collider_id = obj.rapier_collider_description.collider_shape

        box = self.layout.box()
        box.label(text='Size')
        row = box.row()
        if collider_id == "2":  # BOX
            row.prop(context.object.rapier_collider_description, "size_x", text="X")
            row = box.row()
            row.prop(context.object.rapier_collider_description, "size_y", text="Y")
            row = box.row()
            row.prop(context.object.rapier_collider_description, "size_z", text="Z")
        elif collider_id == "0":  # Sphere
            row.prop(context.object.rapier_collider_description, "size_x", text="Radius")
        elif collider_id == "1":  # Capsule
            row.prop(context.object.rapier_collider_description, "size_x", text="Height")
            row = box.row()
            row.prop(context.object.rapier_collider_description, "size_y", text="Width")


def update_draw_bounds(obj):
    """Changes how the object is shown in the viewport in order to
    display the bounds to the user"""
    if ColliderDescription.is_present(obj):
        collider_type_id = int(obj.rapier_collider_description.collider_shape)
        collider_type_data = COLLIDER_SHAPES[collider_type_id].draw_type

        obj.show_bounds = True
        obj.display_bounds_type = collider_type_data

    else:
        obj.show_bounds = False


def update_value(obj):
    collider_type_id = obj.rapier_collider_description.collider_shape
    if obj.type == "MESH":
        if collider_type_id == "0":
            obj.rapier_collider_description.size_x = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z) / 2.0
        elif collider_type_id == "1":
            radius = max(obj.dimensions.x, obj.dimensions.y) / 2.0
            half_height = max(obj.dimensions.z - radius, 0.0) / 2.0
            obj.rapier_collider_description.size_x = radius
            obj.rapier_collider_description.size_y = half_height
        elif collider_type_id == "2":
            obj.rapier_collider_description.size_x = obj.dimensions.x / 2.0
            obj.rapier_collider_description.size_y = obj.dimensions.y / 2.0
            obj.rapier_collider_description.size_z = obj.dimensions.z / 2.0

        for x, y, z in obj.bound_box:
            minx = min(minx, x)
            miny = min(miny, y)
            minz = min(minz, z)

            maxx = max(maxx, x)
            maxy = max(maxy, y)
            maxz = max(maxz, z)

        obj.rapier_collider_description.translation = [
            minx + (maxx - minx) / 2,
            miny + (maxy - miny) / 2,
            minz + (maxz - minz) / 2,
        ]


def collider_shape_changed(_, context):
    """Runs when the enum selecting the shape is changed"""
    update_draw_bounds(context.object)
    obj = context.object
    update_value(obj)


class ColliderDescriptionProperties(bpy.types.PropertyGroup):
    present: bpy.props.BoolProperty(name="Present", default=False)

    friction: bpy.props.FloatProperty(name="friction", default=0.5)
    restitution: bpy.props.FloatProperty(name="restitution", default=0.5)
    size_x: bpy.props.FloatProperty(name="size_x", default=0.0)
    size_y: bpy.props.FloatProperty(name="size_y", default=0.0)
    size_z: bpy.props.FloatProperty(name="size_z", default=0.0)
    is_sensor: bpy.props.BoolProperty(name="is_sensor", default=False)

    translation: bpy.props.FloatVectorProperty(name="translation", size=3)
    rotation: bpy.props.FloatVectorProperty(name="rotation", size=3)

    density: bpy.props.FloatProperty(name="density", default=0.5)

    shape_items = [(str(i), s.name, "") for i, s in enumerate(COLLIDER_SHAPES)]

    collider_shape: bpy.props.EnumProperty(
        name="collider_shape",
        default=0,
        items=shape_items,
        update=collider_shape_changed,
    )
