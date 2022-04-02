#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

def minimum_bounding_rectangle(points):
    # https://stackoverflow.com/questions/13542855/algorithm-to-find-the-minimum-area-rectangle-for-given-points-in-order-to-comput/33619018#33619018
    """
    Find the smallest bounding rectangle for a set of points.
    Returns a set of points representing the corners of the bounding box.

    :param points: an nx2 matrix of coordinates
    :rval: an nx2 matrix of coordinates
    """
    pi2 = np.pi/2.
    
    # 2차원배열만됨
    # x,y 중복되면 안됨
    # get the convex hull for the points

    hull_points = points
    # hull_points = points[ConvexHull(points).vertices]

    cut_points = []
    
    for point in hull_points:
        if len(point) > 2:
            cut_points.append(np.array([point[0],point[1]]))
        else:       
            cut_points.append(point)
    
    cut_points = np.array(cut_points)

    # calculate edge angles
    edges = np.zeros((len(cut_points)-1, 2))
    edges = cut_points[1:] - cut_points[:-1]

    angles = np.zeros((len(edges)))
    angles = np.arctan2(edges[:, 1], edges[:, 0])

    angles = np.abs(np.mod(angles, pi2))
    angles = np.unique(angles)

    # find rotation matrices
    # XXX both work
    rotations = np.vstack([
        np.cos(angles),
        np.cos(angles-pi2),
        np.cos(angles+pi2),
        np.cos(angles)]).T
    rotations = rotations.reshape((-1, 2, 2))

    # apply rotations to the hull
    rot_points = np.dot(rotations, cut_points.T)

    # find the bounding points
    min_x = np.nanmin(rot_points[:, 0], axis=1)
    max_x = np.nanmax(rot_points[:, 0], axis=1)
    min_y = np.nanmin(rot_points[:, 1], axis=1)
    max_y = np.nanmax(rot_points[:, 1], axis=1)

    # find the box with the best area
    areas = (max_x - min_x) * (max_y - min_y)
    best_idx = np.argmin(areas)

    # return the best box
    x1 = max_x[best_idx]
    x2 = min_x[best_idx]
    y1 = max_y[best_idx]
    y2 = min_y[best_idx]
    r = rotations[best_idx]

    rval = np.zeros((4, 2))
    rval[0] = np.dot([x1, y2], r)
    rval[1] = np.dot([x2, y2], r)
    rval[2] = np.dot([x2, y1], r)
    rval[3] = np.dot([x1, y1], r)

    returnValue = np.zeros((4,3))
    i = 0
    for value in rval:
        result = []
        for point in hull_points:
            result.append((((value[0] - point[0] )**2) + ((value[1]-point[1])**2) )**0.5)
        minindex = np.argmin(np.array(result))
        
        returnValue[i]= np.array([value[0], value[1], hull_points[minindex][2]])
       
        i = i+1
        
    return returnValue

def calculate_centroid(points):
    sx = sy= sz = sL = 0
    for i in range(len(points)):
        x0, y0, z0 = points[i - 1]     # in Python points[-1] is last element of points
        x1, y1, z1 = points[i]
        L = ((x1 - x0)**2 + (y1 - y0)**2 + (z1-z0)**2) ** 0.5
        sx += (x0 + x1)/2 * L
        sy += (y0 + y1)/2 * L
        sz += (z0 + z1)/2 * L
        sL += L
        
    centroid_x = sx / sL
    centroid_y = sy / sL
    centroid_z = sz / sL

    return np.array([centroid_x,centroid_y, centroid_z])
