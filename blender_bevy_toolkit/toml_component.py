import os
import bpy
from bpy.app.handlers import persistent
import sys
# temp toml don't exist in 3.10, but was a default lib in 3.11
from blender_bevy_toolkit import toml
from .component_constructor import (
    ComponentDefinition,
    FieldDefinition,
    component_from_def,
    ComponentDefinitionToml
)
from .component_base import register_component


@persistent
def find_component():
    print(sys.version_info)
    print("find_component")
    directory = ""
    try:
        directory = bpy.path.abspath("//")[:-1]
    except:
        print("path not found")
    if not directory:
        return
    print("directory:" + directory)
    folders = directory.split(os.sep)  # not work on windows
    while len(folders):
        test = folders + ["components.toml"]
        file_path = "/" + os.path.join(*test)
        print("f: " + file_path)
        if os.path.exists(file_path):
            load_compoent(file_path)
        folders.pop()

    # filepath = bpy.data.filepath
    # directory = os.path.dirname(filepath)
    # print(directory)


# Map from JSON strings to blender property types
PYTHON_TYPE_PROPERTIES = {
    str: "string",
    int: "int",
    float: "f32",
    bool: "bool",
}


def parse_field(name, field):
    """Convert the json definition of a single field into something static"""
    value = field.get("default") or field["value"]
    type_ = field.get("type") or PYTHON_TYPE_PROPERTIES.get(type(value))
    return FieldDefinition(
        field=field.get("field") or field.get("name") or name,
        type=type_,
        default=value,
        description=field.get("description") or "",
    )


def construct_component_classes(name: str, component):
    """Parse the file from JSON into some python namedtuples"""

    component_def = ComponentDefinitionToml(
        name=component.get("name") or name,
        description=component.get("description") or "",
        id=component.get("id") or name,
        struct=component.get("struct"),
        fields=[parse_field(k, f) for k, f in component["fields"].items()],
        target=component.get("target")
    )

    return component_from_def(component_def)


def load_compoent(path):
    print("found:" + path)

    data = toml.load(path)
    print("data:" + str(data))
    component_class = construct_component_classes("TDCamera", data["TDCamera"])
    print("### register_component")
    register_component(component_class)
