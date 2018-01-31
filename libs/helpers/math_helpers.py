""" Collection of math helper functions
"""

from libs.values.point import Point

def center_point_ints(x,y,w,h):
    """ Return the center point of the argument rect with all values cast to integers
    """

    return center_point(x,y,w,h).cast_values_to_ints()

def center_point(x,y,w,h):
    """ Return the center point of the argument rect
    """

    return inner_point((x,y,w,h), 0.5, 0.5)

def inner_point(rect, x_percent, y_percent):
    """ Return a point within the rectangle x% and y% along its area (% are 0.0 - 1.0)
    """

    x,y,w,h = rect
    x_val = int(lerp(x, x+w, x_percent))
    y_val = int(lerp(y, y+h, y_percent))
    return Point(x_val, y_val)

def lerp(start, end, percent_between):
    """ Return a point between start and end that is percent_between the two
    """

    if percent_between < 0:
        raise ValueError("Can't lerp to a negative percent ({})".format(percent_between))

    return (percent_between * end) + ((1-percent_between) * start)
