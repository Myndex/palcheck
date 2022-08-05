
def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def hex_to_rgb(hex):
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    return rgb

def luminance(r,g,b):
    srgb = get_srgb(r,g,b)
    r,g,b = get_rgb(srgb)
    return round(0.2126 * r + 0.7152 * g + 0.0722 * b, 3)

def get_srgb(r,g,b):
    return [float(v) / 255 for v in (r,g,b)]

def get_rgb(srgb):
    r_srgb = srgb[0]
    g_srgb = srgb[1]
    b_srgb = srgb[2]

    if r_srgb <= 0.03928:
        r = r_srgb/12.92
    else:
        r = ((r_srgb+0.055)/1.055) ** 2.4

    if g_srgb <= 0.03928:
        g = g_srgb/12.92
    else:
        g = ((g_srgb+0.055)/1.055) ** 2.4

    if b_srgb <= 0.03928:
        b = b_srgb/12.92
    else:
        b = ((b_srgb+0.055)/1.055) ** 2.4
    return r,g,b
