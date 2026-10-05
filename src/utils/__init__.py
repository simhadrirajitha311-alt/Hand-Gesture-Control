"""General utility functions for geometry and smoothing."""

from .geometry import clamp, euclidean_distance, midpoint, normalized_point, point_angle
from .smoothing import ExponentialSmoother, MovingAverage

__all__ = [
    "ExponentialSmoother",
    "MovingAverage",
    "clamp",
    "euclidean_distance",
    "midpoint",
    "normalized_point",
    "point_angle",
]
