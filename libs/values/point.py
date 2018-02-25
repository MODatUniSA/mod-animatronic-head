""" Value object to hold point (x,y)
    Mostly just for readability
"""

class Point(dict):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tuple = (self.x, self.y)
        super().__init__()

    def cast_values_to_ints(self):
        self.x = int(self.x)
        self.y = int(self.y)
        return self
