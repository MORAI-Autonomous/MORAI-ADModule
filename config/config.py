#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import io
import pandas as pd
from ..localization.point import Point
from ..perception.object_info import ObjectInfo


class Config(object):
    _instance = None

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)

            with io.open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r', encoding='utf-8') as f:
                config = json.load(f)
                cls._instance.__dict__ = config

            cls._instance._set_map_data()
        return cls._instance

    def __getitem__(self, key):
        return getattr(self, key)

    def _set_map_data(self):
        path = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'map', self["map"]["name"], 'path.csv')
        )
        self["map"]["path"] = path.apply(
            lambda point: Point(point["x"], point["y"]), axis=1
        ).tolist()
        
        traffic_light_list = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'map', self["map"]["name"], 'traffic_light.csv')
        )
        self["map"]["traffic_light_list"] = traffic_light_list.apply(
            lambda traffic_light: ObjectInfo(**traffic_light.to_dict()), axis=1
        ).tolist()

    def update_config(self, file_name):
        with io.open(file_name, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.__dict__.update(config)
