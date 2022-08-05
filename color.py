from relative_luminance import *

class ColorRL:

    def __init__(self, hex):
        self.id = id
        self.hex = hex
        # self.role = role
        # self.element = element

        self.rgb = hex_to_rgb(self.hex)
        self.relative_luminance = luminance(*self.rgb)
        self.is_background = False

    def __equals__(self, c2):
        return self.hex == c2.hex

    def __str__(self):
        return "%s\t%.2f" % (self.hex, self.relative_luminance)

    def blend(self, c2, a):
        bg = self.rgb
        fg = c2.rgb
        r = round((1-a)*fg[0]+a*bg[0])
        g = round((1-a)*fg[1]+a*bg[1])
        b = round((1-a)*fg[2]+a*bg[2])
        return rgb_to_hex((r,g,b))
