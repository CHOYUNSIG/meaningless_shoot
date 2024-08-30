from abc import ABCMeta, abstractmethod
from math import ceil
from typing import TypeVar, Optional

import pygame
from typing_extensions import override

from src import Game
from src.util.Geometry import Point, add_point, round_point, line_dist, copysign

ME = TypeVar('ME', bound='MeaninglessEntity')


class MeaninglessEntity(pygame.sprite.Sprite, metaclass=ABCMeta):
    session: 'Game.Game'
    group: dict[str, pygame.sprite.Group] = {}
    rect_lists: dict[str, list[pygame.rect.Rect]] = {}
    generated: set[ME] = set()
    dispose: set[ME] = set()

    @staticmethod
    def init(session: 'Game.Game'):
        MeaninglessEntity.session = session

    @staticmethod
    def process():
        """
        모든 객체의 move 함수와 update 함수를 호출합니다.
        객체의 생성 및 소멸을 자동으로 실행합니다.
        변경된 객체를 화면에 반영하지는 않습니다.
        """
        # move 호출
        for group in list(MeaninglessEntity.group.values()):
            for entity in group:
                entity.move()
        # rect_lists 재구성
        for group_name, group in list(MeaninglessEntity.group.items()):
            MeaninglessEntity.rect_lists[group_name] = list(map(lambda x: x.get_rounded_rect(), group))
        # update 호출
        for group in list(MeaninglessEntity.group.values()):
            group.update()
        # generated 상태의 객체를 활성화
        for entity in MeaninglessEntity.generated:
            if entity.__class__.__name__ not in MeaninglessEntity.group:
                MeaninglessEntity.group[entity.__class__.__name__] = pygame.sprite.Group()
            MeaninglessEntity.group[entity.__class__.__name__].add(entity)
        # dispose 상태의 객체를 삭제
        for entity in MeaninglessEntity.dispose:
            pygame.sprite.Sprite.kill(entity)
            del entity

    @staticmethod
    def blit(offset: Point):
        """
        모든 객체를 화면에 표현합니다.
        :param offset: 뷰 포인트의 위치입니다.
        """
        z_group: dict[int, pygame.sprite.Group] = dict()
        for group in MeaninglessEntity.group.values():
            for entity in group:
                entity.draw(offset, z_group)
        for z_index in sorted(z_group.keys()):
            z_group[z_index].draw(MeaninglessEntity.session.screen)

    @staticmethod
    def get_collide_entity_by_rect(rect: pygame.rect.Rect, *groups: str) -> Optional['MeaninglessEntity']:
        for group in groups:
            if group in MeaninglessEntity.group:
                sprite_list = MeaninglessEntity.group[group].sprites()
                index = rect.collidelist(MeaninglessEntity.rect_lists[group])
                if index != -1:
                    return sprite_list[index]
        return None

    def __init__(self, image: pygame.Surface, pos: Point, z_index: int):
        super().__init__()
        # 화면에 그려지기 위한 요소입니다.
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (round(pos[0]), round(pos[1]))

        self.pos = pos  # 실제 시스템에서 쓰이는 좌표입니다. 충돌 검사, 화면 표시 때에는 정수형으로 반올림되어 평가됩니다.
        self.z_index = z_index  # 값이 클 수록 위에 그려집니다.
        MeaninglessEntity.generated.add(self)

    @abstractmethod
    def move(self):
        """
        이 메소드는 객체의 위치를 수정합니다.
        한 프레임 루프에서 update 함수보다 먼저 호출됩니다.
        위치 값은 실수형 튜플일 수 있습니다.
        """
        pass

    @abstractmethod
    @override
    def update(self):
        """
        이 메소드는 나머지 상태를 조절합니다.
        한 프레임 루프에서 move 함수보다 나중에 호출됩니다.
        객체의 생성 및 제거는 반드시 이 메소드에서 해야 합니다.
        """
        pass

    def draw(self: ME, offset: Point, z_group: dict[int, pygame.sprite.Group]):
        self.rect.center = round_point(add_point(self.pos, offset))
        if self.z_index not in z_group:
            z_group[self.z_index] = pygame.sprite.Group()
        z_group[self.z_index].add(self)

    @override
    def kill(self):
        MeaninglessEntity.dispose.add(self)

    def get_rounded_rect(self, pos: Optional[Point] = None) -> pygame.rect.Rect:
        if pos is None:
            pos = self.pos
        rect = self.rect.copy()
        rect.center = round_point(pos)
        return rect

    def get_collide_entity(self, *groups: str) -> Optional['MeaninglessEntity']:
        return MeaninglessEntity.get_collide_entity_by_rect(self.get_rounded_rect(), *groups)

    def move_with_collision_safety(self, amount: Point, *collide_groups: str):
        pos = tuple(self.pos)
        dx, dy = [copysign(0.5, v) for v in amount]
        dst = add_point(self.pos, amount)
        for _ in range(ceil(sum(abs(amount[i]) * 2 for i in range(2)))):
            passed = False
            for next_pos in sorted(
                [(pos[0] + dx * int(i == 0), pos[1] + dy * int(i == 1)) for i in range(2) if [dx, dy][i] != 0],
                key=lambda p: line_dist(p, self.pos, dst)
            ):
                if MeaninglessEntity.get_collide_entity_by_rect(
                    self.get_rounded_rect(next_pos),
                    *collide_groups
                ) is None:
                    pos = next_pos
                    passed = True
                    break
            if not passed:
                break
        self.pos = pos
