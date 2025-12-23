from collections.abc import Iterable


class Point(list):
    """A point represented as a list of two or three floats."""

    def __init__(self, x: float | Iterable[float], y: float | None = None, z: float | None = None):
        if y is None and not isinstance(x, (int, float)):
            vals = list(x)  # type: ignore[arg-type]
            if len(vals) not in (2, 3):
                raise TypeError("Point iterable must contain two or three numbers")
            xi, yi = vals[0], vals[1]
            zi = vals[2] if len(vals) == 3 else None
        else:
            if y is None:
                raise TypeError("Point requires both x and y when not initialized from an iterable")
            xi, yi = x, y
            zi = z

        coords = [float(xi), float(yi)]
        if zi is not None:
            coords.append(float(zi))

        super().__init__(coords)

    @property
    def x(self) -> float:
        return self[0]

    @x.setter
    def x(self, value: float) -> None:
        self[0] = float(value)

    @property
    def y(self) -> float:
        return self[1]

    @y.setter
    def y(self, value: float) -> None:
        self[1] = float(value)

    @property
    def z(self) -> float | None:
        return self[2] if len(self) > 2 else None

    @z.setter
    def z(self, value: float | None) -> None:
        if value is None:
            if len(self) > 2:
                self.pop()
            return

        if len(self) > 2:
            self[2] = float(value)
        else:
            self.append(float(value))