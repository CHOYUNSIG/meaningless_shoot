from math import sin, cos, pi, sqrt
from random import randint, shuffle
from time import sleep, perf_counter
from typing import Optional

import pygame

from src.MeaninglessEntity import MeaninglessEntity as Me
from src.entities import Player, Wall, Enemy
from src.util.Geometry import Point, sub_point, mul_point


class Game:
    move_key = [pygame.K_d, pygame.K_s, pygame.K_a, pygame.K_w]
    shoot_key = [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]
    inertia_intensity = 3  # unit
    inertia_speed = 3

    def __init__(self, size: tuple[int, int], fps: int):
        Me.init(self)
        pygame.init()

        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.unit = min(size) // 20
        self.fps = fps

        self.buttons = pygame.key.get_pressed()
        self.pos = (0, 0)
        self.shoot_queue = []

        self.pre_drct = (0, 0)
        self.pre_target_inertia = [0.0, 0.0]
        self.pre_inertia = (0.0, 0.0)
        self.inertia_changed_time = [0.0, 0.0]

        self.score = 0
        self.end_flag = False

        while self.screen.get_width() == 0:
            sleep(0)
            continue
        pygame.display.set_caption("meaningless: shoot")

    def reset(self):
        Me.reset()

        self.pos = (0, 0)
        self.shoot_queue = []

        self.pre_drct = (0, 0)
        self.pre_target_inertia = [0.0, 0.0]
        self.pre_inertia = (0.0, 0.0)
        self.inertia_changed_time = [0.0, 0.0]

        self.score = 0
        self.end_flag = False

    def loop(self):
        while True:
            self.reset()
            if self.__game_loop():
                break
            if self.__over_loop():
                break

    def __game_loop(self) -> bool:
        player = Player.Player()
        self.put_wall(get_box_pattern(6), (0, 0))

        while not self.end_flag:
            # 프레임 시작
            current_time = perf_counter()
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
                    return True

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
                            self.pos[i] + \
                            (self.screen.get_size()[i] / 2 + (size + Game.inertia_intensity) * self.unit / 2) * drct[i]
                            for i in range(2)
                        )
                    )

            # 적 생성
            if not is_wall_generated and not randint(0, self.fps):
                r = randint(0, 7)
                self.put_enemy(
                    tuple(
                        self.pos[i] + \
                        (self.screen.get_size()[i] / 2 + self.unit * Game.inertia_intensity) * \
                        round([cos, sin][i](pi * r / 4) * sqrt(2))
                        for i in range(2)
                    )
                )

            # 객체 업데이트
            Me.process()
            self.pos = player.pos

            # 뷰포트 관성 처리
            drct = self.get_mvdrct()
            for i in range(2):
                if drct[i] != self.pre_drct[i]:
                    self.inertia_changed_time[i] = current_time
                    self.pre_target_inertia[i] = self.pre_inertia[i]
            target_inertia = mul_point(drct, -self.unit * Game.inertia_intensity)
            inertia = tuple(
                self.pre_target_inertia[i] + \
                (target_inertia[i] - self.pre_target_inertia[i]) * \
                (1 - 1 / ((current_time - self.inertia_changed_time[i]) * Game.inertia_speed + 1))
                for i in range(2)
            )
            self.pre_drct = drct
            self.pre_inertia = inertia

            # 화면 생성
            self.screen.fill((20, 20, 20))
            Me.blit(tuple(self.screen.get_size()[i] // 2 - (self.pos[i] + inertia[i]) for i in range(2)))
            self.screen.blit(
                pygame.font.Font("res/font/OpenSans-Bold.ttf", self.unit)
                .render(f"Score: {self.score}", True, (255, 255, 255)),
                (0, 0),
            )
            pygame.display.flip()

        return False

    def __over_loop(self) -> bool:
        # 게임 오버 이후
        game_over_text = pygame.font.Font(
            "res/font/OpenSans-Bold.ttf",
            self.unit * 3
        ).render("Game Over", True, (127, 255, 127))
        self.screen.blit(
            game_over_text,
            sub_point(self.screen.get_rect().center, mul_point(game_over_text.get_size(), 0.5))
        )
        pygame.display.flip()

        while True:
            # 프레임 시작
            self.clock.tick(self.fps)

            # 이벤트 검사
            for event in pygame.event.get():
                if event.type in [pygame.KEYDOWN, pygame.KEYUP]:  # 키 입력 이벤트
                    self.buttons = pygame.key.get_pressed()
                elif event.type == pygame.QUIT:
                    return True

            if self.buttons[pygame.K_r]:
                return False

            if self.buttons[pygame.K_ESCAPE]:
                return True

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

    def game_over(self):
        self.end_flag = True


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
