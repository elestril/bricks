from bricks.point import Point


def test_construct_from_scalars_2d():
    p = Point(1, 2)
    assert p == [1.0, 2.0]
    assert p.z is None


def test_construct_from_scalars_3d():
    p = Point(1, 2, 3)
    assert p == [1.0, 2.0, 3.0]
    assert p.z == 3.0


def test_construct_from_iterables():
    p2 = Point([4, 5])
    p3 = Point((6, 7, 8))
    assert p2 == [4.0, 5.0]
    assert p2.z is None
    assert p3 == [6.0, 7.0, 8.0]


def test_setters_add_and_remove_z():
    p = Point(0, 0)
    p.z = 9
    assert p == [0.0, 0.0, 9.0]
    p.z = None
    assert p == [0.0, 0.0]
