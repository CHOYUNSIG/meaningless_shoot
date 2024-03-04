import pygame
from abc import *
from time import perf_counter
from math import cos, sin, pi, sqrt
from random import random, randint, shuffle
import game


class MeaninglessEntity(pygame.sprite.Sprite, metaclass=ABCMeta):
    session: 'game.Game' or None = None
    group: dict[str: pygame.sprite.Group] = {}
    dispose: set[pygame.sprite.Sprite] = set()

    @staticmethod
    def process():
        for callback in [
            lambda e: e.move(),
            lambda e: e.update()
        ]:
            for group in list(MeaninglessEntity.group.values()):
                for entity in group:
                    callback(entity)
        for entity in MeaninglessEntity.dispose:
            for group in entity.groups():
                group.remove(entity)
            del entity

    @staticmethod
    def blit(offset: tuple[float or int, float or int]):
        z_group: dict[int: pygame.sprite.Group] = {}
        for group in MeaninglessEntity.group.values():
            for entity in group:
                entity.draw(offset, z_group)
        for z_index in sorted(z_group.keys()):
            z_group[z_index].draw(MeaninglessEntity.session.screen)

    def __init__(self, image: pygame.Surface, pos: tuple[float or int, float or int], z_index: int):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (round(pos[0]), round(pos[1]))
        self.pos = pos
        self.z_index = z_index
        if self.__class__.__name__ not in MeaninglessEntity.group:
            MeaninglessEntity.group[self.__class__.__name__] = pygame.sprite.Group()
        super().__init__(MeaninglessEntity.group[self.__class__.__name__])

    @abstractmethod
    def move(self):
        pass  # 이 메소드는 스프라이트의 pos, rect를 조절합니다.

    @abstractmethod
    def update(self):
        pass  # 이 메소드는 스프라이트의 나머지 상태를 조절합니다.

    def draw(self, offset: tuple[float or int, float or int], z_group: dict[int: pygame.sprite.Group]):
        self.rect.center = (round(self.pos[0] + offset[0]), round(self.pos[1] + offset[1]))
        if self.z_index not in z_group:
            z_group[self.z_index] = pygame.sprite.Group()
        z_group[self.z_index].add(self)

    def kill(self):
        MeaninglessEntity.dispose.add(self)

    def get_rect(self) -> pygame.rect.Rect:
        rect = self.rect.copy()
        rect.center = self.pos
        return rect


class Player(MeaninglessEntity):
    image = pygame.image.load('meaningless_data/image/player.png')
    velocity = 10  # unit per second
    reload_time = 0.3  # second

    def __init__(self):
        super().__init__(
            pygame.transform.scale(Player.image, (MeaninglessEntity.session.unit, MeaninglessEntity.session.unit)),
            (0, 0),
            100
        )
        self.reloaded = True
        self.shoot_time = perf_counter()
        self.shoot_queue = []

    def move(self):
        e = MeaninglessEntity.session.get_mvdrct()
        if e == (0, 0):
            return
        unit = round(
            Player.velocity * MeaninglessEntity.session.unit / sqrt(
                e[0] ** 2 + e[1] ** 2
            ) / MeaninglessEntity.session.fps
        )
        if 'Wall' in MeaninglessEntity.group:
            rect = self.get_rect()
            wall = list(map(lambda x: x.get_rect(), MeaninglessEntity.group['Wall']))
            for _ in range(unit):
                for next_rect in [rect.move(e[0], 0), rect.move(0, e[1]), rect.move(*e)]:
                    if next_rect.collidelist(wall) == -1:
                        rect = next_rect
            self.pos = rect.center
        else:
            self.pos = (self.pos[0] + unit * e[0], self.pos[1] + unit * e[1])

    def update(self):
        degree = MeaninglessEntity.session.get_shtdrct()
        if degree is not None and perf_counter() - self.shoot_time > Player.reload_time:
            self.shoot_time = perf_counter()
            Bullet(self.pos, degree)


