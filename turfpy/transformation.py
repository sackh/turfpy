"""
This module implements some of the spatial analysis techniques and processes used to
understand the patterns and relationships of geographic features.
This is mainly inspired by turf.js.
link: http://turfjs.org/
"""
from typing import Union, Any

from geojson import Feature, Point, Polygon, MultiPolygon

from martinez.boolean import OperationType, compute

from turfpy.measurement import destination, area
from turfpy.meta import flatten_each



def circle(
    center: Point, radius: int, steps: int = 64, units: str = "km", **kwargs
) -> Polygon:
    """
    Takes a Point and calculates the circle polygon given a radius in degrees,
    radians, miles, or kilometers; and steps for precision.

    :param center: A `Point` object representing center point of circle.
    :param radius: An int representing radius of the circle.
    :param steps: An int representing number of steps.
    :param units: A string representing units of distance e.g. 'mi', 'km',
        'deg' and 'rad'.
    :param kwargs: A dict representing additional properties.
    :return: A polygon object.

    Example:

    >>> from turfpy import circle
    >>> circle(center=Point((-75.343, 39.984)), radius=5, steps=10)

    """
    coordinates = []
    options = dict(steps=steps, units=units)
    options.update(kwargs)
    for i in range(steps):
        bearing = i * -360 / radius
        pt = destination(center, radius, bearing, options=options)
        cords = pt.geometry.coordinates
        coordinates.append(cords)
    coordinates.append(coordinates[0])
    return Polygon(coordinates, **kwargs)


def polygon_difference(polygon1: Union[Polygon, MultiPolygon], polygon2: Union[Polygon, MultiPolygon]):
    """
    Finds the difference between two polygons by clipping the second polygon from the first.

    :param polygon1: A Polygon feature.
    :param polygon2: A Polygon feature.
    :return: A `Polygon` or `MultiPolygon` feature showing the area of polygon1 excluding
         the area of polygon2 (if empty returns null).
    """
    geom1 = polygon1
    geom2 = polygon2
    properties = {}
    geom1 = _remove_empty_polygon(geom1)
    geom2 = _remove_empty_polygon(geom2)
    if not geom1:
        return None
    if not geom2:
        return Feature(geom1, properties)
    differenced = compute(geom1, geom2, OperationType.DIFFERENCE)
    if len(differenced.contours) == 0:
        return None
    if len(differenced.contours) == 1:
        return Polygon(differenced.contours, properties)

    return MultiPolygon(differenced, properties)


def _remove_empty_polygon(geom: Union[Polygon, MultiPolygon]) -> Any:
    if geom.type == "Polygon":
        return geom if area(geom) > 1 else None
    elif geom.type == "MultiPolygon":
        coordinates = []

        def _flatten_each_callback(feature):
            if area(feature) > 1:
                coordinates.append(feature.geometry.coordinates)
        flatten_each(geom, _flatten_each_callback)
        if coordinates:
            return {"type": 'MultiPolygon', "coordinates": coordinates}


if __name__ == "__main__":
    p1 = Polygon([([128, -26], [141, -26], [141, -21], [128, -21], [128, -26])])
    p2 = Polygon([([126, -28], [140, -28], [140, -20], [126, -20], [126, -28])])
    diff = polygon_difference(p1, p2)
    print(diff)
