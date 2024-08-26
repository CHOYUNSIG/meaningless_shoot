from random import randint

import pygame
from typing_extensions import override

from src.MeaninglessEntity import MeaninglessEntity as Me
from src.entities.Particle import Particle
from src.util.Geometry import mul_point, sub_point, dist


class Enemy(Me):
    image = pygame.image.load('res/image/player.png')
    velocity = 5  # unit per second
    particle_amount = (8, 12)

    def __init__(self, pos: tuple[float or int, float or int]):
        super().__init__(
            pygame.transform.scale(Enemy.image, (Me.session.unit, Me.session.unit)),
            pos,
            1
        )

    @override
    def kill(self):
        super().kill()

    @override
    def move(self):
        to_player = sub_point(Me.session.pos, self.pos)
        if dist((0, 0), to_player) < Me.session.unit:
            return
        unit = Me.session.unit * Enemy.velocity / Me.session.fps
        self.move_with_collision_safety(mul_point(to_player, unit / dist((0, 0), to_player)), 'Wall')

    @override
    def update(self):
        if self.get_collide_entity('Bullet'):
            for _ in range(randint(*Enemy.particle_amount)):
                Particle(self.pos, Enemy.image)
            self.kill()
