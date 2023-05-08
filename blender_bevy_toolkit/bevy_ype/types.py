

from multiprocessing import RawValue
from blender_bevy_toolkit.bevy_ype.bevy_scene import EnumProp, StructProp
from blender_bevy_toolkit.rust_types.ron import Tuple


def Vec3(*props, **propsObj):
    return StructProp(
        x=propsObj.get("x") or props[0] or 0,
        y=propsObj.get("y") or props[1] or 0,
        z=propsObj.get("z") or props[2] or 0
    )


def asVec3(position):
    return Vec3(*position)


def Vec2(*props, **propsObj):
    return StructProp(
        x=propsObj.get("x") or props[0] or 0,
        y=propsObj.get("y") or props[1] or 0,
    )


def asVec2(position):
    return Vec2(*position)


def Quat(*items, **props):
    return Tuple(
        props.get("x") or items[0] or 0,
        props.get("y") or items[1] or 0,
        props.get("z") or items[2] or 0,
        props.get("w") or items[3] or 0
    )


def asQuat(position):
    return Quat(*position)


def color_rgba(red: float, green: float, blue: float, alpha: float):
    return EnumProp("Rgba", red=red, green=green, blue=blue, alpha=alpha)


def color_rgb(red: float, green: float, blue: float):
    return color_rgba(red, green, blue, 1.0)


def asColor(color):
    return color_rgba(color.r, color.g, color.b, 1.0)


def asMatrix(matrix):
    return StructProp(
        x_axis=asVec3(matrix[0]),
        y_axis=asVec3(matrix[1]),
        z_axis=asVec3(matrix[2]),
    )
