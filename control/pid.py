#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np


class Pid:
    def __init__(self, p_gain, i_gain, d_gain, sampling_time):
        self.p_gain = p_gain
        self.i_gain = i_gain
        self.d_gain = d_gain
        self.sampling_time = sampling_time

        self.previous_error = 0
        self.integral_error = 0

    def get_output(self, target_value, current_value):
        error = target_value-current_value
        self.integral_error += error*self.sampling_time
        derivative_error = (error-self.previous_error)/self.sampling_time

        output = self.p_gain*error + self.i_gain*self.integral_error + self.d_gain*derivative_error
        self.previous_error = error
        return output
