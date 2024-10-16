from time import perf_counter

import pygame
from typing_extensions import override

from src.MeaninglessEntity import MeaninglessEntity
from src.util.Geometry import Point


class FadeText(MeaninglessEntity):
    def __init__(self, text: str, size: int, color: tuple[int, int, int], pos: Point, fade_time: float):
        super().__init__(
            pygame.font.Font("res/font/OpenSans-Bold.ttf", size).render(text, True, color),
            pos,
            50,
        )
        self.fade_time = fade_time
        self.generated_time = perf_counter()

    @override
    def move(self):
        pass

    @override
    def update(self):
        alpha = int(255 * (1 - (perf_counter() - self.generated_time) / self.fade_time))
        if alpha < 0:
            self.kill()
        else:
            self.image.set_alpha(alpha)
