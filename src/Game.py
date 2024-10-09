from math import sin, cos, pi, sqrt
from random import randint, shuffle
from time import sleep
from typing import Optional

import pygame

from src.MeaninglessEntity import MeaninglessEntity as Me
from src.entities import Player, Wall, Enemy
from src.util.Geometry import Point, sub_point, mul_point


class Game:
    move_key = [pygame.K_d, pygame.K_s, pygame.K_a, pygame.K_w]
    shoot_key = [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]

    def __init__(self, size: tuple[int, int], fps: int):
        Me.init(self)
        pygame.init()

        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.unit = min(size) // 20
        self.fps = fps
        self.buttons: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        self.pos = (0, 0)
        self.shoot_queue = []

        while self.screen.get_width() == 0:
            sleep(0)
            continue
        pygame.display.set_caption("meaningless: shoot")

    def loop(self):
        player = Player.Player()
        self.put_wall(get_box_pattern(6), (0, 0))
        done = False

        while not done:
            # 프레임 시작
            self.clock.tick(self.fps)

            # 이벤트 검사
            for event in pygame.event.get():
                if event.type in [pygame.KEYDOWN, pygame.KEYUP]:  # 키 입력 이벤트
                    self.buttons = pygame.key.get_pressed()
                    for key in Game.shoot_key:
                        if self.buttons[key] and key not in self.shoot_queue:
                            self.shoot_queue.append(key)
                        if not self.buttons[key] and key in self.shoot_queue:
                            self.shoot_queue.remove(key)
                elif event.type == pygame.QUIT:  # 닫기 버튼을 누름
                    done = True

            # 나가는 키 입력
            if self.buttons[pygame.K_ESCAPE]:
                done = True

            # 벽 생성
            is_wall_generated = False
            if not randint(0, self.fps):
                p = randint(0, 12) // 10
                size = [randint(3, 7), randint(5, 10)][p]
                pattern = [get_snake_pattern, get_box_pattern][p](size)
                drct = self.get_mvdrct()
                if drct != (0, 0):
                    is_wall_generated = self.put_wall(
                        pattern,
                        tuple(
                            self.pos[i] + (self.screen.get_size()[i] / 2 + size * self.unit / 2) * drct[i]
                            for i in range(2)
                        )
                    )

            # 적 생성
            if not is_wall_generated and not randint(0, self.fps):
                r = randint(0, 7)
                self.put_enemy(
                    tuple(
                        self.pos[i] + (self.screen.get_size()[i] / 2 + self.unit) * round([cos, sin][i](pi * r / 4) * sqrt(2))
                        for i in range(2)
                    )
                )

            # 객체 업데이트
            Me.process()
            self.pos = player.pos

            # 화면 생성
            self.screen.fill((20, 20, 20))
            Me.blit((self.screen.get_width() // 2 - player.pos[0], self.screen.get_height() // 2 - player.pos[1]))
            pygame.display.flip()

    def get_mvdrct(self) -> Point:
        x, y = 0, 0
        for i, key in enumerate(Game.move_key):
            if self.buttons[key]:
                x += round(cos(i / 2 * pi))
                y += round(sin(i / 2 * pi))
        return x, y

    def get_shtdrct(self) -> Optional[int]:
        if self.shoot_queue:
            return Game.shoot_key.index(self.shoot_queue[0]) * 90
        else:
            return None

    def put_wall(self, pattern: list[list[bool]], center: Point) -> bool:
        size = (max(len(p) for p in pattern), len(pattern))
        topleft = sub_point(center, mul_point(size, self.unit / 2))
        if Me.get_collide_entity_by_rect(pygame.rect.Rect(*topleft, *mul_point(size, self.unit)), 'Wall', 'Enemy'):
            return False
        for i in range(len(pattern)):
            for j in range(len(pattern[i])):
                if pattern[i][j]:
                    Wall.Wall((self.unit / 2 + topleft[0] + self.unit * j, self.unit / 2 + topleft[1] + self.unit * i))
        return True

    def put_enemy(self, pos: Point) -> bool:
        rect = pygame.rect.Rect(0, 0, self.unit, self.unit)
        rect.center = pos
        if Me.get_collide_entity_by_rect(rect, 'Wall'):
            return False
        Enemy.Enemy(pos)
        return True


def get_snake_pattern(size: int) -> list[list[bool]]:
    m = [[False] * size for _ in range(size)]

    def dfs(pos: Point):
        x, y = pos
        m[x][y] = True
        nextpos = [[x + round(cos(t * pi / 2)), y + round(sin(t * pi / 2))] for t in range(4)]
        shuffle(nextpos)
        for dx, dy in nextpos:
            if 0 <= dx < size and 0 <= dy < size and not m[dx][dy] and len(
                list(
                    filter(
                        lambda p: 0 <= p[0] < size and 0 <= p[1] < size and m[p[0]][p[1]],
                        [[dx + round(cos(t * pi / 2)), dy + round(sin(t * pi / 2))] for t in range(4)]
                    )
                )
            ) <= 1 and randint(0, 2):
                dfs((dx, dy))
                break

    dfs((size // 2, size // 2))
    return m


def get_box_pattern(size: int) -> list[list[bool]]:
    m = [[False] * size for _ in range(size)]
    for t, dx, dy in [[(size - 1) * (i // 2), round(cos(i * pi / 2)), round(sin(i * pi / 2))] for i in range(4)]:
        for x, y in [[t + dx * i, t + dy * i] for i in range(size)]:
            m[x][y] = True
    return m
