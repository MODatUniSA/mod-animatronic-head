""" Collection of math helper functions
"""

def lerp(start, end, percent_between):
    """ Return a point between start and end that is percent_between the two
    """

    if percent_between < 0:
        raise ValueError("Can't lerp to a negative percent ({})".format(percent_between))

    return (percent_between * end) + ((1-percent_between) * start)
