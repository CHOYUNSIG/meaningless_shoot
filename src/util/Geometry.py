import math
from math import sqrt, acos, pi

number = float | int
Point = tuple[number, number]


def round_point(p: Point) -> Point:
    return round(p[0]), round(p[1])


def copysign(absolute: number, sign: number) -> number:
    if sign == 0:
        return 0
    return math.copysign(absolute, sign)


def add_point(a: Point, b: Point) -> Point:
    return a[0] + b[0], a[1] + b[1]


def sub_point(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1]


def mul_point(p: Point, v: number) -> Point:
    return p[0] * v, p[1] * v


def inner_product(a: Point, b: Point) -> number:
    return a[0] * b[0] + a[1] * b[1]


def dist(a: Point, b: Point) -> number:
    return sqrt(sum((a[i] - b[i]) ** 2 for i in range(2)))


def line_dist(p: Point, line_a: Point, line_b: Point) -> number:
    return area(p, line_a, line_b) * 2 / dist(line_a, line_b)


def diagonal_formula(*points: Point) -> number:
    left, right = [sum(points[i][0] * points[(i + j) % len(points)][1] for i in range(len(points))) for j in [1, len(points) - 1]]
    return left - right


def area(*points: Point) -> number:
    return abs(diagonal_formula(*points)) / 2


def ccw_point(a: Point, b: Point, c: Point) -> int:
    d = diagonal_formula(a, b, c)
    return round(copysign(1, d))


def ccw_vector(p: Point, q: Point) -> int:
    return ccw_point((0, 0), p, (p[0] + q[0], p[1] + q[1]))


def angle_point(a: Point, b: Point, c: Point) -> number:
    ba = sub_point(a, b)
    bc = sub_point(c, b)
    try:
        return acos(inner_product(ba, bc) / (dist((0, 0), ba) * dist((0, 0), bc)))
    except ZeroDivisionError:
        return pi / 2
    except ValueError:
        return 0