from math import cos, pi, sin
from time import perf_counter
from typing_extensions import override

import pygame

from src.MeaninglessEntity import MeaninglessEntity as Me
from src.entities.FadeText import FadeText
from src.util.Geometry import Point


class Bullet(Me):
    image = pygame.image.load('res/image/bullet.png')
    velocity = 30  # unit per second
    remain_time = 1  # second

    def __init__(self, pos: Point, angle: float):
        super().__init__(
            pygame.transform.rotate(
                pygame.transform.scale(
                    Bullet.image,
                    (Me.session.unit // 3, Me.session.unit // 10)
                ),
                angle
            ),
            pos,
            1
        )
        self.angle = angle  # degree
        self.generated_time = perf_counter()
        self.kill_streak = 0

    @override
    def move(self):
        unit = Me.session.unit * Bullet.velocity / Me.session.fps
        self.pos = (self.pos[0] + unit * cos(self.angle * pi / 180), self.pos[1] + unit * sin(self.angle * pi / 180))

    @override
    def update(self):
        if self.get_collide_entity('Enemy'):
            score = 3 ** self.kill_streak
            FadeText(f"+{score}", Me.session.unit, (255, 0, 0), self.pos, 1.0)
            Me.session.score += score
            self.kill_streak += 1
        if self.get_collide_entity('Wall') or perf_counter() - self.generated_time > Bullet.remain_time:
            self.kill()
