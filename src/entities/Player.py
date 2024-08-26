from time import perf_counter

import pygame
from typing_extensions import override

from src.MeaninglessEntity import MeaninglessEntity as Me
from src.entities.Bullet import Bullet
from src.util.Geometry import mul_point, dist


class Player(Me):
    image = pygame.image.load('res/image/player.png')
    velocity = 10  # unit per second
    reload_time = 0.3  # second

    def __init__(self):
        super().__init__(
            pygame.transform.scale(Player.image, (Me.session.unit, Me.session.unit)),
            (0, 0),
            100
        )
        self.reloaded = True
        self.shoot_time = perf_counter()
        self.shoot_queue = []

    @override
    def move(self):
        e = Me.session.get_mvdrct()
        if e == (0, 0):
            return
        unit = Player.velocity * Me.session.unit / Me.session.fps
        self.move_with_collision_safety(mul_point(e, unit / dist((0, 0), e)), 'Wall')

    @override
    def update(self):
        degree = Me.session.get_shtdrct()
        if degree is not None and perf_counter() - self.shoot_time > Player.reload_time:
            self.shoot_time = perf_counter()
            Bullet(self.pos, degree)
