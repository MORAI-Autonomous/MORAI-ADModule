#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .localization.point import Point


class VehicleState:
    def __init__(self, x=0, y=0, yaw=0, velocity=0):
        self.position = Point(x, y)
        self.yaw = yaw
        self.velocity = velocity

    def __str__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)
