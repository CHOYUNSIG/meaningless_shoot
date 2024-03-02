import pygame
import entity


class Game:
    def __init__(self, size: tuple[int, int], fps: int):
        entity.MeaninglessEntity.session = self

        pygame.init()
        pygame.display.set_caption("meaningless: shoot")

        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.unit = min(size) // 20
        self.fps = fps
        self.buttons: pygame.key.ScancodeWrapper = pygame.key.get_pressed()

        while self.screen.get_width() == 0:
            continue

    def loop(self):
        player = entity.Player()
        entity.Wall((-100, 0))
        entity.Wall((100, 100))
        entity.Wall((200, 0))
        entity.Wall((20, 300))

        done = False

        while not done:
            # 프레임 시작
            self.clock.tick(self.fps)

            # 이벤트 검사
            for event in pygame.event.get():
                if event.type in [pygame.KEYDOWN, pygame.KEYUP]:  # 키 입력 이벤트
                    self.buttons = pygame.key.get_pressed()
                elif event.type == pygame.QUIT:
                    done = True

            # 나가는 키 입력
            if self.buttons[pygame.K_ESCAPE]:
                done = True

            # 객체 업데이트
            entity.MeaninglessEntity.process()

            # 화면 생성
            self.screen.fill((50, 50, 50))
            entity.MeaninglessEntity.blit((self.screen.get_width() // 2 - player.pos[0], self.screen.get_height() // 2 - player.pos[1]))
            pygame.display.flip()
