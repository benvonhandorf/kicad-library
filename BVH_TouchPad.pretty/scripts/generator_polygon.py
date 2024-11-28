import math
import numpy as np

from kiutils.footprint import Footprint, Pad, PadOptions
from kiutils.items.gritems import GrPoly

from kiutils.items.common import Position

from interpolation_finger import InterpolationFinger

#All units in mm
target_length = 100 # Overall length, including clearances and borders
target_width = 10 # Overall width, including clearances and borders
target_center = (0,0)
target_pads = 3
target_clearance = 1.0 # Orthoginal distance between adjacent interpolation fingers
target_interpolation_fingers = 3 # Number of interpolation fingers extending into the next pad
target_interpolation_deadzone = 10.0 # mm on each pad not subject to overlap with adjacent pads.  No interpolation may be possible.

target_length_clearance = 10 # Lengthwise offset of fingers to achieve target clearance

library = 'BVH_TouchPads'
library_file = f'TouchPad_Linear_{target_length}x{target_width}_{target_pads}'

# Interpolation Areas - Fingers
# Interpolation fingers are arbitrarily defined to be "internal" on the bottom and "external" on the top (positive Y direction) 
# of a pad.  External areas extend the full width of the footprint while internal areas are nested within the external areas of
# the next pad.
# The top-most pad only has internal fingers on the bottom and the bottom-most pad only has external finters on the top.
# We want the interpolation fingers to start.
# Finger definition starts beyond the interpolation offset.  Top and bottom pads have full interpolation offsets.
interpolation_finger_length = (target_length - (target_interpolation_deadzone * target_pads) - (target_length_clearance * (target_pads - 1))) / (target_pads - 1)
interpolation_finger_width = (target_width - (target_length_clearance * 2)) / target_interpolation_fingers
interpolation_finger_half_width = interpolation_finger_width / 2

interpolation_finger_generator = InterpolationFinger(width = interpolation_finger_width, length = interpolation_finger_length, radius = 2)

footprint_pads = []

# Bottom grounding pad
footprint_pads += [Pad(number='1', shape='rect', layers = ['B.Cu'], position = Position(X = 0, Y = 0), size = (target_width, target_length))]

for i in range(0, target_pads):
    pad_nodes = []

    for f in range(0, target_interpolation_fingers):
        x_offset = (f * interpolation_finger_width) - (target_width / 2)
        pad_nodes += interpolation_finger_generator.generate_finger_polygon(x_offset, 0, len(pad_nodes) == 0, True)

    pad_polygon = GrPoly( layer = 'F.Cu', coordinates = pad_nodes, fill = 'solid')
    
    pad_polygon.to_sexpr()
    
    custom_pad_primatives = [pad_polygon]

    custom_pad_options = PadOptions( clearance="outline", anchor="rect")

    pad_position = Position(X = 0, Y = 0)
    pad_size = Position(X = 1, Y = 1)
    
    pad = Pad(number=f'{i + 2}', shape='custom', layers = ['F.Cu'], position = pad_position, size = pad_size, customPadOptions=custom_pad_options, customPadPrimitives = custom_pad_primatives)

    pad.to_sexpr()
    
    footprint_pads += [pad]

footprint = Footprint.create_new(library_file, 'smd')

footprint.pads = footprint_pads
footprint.center = Position(X = 0, Y = 0)

print(footprint.to_sexpr())

footprint.to_file(library_file + '.kicad_mod')

