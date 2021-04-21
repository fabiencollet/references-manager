import math
import colorsys
import os

from PIL import ImageOps

try:
    import core
except ImportError:
    from . import core

# Globals
################################################################################

dict_hue = {
            "red":
                {"rgb": (255, 0, 0),
                 "id": 0},
            "orange":
                {"rgb": (255, 128, 0),
                 "id": 1},
            "yellow":
                {"rgb": (255, 255, 0),
                 "id": 2},
            "yellow_green":
                {"rgb": (128, 255, 0),
                 "id": 3},
            "green":
                {"rgb": (0, 255, 0),
                 "id": 4},
            "green_cyan":
                {"rgb": (0, 255, 128),
                 "id": 5},
            "cyan":
                {"rgb": (0, 255, 255),
                 "id": 6},
            "cyan_blue":
                {"rgb": (0, 128, 255),
                 "id": 7},
            "blue":
                {"rgb": (0, 0, 255),
                 "id": 8},
            "violet":
                {"rgb": (128, 0, 255),
                 "id": 9},
            "magenta":
                {"rgb": (255, 0, 255),
                 "id": 10},
            "pink":
                {"rgb": (255, 0, 128),
                 "id": 11},
           }

# Functions
################################################################################


def distanceBetweenColor(color1, color2):

    square_minus_r = math.pow((color1[0]-color2[0]), 2)
    square_minus_g = math.pow((color1[1]-color2[1]), 2)
    square_minus_b = math.pow((color1[2]-color2[2]), 2)

    total_square = square_minus_r + square_minus_g + square_minus_b

    result = math.sqrt(total_square)

    return result


def closestColorFromDict(pixel_color, dict_color):

    result_list = []

    for color in dict_color:

        rgb = dict_color[color]["rgb"]

        result_list.append((rgb, distanceBetweenColor(pixel_color, rgb)))

    closest = min(result_list, key=lambda x: x[1])

    return closest[0]


def getPictureInformations(url):

    # Return values
    ############################################################################

    hue = 12
    # saturation = 0.5
    # value = 0.5
    # brightness = 0.5
    grey_dominant = False

    # Globals
    ############################################################################

    max_size = 50

    ############################################################################

    image = core.openImage(url)

    if not image:
        list_values = [12, 0, 0, 0, 1, 1]
        return list_values

    current_size = image.size

    origin_width, origin_height = current_size
    width_ratio = round(origin_width / origin_height, 3)
    height_ratio = round(origin_height / origin_width, 3)

    if current_size[0] > current_size[1]:
        bigger_size = current_size[0]
    else:
        bigger_size = current_size[1]

    ratio = bigger_size / max_size

    new_size = (int(current_size[0] / ratio),
                int(current_size[1] / ratio))

    width = new_size[0]
    height = new_size[1]

    # Resize image
    image_resize = image.resize(new_size, resample=0, box=None)

    total_pixel = width * height

    # applying grayscale method
    grey_image = ImageOps.grayscale(image_resize)

    dict_count_hue = {}

    # HUE
    ############################################################################

    total_grey_pixel = 0
    total_hue_pixel = 0

    total_saturation = 0
    total_value = 0

    for x in range(width):
        for y in range(height):

            color = image_resize.getpixel((x, y))
            if isinstance(color, int):
                total_grey_pixel += 1
                continue
            grey = grey_image.getpixel((x, y))

            if distanceBetweenColor(color, (grey, grey, grey)) < 15:
                total_grey_pixel += 1
                continue

            total_hue_pixel += 1

            closest_hue = closestColorFromDict(color, dict_hue)

            if closest_hue not in dict_count_hue.keys():
                value = 1
            else:
                value = dict_count_hue[closest_hue]["count"] + 1

            dict_count_hue[closest_hue] = {"count": value}

            image_resize.putpixel((x, y), closest_hue)

            # Saturation
            r, g, b = color
            h, s, v = colorsys.rgb_to_hsv(r, g, b)

            total_saturation += s
            total_value += v / 255

    if total_hue_pixel <= int(total_pixel*0.05):
        grey_dominant = True

    # GREY
    ############################################################################

    grey_total = 0

    for x in range(width):
        for y in range(height):
            grey_total += grey_image.getpixel((x, y))

    brightness = round((grey_total / total_pixel) / 255.0, 1)

    if grey_dominant:

        saturation = 0
        value = brightness

        list_values = [hue,
                       saturation,
                       value,
                       brightness,
                       width_ratio,
                       height_ratio]
        return list_values

    # Hue
    list_count_colors = []

    for key in dict_count_hue.keys():
        list_count_colors.append((key, dict_count_hue[key]["count"]))

    main_hue = max(list_count_colors, key=lambda x: x[1])[0]

    for color in dict_hue:
        if dict_hue[color]["rgb"] == main_hue:
            hue = dict_hue[color]["id"]
            break

    saturation = round(total_saturation/total_hue_pixel, 1)
    value = round(total_value / total_hue_pixel, 1)

    list_values = [hue,
                   saturation,
                   value,
                   brightness,
                   width_ratio,
                   height_ratio]

    return list_values
