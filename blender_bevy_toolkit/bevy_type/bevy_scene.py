
from blender_bevy_toolkit.rust_types.ron import Base, encode


class Encodable(Base):
    def to_str(self, indent):
        return self.to_ron()


class BevyScene(Encodable):
    def __init__(self, entities=[]):
        self.entities = entities

    def add(self, entity):
        self.entities.append(entity)

    def to_ron(self):
        result = ["(", "  entities: {"]
        cpt = 0
        for v in self.entities:
            result.append(f"    {cpt}: {convert(v, 2)},")
            cpt += 1
        result.append("  }")
        result.append(")")
        return "\n".join(result)


class BevyEntity(Encodable):
    def __init__(self, components=[]):
        self.components = components

    def add(self, component):
        self.components.append(component)

    def to_ron(self):
        result = ["(", "  components: {"]
        for v in self.components:
            result.append(f"    {convert(v, 2)},")
        result.append("  }")
        result.append(")")
        return "\n".join(result)


class BevyComponent(Encodable):
    def __init__(self, struct, value=None, **props):
        self.struct = struct
        self.value = value
        self.props = props

    def to_ron(self):

        if self.value is not None:
            return f"\"{self.struct}\": {convert(self.value)}"
        result = [f"\"{self.struct}\": ("]
        for k, v in self.props.items():
            result.append(f"  {k}: {convert(v)},")
        result.append(")")
        return "\n".join(result)


class BevyComponentBundle(Encodable):
    def __init__(self, *components):
        self.components = components

    def to_ron(self):
        return ",\n".join(self.components)


class RawValue:
    def __init__(self,  value):
        self.value = value

    def to_ron(self):
        return self.value


class StructProp:
    def __init__(self,  *items, **props):
        self.items = items
        self.props = props

    def to_ron(self):
        result = [f"("]
        if self.items and len(self.items) != 0:
            # encoded = [encode(item) for item in self.items]
            result.append(",".join(self.items))

        for k in self.props:
            result.append(f"  {k}: {convert(self.props[k])},")
        result.append(")")
        return "\n".join(result)


class PrimitiveProp:
    def __init__(self, value):
        self.value = value

    def to_ron(self):
        if type(self.value) == str:
            return f"\"{self.value}\""
        return str(self.value)


class DebugProp:
    def __init__(self, value):
        self.value = value

    def to_ron(self):
        return str(self.value)

# REVIEW


class EnumProp:
    def __init__(self, option, *params, **props):
        self.option = option
        self.props = props
        self.params = params

    def to_ron(self):
        if self.props and len(self.props) == 0:
            return f"{self.option}"
        result = [f"{self.option}"]
        if len(self.params):
            result[0] = result[0]+"("
        if self.params and len(self.params) != 0:
            encoded = [str(item)
                       for item in self.params]  # replace str by encode
            result.append("  "+(",".join(encoded)))
        for k, v in self.props.items():
            result.append(f"  {k}: {convert(v)},")
        if len(self.params):
            result.append(")")
        return "\n".join(result)


def convert(value, indent=1):
    return encode(value, 1)


def add_indent(value, indent=1):
    if not indent:
        return value
    try:
        return str(value).replace("\n", "\n"+("  "*indent))
    except:
        return ""
