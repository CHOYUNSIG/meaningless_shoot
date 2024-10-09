from math import pi, cos, sin
from random import random
from time import perf_counter
from typing import Callable

import pygame
from typing_extensions import override

from src.MeaninglessEntity import MeaninglessEntity as Me
from src.util.Geometry import Point


class Particle(Me):
    get_distance: Callable[[], float] = lambda: random() * 2 + 1  # unit
    get_lifetime: Callable[[], float] = lambda: random() * 0.3 + 0.2  # second

    def __init__(self, pos: Point, image: pygame.Surface):
        self.size = round(Me.session.unit / 2 * (random() * 0.5 + 0.5))
        super().__init__(
            pygame.transform.scale(image, (self.size, self.size)),
            pos,
            0
        )
        self.generated_time = perf_counter()
        self.distance = Particle.get_distance()
        self.lifetime = Particle.get_lifetime()
        self.angle = random() * 2 * pi  # rad
        self.f = lambda x: x * (2 * self.lifetime - x) / self.lifetime ** 2

    @override
    def move(self):
        t = perf_counter() - self.generated_time
        dt = 1 / Me.session.fps
        y = self.f(t)
        dy = self.f(t + dt) - y
        unit = self.distance * Me.session.unit * dy
        size = self.size * (1 - y)
        self.pos = (self.pos[0] + unit * cos(self.angle), self.pos[1] + unit * sin(self.angle))
        self.image = pygame.transform.scale(self.image, (size, size))

    @override
    def update(self):
        if self.get_collide_entity('Wall', 'Player', 'Enemy') or perf_counter() - self.generated_time > self.lifetime:
            self.kill()
