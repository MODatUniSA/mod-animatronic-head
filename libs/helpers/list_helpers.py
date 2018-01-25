""" Contains helper methods for list operations
"""

import collections

def flatten(in_list):
    """ Flattens an arbitrarily nested list. Generator, so call as list(flatten(in_list))
    """

    for entry in in_list:
        if isinstance(entry, collections.Iterable) and not isinstance(entry, (str, bytes)):
            yield from flatten(entry)
        else:
            yield entry
