#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..localization.point import Point


class ObjectInfo:
    def __init__(self, x, y, velocity, object_type, name=""):
        """Simulator 에서 얻어지는 object 정보를 담는 data class"""
        self.position = Point(x, y)
        self.velocity = velocity
        self.type = object_type  # 0: person / 1, 2: vehicle / 3: traffic light
        self.name = name

    def __str__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)
