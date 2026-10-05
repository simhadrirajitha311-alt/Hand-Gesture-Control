from __future__ import annotations

import numpy as np

from src.utils.geometry import euclidean_distance, midpoint, point_angle


def test_euclidean_distance():
    assert euclidean_distance((0, 0), (3, 4)) == 5.0


def test_midpoint():
    got = midpoint((0, 0), (10, 10))
    assert np.allclose(got, np.array([5.0, 5.0]))


def test_point_angle():
    a = np.array([0.0, 0.0])
    b = np.array([0.0, 1.0])
    c = np.array([1.0, 1.0])
    assert point_angle(a, b, c) > 0
