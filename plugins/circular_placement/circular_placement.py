from pcbnew import *
# import pcbnew
import wx
import wx.lib
import re
import math

def footprint_sort_key(footprint):
    return int(footprint.GetReference().strip("D"))

class CircularPlacementPlugin(ActionPlugin):
    def defaults(self):
        self.name = "Circular Footprint Placement"
        self.category = "Circular Utility"
        self.description = "Place a set of footprints in a circle around a location"

    def Run(self):
        footprint_pattern = re.compile("^D\d+$")

        origin = wxPoint(FromMM(150), FromMM(100))

        radius_mm = 15

        radius = FromMM(radius_mm)

        start_angle = 90

        start_rad = math.radians(start_angle)

        vertical_tangent_orientation_degrees = 90

        board = GetBoard()

        footprints = []

        for module in board.GetFootprints():
            if footprint_pattern.match(module.GetReference()):
                footprints.append(module)

        if not footprints:
            return

        footprints.sort(key=footprint_sort_key)

        segment_rad = (2 * math.pi) / len(footprints)
        segment_deg = 360 / len(footprints)

        for i in range(0, len(footprints)):
            footprint = footprints[i]

            rad = start_rad + (i * segment_rad)

            position = wxPoint(origin.x + (math.cos(rad) * radius), origin.y + (math.sin(rad) * radius))

            footprint.SetPosition(position)

            footprint.SetOrientationDegrees(vertical_tangent_orientation_degrees - (i * segment_deg))

        Refresh()