class Wall(MeaninglessEntity):
    image = pygame.image.load('meaningless_data/image/wall.png')
    particle_amount = (8, 12)

    @staticmethod
    def pattern_snake(
            size: int or None = None,
            m: list[list[bool]] or None = None,
            x: int or None = None,
            y: int or None = None
    ) -> list[list[bool]]:
        if size is None:
            size = randint(1, 5)
        if m is None:
            m = [[False] * size for _ in range(size)]
            x = y = size // 2
        m[x][y] = True
        nextpos = [[x + round(cos(t * pi / 2)), y + round(sin(t * pi / 2))] for t in range(4)]
        shuffle(nextpos)
        for dx, dy in nextpos:
            if 0 <= dx < size and 0 <= dy < size and not m[dx][dy] and len(list(
                    filter(
                        lambda p: 0 <= p[0] < size and 0 <= p[1] < size and m[p[0]][p[1]],
                        [[dx + round(cos(t * pi / 2)), dy + round(sin(t * pi / 2))] for t in range(4)]
                    ))
            ) <= 1 and randint(0, 2):
                Wall.pattern_snake(size, m, dx, dy)
                break
        return m

    @staticmethod
    def pattern_box(size: int or None = None) -> list[list[bool]]:
        if size is None:
            size = randint(5, 10)
        m = [[False] * size for _ in range(size)]
        for t, dx, dy in [[(size - 1) * (i // 2), round(cos(i * pi / 2)), round(sin(i * pi / 2))] for i in range(4)]:
            for x, y in [[t + dx * i, t + dy * i] for i in range(size)]:
                m[x][y] = True
        return m

    @staticmethod
    def generate() -> bool:
        pattern = [Wall.pattern_snake, Wall.pattern_box][randint(0, 12) // 10]()
        dx, dy = MeaninglessEntity.session.get_mvdrct()
        if (dx, dy) == (0, 0):
            return False
        x, y = MeaninglessEntity.session.pos[0] + \
               (MeaninglessEntity.session.screen.get_width() // 2 + MeaninglessEntity.session.unit) * dx + \
               len(pattern) * MeaninglessEntity.session.unit * min(0, dx), \
               MeaninglessEntity.session.pos[1] + \
               (MeaninglessEntity.session.screen.get_height() // 2 + MeaninglessEntity.session.unit) * dy + \
               len(pattern) * MeaninglessEntity.session.unit * min(0, dy)
        if 'Wall' in MeaninglessEntity.group and pygame.rect.Rect(
                x,
                y,
                MeaninglessEntity.session.unit * len(pattern),
                MeaninglessEntity.session.unit * len(pattern)
        ).collidelist(list(map(lambda w: w.get_rect(), MeaninglessEntity.group['Wall']))) != -1:
            return False
        for i in range(len(pattern)):
            for j in range(len(pattern[i])):
                if pattern[i][j]:
                    Wall((x + MeaninglessEntity.session.unit * i, y + MeaninglessEntity.session.unit * j))
        return True

    def __init__(self, pos: tuple[int, int]):
        super().__init__(
            pygame.transform.scale(Wall.image, (MeaninglessEntity.session.unit, MeaninglessEntity.session.unit)),
            pos,
            2
        )

    def move(self):
        pass

    def update(self):
        if 'Bullet' in MeaninglessEntity.group and pygame.sprite.spritecollideany(
                self,
                MeaninglessEntity.group['Bullet']
        ):
            for _ in range(randint(*Wall.particle_amount)):
                Particle(self.pos)
            self.kill()


class Bullet(MeaninglessEntity):
    image = pygame.image.load('meaningless_data/image/bullet.png')
    velocity = 30  # unit per second
    remain_time = 1  # second

    def __init__(self, pos: tuple[int, int], angle: float):
        super().__init__(
            pygame.transform.rotate(
                pygame.transform.scale(
                    Bullet.image,
                    (MeaninglessEntity.session.unit // 3, MeaninglessEntity.session.unit // 10)
                ),
                angle
            ),
            pos,
            1
        )
        self.angle = angle  # degree
        self.generated_time = perf_counter()

    def move(self):
        unit = MeaninglessEntity.session.unit * Bullet.velocity / MeaninglessEntity.session.fps
        self.pos = (self.pos[0] + unit * cos(self.angle * pi / 180), self.pos[1] + unit * sin(self.angle * pi / 180))

    def update(self):
        if ('Wall' in MeaninglessEntity.group and pygame.sprite.spritecollideany(self, MeaninglessEntity.group['Wall'])) \
                or perf_counter() - self.generated_time > Bullet.remain_time:
            self.kill()


class Particle(MeaninglessEntity):
    image = pygame.image.load('meaningless_data/image/wall.png')
    distance = lambda: random() * 2 + 1  # unit
    lifetime = lambda: random() * 0.3 + 0.2  # second

    def __init__(self, pos: tuple[int, int]):
        self.size = round(MeaninglessEntity.session.unit / 2 * (random() * 0.5 + 0.5))
        super().__init__(
            pygame.transform.scale(Particle.image, (self.size, self.size)),
            pos,
            0
        )
        self.generated_time = perf_counter()
        self.distance = Particle.distance()
        self.lifetime = Particle.lifetime()
        self.angle = random() * 2 * pi  # rad
        self.f = lambda x: x * (2 * self.lifetime - x) / self.lifetime ** 2

    def move(self):
        t = perf_counter() - self.generated_time
        dt = 1 / MeaninglessEntity.session.fps
        y = self.f(t)
        dy = self.f(t + dt) - y
        unit = self.distance * MeaninglessEntity.session.unit * dy
        size = self.size * (1 - y)
        self.pos = (self.pos[0] + unit * cos(self.angle), self.pos[1] + unit * sin(self.angle))
        self.image = pygame.transform.scale(self.image, (size, size))

    def update(self):
        if ('Wall' in MeaninglessEntity.group and pygame.sprite.spritecollideany(self, MeaninglessEntity.group['Wall'])
                or perf_counter() - self.generated_time > self.lifetime):
            self.kill()
