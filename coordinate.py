import dataclasses
from dataclasses import dataclass

@dataclass
class Coordinate:
    x: int
    y: int

    def distance(self, other):
        px = (self.x - other.x) ** 2
        py = (self.y - other.y) ** 2
        return (px + py) ** 0.5

    def __iter__(self):
        return iter(dataclasses.astuple(self))

    def __str__(self):
        return "{x: %s, y: %s}" % (self.x, self.y)

    def __repr__(self):
        L = [self.x, self.y]
        s = "%s(%s)" % (self.__class__.__qualname__,
                        ", ".join(map(str, L)))

        return s

pos = Coordinate(14, 50)
