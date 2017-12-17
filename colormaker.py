import webcolors

# Return [w, r, g, b] by giving a color name
def name2wrgb(color):
    l_color = color.lower()
    if l_color == 'white':
        return [255, 0, 0, 0]
    else:
        return [0] + list(webcolors.name_to_rgb(color))