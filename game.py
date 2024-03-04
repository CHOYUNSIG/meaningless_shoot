import pygame
import entity
from math import sin, cos, pi
from random import randint


class Game:
    move_key = [pygame.K_d, pygame.K_s, pygame.K_a, pygame.K_w]
    shoot_key = [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]

    def __init__(self, size: tuple[int, int], fps: int):
        entity.MeaninglessEntity.session = self

        pygame.init()
        pygame.display.set_caption("meaningless: shoot")

        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.unit = min(size) // 20
        self.fps = fps
        self.buttons: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        self.shoot_queue = []
        self.pos = (0, 0)

        while self.screen.get_width() == 0:
            continue

    def loop(self):
        player = entity.Player()
        entity.Wall((100, 0))
        entity.Wall((0, 100))
        entity.Wall((-100, 0))
        entity.Wall((0, -100))
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
            if not randint(0, self.fps):
                entity.Wall.generate()

            # 객체 업데이트
            entity.MeaninglessEntity.process()
            self.pos = player.pos

            # 화면 생성
            self.screen.fill((50, 50, 50))
            entity.MeaninglessEntity.blit(
                (self.screen.get_width() // 2 - player.pos[0], self.screen.get_height() // 2 - player.pos[1]))
            pygame.display.flip()

    def get_mvdrct(self) -> tuple[int, int]:
        x, y = 0, 0
        for i, key in enumerate(Game.move_key):
            if self.buttons[key]:
                x += round(cos(i / 2 * pi))
                y += round(sin(i / 2 * pi))
        return x, y

    def get_shtdrct(self) -> int or None:
        if self.shoot_queue:
            return Game.shoot_key.index(self.shoot_queue[0]) * 90
        else:
            return None
