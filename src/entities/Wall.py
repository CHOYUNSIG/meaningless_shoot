from math import cos, pi, sin
from random import randint, shuffle

import pygame
from typing_extensions import override

from src.MeaninglessEntity import MeaninglessEntity as Me
from src.entities.Particle import Particle


class Wall(Me):
    image = pygame.image.load('res/image/wall.png')
    particle_amount = (8, 12)

    def __init__(self, pos: tuple[int, int]):
        super().__init__(
            pygame.transform.scale(Wall.image, (Me.session.unit, Me.session.unit)),
            pos,
            2
        )

    @override
    def move(self):
        pass

    @override
    def update(self):
        if self.get_collide_entity('Bullet'):
            for _ in range(randint(*Wall.particle_amount)):
                Particle(self.pos, Wall.image)
            self.kill()
