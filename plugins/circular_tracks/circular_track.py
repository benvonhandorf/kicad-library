from pcbnew import *
# import pcbnew
import wx
import wx.lib
import re
import math

class CircularTrackPlugin(ActionPlugin):
    def defaults(self):
        self.name = "Circular Track Creator"
        self.category = "Circular Utility"
        self.description = "Place a track at a specific radius approximating a circle"

    def Run(self):
        # Routing is clockwise for an incomplete circle
        start_angle = 91
        end_angle = 90

        base_radius_mm = 14

        segments = 64

        origin = wxPoint(FromMM(150), FromMM(100))

        # Route on the back
        track_layer_id = 31
        net_names = ["A",  "B", "C", "D", "E"]
        # net_names = ["/A_Col"]

        track_width_mm = 0.4
        track_spacing_mm = 0.5

        for i, net_name in enumerate(net_names):
            radius_mm = base_radius_mm + (i * (track_width_mm + track_spacing_mm))

            self.layout_track(origin, track_layer_id, net_name, start_angle, end_angle, segments, radius_mm, track_width_mm)

    def layout_track(self, origin, layer_id, net_name, start_angle, end_angle, segments, radius_mm, track_width_mm):

        radius = FromMils(radius_mm * 39.37)

        if start_angle > end_angle:
            end_angle += 360

        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        segment_rad = (end_rad - start_rad) / (segments - 1)

        board = GetBoard()

        net = board.GetNetsByName()[net_name]

        width = FromMM(track_width_mm)

        for i in range(1, segments):
            start_point_rad = start_rad + (segment_rad * (i - 1))
            start_point = wxPoint(origin.x + (math.cos(start_point_rad) * radius), origin.y + (math.sin(start_point_rad) * radius))

            end_point_rad = start_rad + (segment_rad * i)
            end_point = wxPoint(origin.x + (math.cos(end_point_rad) * radius), origin.y + (math.sin(end_point_rad) * radius))

            track_segment = TRACK(board)

            track_segment.SetStart(start_point)
            track_segment.SetEnd(end_point)
            track_segment.SetWidth(width)
            track_segment.SetLayer(layer_id)

            board.Add(track_segment)

            track_segment.SetNet(net)

        Refresh()

