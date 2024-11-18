from kiutils.footprint import Footprint, Pad, PadOptions
from kiutils.items.gritems import GrPoly, GrArc

from kiutils.items.common import Position


class InterpolationFinger:
    def __init__(self, width, length, radius):
        self.width = width
        self.length = length
        self.radius = radius
    
    def generate_finger_polygon(self, x_offset, y_offset, include_initial_position, round_positive_end):
        shapes = []

        if include_initial_position:
            shapes += [Position(X = x_offset - (self.width / 2), Y = y_offset)]
        
        if round_positive_end:
            arc_start = Position(X = x_offset - self.radius, Y = y_offset + self.length - self.radius)
            arc_center = Position(X = x_offset, Y = y_offset + self.length)
            arc_end = Position(X = x_offset + self.radius, Y = y_offset + self.length - self.radius)
        else:
            shapes += [Position(X = x_offset, Y = y_offset + self.length)]

        shapes += [GrArc(start = arc_start, mid = arc_center, end = arc_end)]
        
        shapes += [Position(X = x_offset + (self.width / 2), Y = y_offset)]

        return shapes
        
