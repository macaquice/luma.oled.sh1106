#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Rotating 3D box wireframe & color dithering.

Adapted from:
http://codentronix.com/2011/05/12/rotating-3d-cube-using-python-and-pygame/
"""

import sys
import math
from operator import itemgetter
from demo_opts import get_device
from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator


def radians(degrees):
    return degrees * math.pi / 180


class point(object):

    def __init__(self, x, y, z):
        self.coords = (x, y, z)
        self.xy = (x, y)
        self.z = z

    def rotate_x(self, angle):
        x, y, z = self.coords
        rad = radians(angle)
        c = math.cos(rad)
        s = math.sin(rad)
        return point(x, y * c - z * s, y * s + z * c)

    def rotate_y(self, angle):
        x, y, z = self.coords
        rad = radians(angle)
        c = math.cos(rad)
        s = math.sin(rad)
        return point(z * s + x * c, y, z * c - x * s)

    def rotate_z(self, angle):
        x, y, z = self.coords
        rad = radians(angle)
        c = math.cos(rad)
        s = math.sin(rad)
        return point(x * c - y * s, x * s + y * c, z)

    def project(self, size, fov, viewer_distance):
        x, y, z = self.coords
        factor = fov / (viewer_distance + z)
        return point(x * factor + size[0] / 2, -y * factor + size[1] / 2, z)


def sine_wave(min, max, step=1):
    angle = 0
    diff = max - min
    diff2 = diff / 2
    offset = min + diff2
    while True:
        yield angle, offset + math.sin(radians(angle)) * diff2
        angle += step


def build_wireframe_sphere(segments=18, radius=1.0):
    vertices = []
    edges = []

    for lat_idx in range(segments):
        theta = math.pi * (lat_idx / (segments - 1) - 0.5)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        for lon_idx in range(segments):
            phi = 2 * math.pi * lon_idx / segments
            x = radius * cos_theta * math.cos(phi)
            y = radius * sin_theta
            z = radius * cos_theta * math.sin(phi)
            vertices.append(point(x, y, z))

    for lat_idx in range(segments):
        row_start = lat_idx * segments
        for lon_idx in range(segments):
            index = row_start + lon_idx

            if lat_idx < segments - 1:
                edges.append((index, index + segments))

            if lon_idx < segments - 1:
                edges.append((index, row_start + lon_idx + 1))
            else:
                edges.append((index, row_start))

    return vertices, edges


def main(num_iterations=sys.maxsize):

    regulator = framerate_regulator(fps=30)
    vertices, edges = build_wireframe_sphere(segments=18, radius=1.0)

    a, b, c = 0, 0, 0
    dist = 5

    for angle, _ in sine_wave(8, 40, 1.5):
        with regulator:
            num_iterations -= 1
            if num_iterations == 0:
                break

            # t = [v.rotate_x(a).rotate_y(b).rotate_z(c).project(device.size, 256, dist)
            t = [v.rotate_y(b).project(device.size, 256, dist)
                for v in vertices]

            with canvas(device, dither=True) as draw:
                for p1_idx, p2_idx in edges:
                    p1 = t[p1_idx]
                    p2 = t[p2_idx]
                    draw.line([int(p1.xy[0]), int(p1.xy[1]), int(p2.xy[0]), int(p2.xy[1])], fill="white")

            # a += 0.3
            b -= 1.1
            # c += 0.85


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
