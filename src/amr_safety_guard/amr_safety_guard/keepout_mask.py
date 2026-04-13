#!/usr/bin/env python3

import numpy as np
from PIL import Image

resolution = 0.05
origin_x = -9.975
origin_y = -10.092
width = 404
height = 402

#mask
mask = np.ones((height, width), dtype=np.uint8)*254

#Danger Zone
x_min_px = int((4.0-origin_x)/resolution)
x_max_px = int((8.0-origin_x)/resolution)
y_min_px = int((-3.0-origin_y)/resolution)
y_max_px = int((3.0-origin_y)/resolution)

#PGM row
row_min = height-y_min_px
row_max = height-y_max_px
mask[row_min:row_max, x_min_px:x_max_px] = 0 #black = keepout

img = Image.fromarray(mask)
img.save('/home/kaneki/amr_ws/src/amr_safety_guard/maps/keepout_mask.pgm')
print(f'Saved keepout_mask.pgm ({width}x{height})')
print(f'Danger zone pixels: x=[{x_min_px}:{x_max_px}], rows=[{row_min}:{row_max}]')
