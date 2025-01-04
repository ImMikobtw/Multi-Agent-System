import math

def get_distance(pos1, pos2):
    """Calculate the Euclidean distance between two points."""
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
