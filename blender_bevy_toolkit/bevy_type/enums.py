TONE_MAPPING = [
    ("None", "None", "Bypass tonemapping."),
    ("Reinhard", "Reinhard",
     "Suffers from lots hue shifting, brights don’t desaturate naturally. Bright primaries and secondaries don’t desaturate at all."),
    ("ReinhardLuminance", "Reinhard Luminance",
     "Current bevy default. Likely to change in the future. Suffers from hue shifting. Brights don’t desaturate much at all across the spectrum."),
    ("AcesFitted", "Aces Fitted",
     "Same base implementation that Godot 4.0 uses for Tonemap ACES. Not neutral, has a very specific aesthetic, intentional and dramatic hue shifting. Bright greens and reds turn orange. Bright blues turn magenta. Significantly increased contrast. Brights desaturate across the spectrum."),
    ("AgX", "AgX",
     "Very neutral. Image is somewhat desaturated when compared to other tonemappers. Little to no hue shifting"),
    ("SomewhatBoringDisplayTransform", "SomewhatBoringDisplayTransform",
     "Brights desaturate across the spectrum. Is sort of between Reinhard and ReinhardLuminance. Conceptually similar to reinhard-jodie. Designed as a compromise if you want e.g. decent skin tones in low light"),
    ("TonyMcMapface", "TonyMcMapface",
     "Very neutral. Subtle but intentional hue shifting. Brights desaturate across the spectrum."),
    ("BlenderFilmic", "Blender Filmic",
     "Default Filmic Display Transform from blender. Somewhat neutral. Suffers from hue shifting. Brights desaturate across the spectrum.")
]
