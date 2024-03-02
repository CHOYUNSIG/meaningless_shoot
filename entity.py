import pygame
from abc import *
from time import perf_counter
from math import cos, sin, pi, sqrt
from random import random, randint
import game


class MeaninglessEntity(pygame.sprite.Sprite, metaclass=ABCMeta):
    session: 'game.Game' or None = None
    group: dict[str: pygame.sprite.Group] = {}
    dispose: set[pygame.sprite.Sprite] = set()

    @staticmethod
    def process():
        for callback in [
            lambda entity: entity.move(),
            lambda entity: entity.update()
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

    def __init__(self, image: pygame.image, pos: tuple[float or int, float or int], z_index: int):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (round(pos[0]), round(pos[1]))
        self.pos = tuple(pos)
        self.z_index = z_index
        if self.__class__.__name__ not in MeaninglessEntity.group:
            MeaninglessEntity.group[self.__class__.__name__] = pygame.sprite.Group()
        super().__init__(MeaninglessEntity.group[self.__class__.__name__])

    @abstractmethod
    def move(self):
        pass  # 이 메소드는 스프라이트의 배율과 좌표를 조절합니다.

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
    shoot_key = [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]
    move_key = [pygame.K_d, pygame.K_s, pygame.K_a, pygame.K_w]

    def __init__(self):
        super().__init__(
            pygame.transform.scale(Player.image, (MeaninglessEntity.session.unit, MeaninglessEntity.session.unit)),
            (MeaninglessEntity.session.screen.get_width() // 2, MeaninglessEntity.session.screen.get_height() // 2),
            100
        )
        self.reloaded = True
        self.shoot_time = perf_counter()
        self.shoot_queue = []

    def move(self):
        e = [0, 0]
        for i, key in enumerate(Player.move_key):
            if MeaninglessEntity.session.buttons[key]:
                e[0] += round(cos(i / 2 * pi))
                e[1] += round(sin(i / 2 * pi))
        if e == [0, 0]:
            return

        rect = self.get_rect()
        unit = round(Player.velocity * MeaninglessEntity.session.unit / sqrt(e[0] ** 2 + e[1] ** 2) / MeaninglessEntity.session.fps)
        if 'Wall' in MeaninglessEntity.group:
            wall = list(map(lambda x: x.get_rect(), MeaninglessEntity.group['Wall']))
            for _ in range(unit):
                for next_rect in [rect.move(e[0], 0), rect.move(0, e[1]), rect.move(*e)]:
                    if next_rect.collidelist(wall) == -1:
                        rect = next_rect
            self.pos = rect.center
        else:
            self.pos = (self.pos[0] + unit * e[0], self.pos[1] + unit * e[1])

    def update(self):
        # 총알 발사
        for key in Player.shoot_key:
            if MeaninglessEntity.session.buttons[key] and key not in self.shoot_queue:
                self.shoot_queue.append(key)
            if not MeaninglessEntity.session.buttons[key] and key in self.shoot_queue:
                self.shoot_queue.remove(key)
        if self.shoot_queue and perf_counter() - self.shoot_time > Player.reload_time:
            self.shoot_time = perf_counter()
            Bullet(self.pos, Player.shoot_key.index(self.shoot_queue[0]) * 90)


class Wall(MeaninglessEntity):
    image = pygame.image.load('meaningless_data/image/wall.png')
    particle_amount = (8, 12)

    def __init__(self, pos: tuple[int, int]):
        super().__init__(
            pygame.transform.scale(Wall.image, (MeaninglessEntity.session.unit, MeaninglessEntity.session.unit)),
            pos,
            2
        )

    def move(self):
        pass

    def update(self):
        if 'Bullet' in MeaninglessEntity.group and pygame.sprite.spritecollideany(self,
                                                                                  MeaninglessEntity.group['Bullet']):
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
                pygame.transform.scale(Bullet.image,
                                       (MeaninglessEntity.session.unit // 3, MeaninglessEntity.session.unit // 10)),
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
