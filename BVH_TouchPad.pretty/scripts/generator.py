import math
import numpy as np
import matplotlib.pyplot as plt

def plot_coordinates(d):
    xs = [x[0] for x in d]
    ys = [x[1] for x in d]

    # plt.gca().invert_yaxis()
    plt.gca().set_aspect('equal')
    
    plt.plot(xs, ys)
    # plt.show()

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

# Top and bottom-most pads are effectively "half pads" since they would not interpolate into anything else.
# Thus for the intent of calculation, we treat the slider as having one fewer pads than it actually does.
# This includes clearance areas
standard_pad_length_full = target_length / (target_pads - 1) # Full length, counting clearance.  Copper does not extend this far.
standard_pad_length_copper = standard_pad_length_full - target_length_clearance # Half clearance at either end.  Copper area.

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

print(f'Interpolation fingers: {interpolation_finger_length} x {interpolation_finger_width}, including clearances')
print(f'Interpolation dead zone: {target_interpolation_deadzone}')

interpolation_finger_coordinates = np.array([])

# Calculate the fingers without any clearance
for i in range(0, target_interpolation_fingers + 1):
    ideal_x = (i * interpolation_finger_width)
    
    #Starting Point
    interpolation_finger_coordinates = np.concatenate((interpolation_finger_coordinates, [i * 1, 1.0]))

    if i < target_interpolation_fingers:
        interpolation_finger_coordinates = np.concatenate((interpolation_finger_coordinates, [(i * 1) + 0.5, 0.0]))

interpolation_finger_coordinates = interpolation_finger_coordinates.reshape(-1, 2)

print(f'{interpolation_finger_coordinates}')

# Adjust to be correctly aligned in X and Y
interpolation_finger_coordinates = interpolation_finger_coordinates - [0, 1.0]

print(f'{interpolation_finger_coordinates}')

# Adjust the fingers for correct lengths
interpolation_finger_coordinates = interpolation_finger_coordinates * [interpolation_finger_width, interpolation_finger_length]

from kiutils.footprint import Footprint, Pad, PadOptions
from kiutils.items.gritems import GrPoly

from kiutils.items.common import Position

def coordinates_to_position(coord):
    return Position(X = coord[0], Y = coord[1] * -1)

def generate_bottom_pad_coordinates(interpolation_finger_coordinates):
    pad_coordinates = np.array([])

    offset_finger_coordinates = interpolation_finger_coordinates + [0, target_interpolation_deadzone + interpolation_finger_length]

    initial_x = offset_finger_coordinates[0][0]
    final_x = offset_finger_coordinates[-1][0]

    pad_coordinates = np.append(pad_coordinates, [initial_x, target_length_clearance])
    pad_coordinates = np.append(pad_coordinates, offset_finger_coordinates)
    pad_coordinates = np.append(pad_coordinates, [final_x, target_length_clearance])
    pad_coordinates = np.append(pad_coordinates, [initial_x, target_length_clearance])

    pad_coordinates = pad_coordinates.reshape((-1, 2))

    pad_center_coordinates = [0, 0]

    return (pad_coordinates, pad_center_coordinates)

def generate_upper_pad_coordinates(interpolation_finger_coordinates):
    pad_coordinates = np.array([])

    offset_finger_coordinates = interpolation_finger_coordinates - [0, target_interpolation_deadzone]
    
    initial_x = offset_finger_coordinates[0][0]
    final_x = offset_finger_coordinates[-1][0]
        
    pad_coordinates = np.append(pad_coordinates, offset_finger_coordinates)
    
    pad_coordinates = np.append(pad_coordinates, [final_x, target_length_clearance])
    pad_coordinates = np.append(pad_coordinates, [initial_x, target_length_clearance])

    pad_coordinates = np.append(pad_coordinates, [offset_finger_coordinates[0]])

    pad_coordinates = pad_coordinates.reshape((-1, 2))

    pad_center_coordinates = [0, 0]

    return (pad_coordinates, pad_center_coordinates)
    
def generate_mid_pad_coordinates(interpolation_finger_coordinates):
    pad_coordinates = np.array([])

    offset_lower = interpolation_finger_coordinates - [0,  (target_interpolation_deadzone) / 2]
    offset_upper = interpolation_finger_coordinates + [0, interpolation_finger_length + (target_interpolation_deadzone) / 2]

    pad_coordinates = np.append(pad_coordinates, offset_lower)
    pad_coordinates = np.append(pad_coordinates, np.flip(offset_upper, 0))
    pad_coordinates = np.append(pad_coordinates, [offset_lower[0]])

    pad_coordinates = pad_coordinates.reshape((-1, 2))

    # pad_coordinates = pad_coordinates + [0, (target_interpolation_deadzone) / 2]

    pad_center_coordinates = [0, 0]

    return (pad_coordinates, pad_center_coordinates)

footprint_pads = []

mid_pad_offset = target_length / (target_pads - 1)

for i in range(0, target_pads):
    
    pad_position = None
    pad_size = None
    
    if i == 0:
        # Pad 1
        (pad_coordinates, pad_center_coordinates) = generate_bottom_pad_coordinates(interpolation_finger_coordinates)
    
        pad_center_coordinates = [0, -(target_length / 2)]
        pad_position = coordinates_to_position( pad_center_coordinates )
        pad_size = coordinates_to_position( (1, 1 ) )
    elif i == target_pads - 1:
        # Last Pad
        (pad_coordinates, pad_center_coordinates) = generate_upper_pad_coordinates(interpolation_finger_coordinates)        

        pad_center_coordinates = [0, (target_length / 2)]

        pad_position = coordinates_to_position( pad_center_coordinates )
        pad_size = coordinates_to_position( (1, 1 ) )
    else:
        # All other pads
        (pad_coordinates, pad_center_coordinates) = generate_mid_pad_coordinates(interpolation_finger_coordinates)

        pad_position = coordinates_to_position( pad_center_coordinates )
        pad_size = coordinates_to_position( (1, 1 ) )

    # Center the pad in X
    initial_x = interpolation_finger_coordinates[0][0]
    final_x = interpolation_finger_coordinates[-1][0]
    
    pad_coordinates = pad_coordinates - [(final_x - initial_x) / 2, 0]

    pad_positions = [coordinates_to_position(c) for c in pad_coordinates]
    
    pad_polygon = GrPoly( layer = 'F.Cu', coordinates = pad_positions, fill = 'solid')
    
    custom_pad_primatives = [pad_polygon]

    custom_pad_options = PadOptions( clearance="outline", anchor="rect")
    
    pad = Pad(number=f'{i + 2}', shape='custom', layers = ['F.Cu'], position = pad_position, size = pad_size, custom_pad_options=custom_pad_options, customPadPrimitives = custom_pad_primatives)
    
    footprint_pads += [pad]

    print(pad_position)
    print(pad_coordinates)
    
    pad_coordinates = pad_coordinates + [pad_center_coordinates[0], pad_center_coordinates[1]]
    print(pad_coordinates)
    plot_coordinates(pad_coordinates)

plt.show()



footprint = Footprint.create_new(library_file, 'smd')

footprint.pads = footprint_pads

print(footprint.to_sexpr())

footprint.to_file('~/project/kicad_library/BVH_TouchPadlibrary_file + '.kicad_mod')

