# Import a library of functions called 'pygame'
import pygame
import random
import math
#import gc
#import tracemalloc

'''
<hyperparameters>
can be modified by user
need before start
'''
fps = 60
wall_pattern_size = 11
size = [600,480]
COLOR_BG = (50, 50, 50)
bullet_cool = 0.1
particle_remain_time = 10

'''
<global var 1>
cannot change
'''
player_size = size[0]//20
player_velocity = size[0]/fps/2
bullet_velocity = size[0]/fps/0.5

#image load
image_player = pygame.image.load('meaningless_data/image/player.png')
image_bullet = pygame.image.load('meaningless_data/image/bullet.png')
image_wall = pygame.image.load('meaningless_data/image/wall.png')


'''
<global var 2>
can change
globalization in any obj
''' 
buttons = list()
x_weight, y_weight = 0, 0
move_x, move_y = 0, 0
atk_permission = [0,0,0,0]
done = False

#debug parameters
debug_frame = 0

bullet_remain = 0
particle_remain = 0
player_remain = 0
wall_remain = 0

#스프라이트 그룹
player_cache=list()
bullet_cache=list()
particle_cache=list()
wall_cache=list()
cache_list = [player_cache, bullet_cache, wall_cache, particle_cache]

#화면 표시 그룹
player_draw_cache=list()
bullet_draw_cache=list()
particle_draw_cache=list()
wall_draw_cache=list()
draw_cache_list = [player_draw_cache, bullet_draw_cache, wall_draw_cache, particle_draw_cache]


def wall_pattern(map, x, y):
    map[y][x] = 1
    if random.randrange(10)>6 and  x < wall_pattern_size-1 and (x+2 >= wall_pattern_size or map[y][x+2]==0) and (y-1 < 0 or map[y-1][x+1]==0) and (y+1 >= wall_pattern_size or map[y+1][x+1]==0) and (x+2 >= wall_pattern_size or y-1 < 0 or map[y-1][x+2]==0) and (x+2 >= wall_pattern_size or y+1 >= wall_pattern_size or map[y+1][x+2]==0):
        wall_pattern(map, x+1, y)
    if random.randrange(10)>6 and  y < wall_pattern_size-1 and (y+2 >= wall_pattern_size or map[y+2][x]==0) and (x-1 < 0 or map[y+1][x-1]==0) and (x+1 >= wall_pattern_size or map[y+1][x+1]==0) and (y+2 >= wall_pattern_size or x-1 < 0 or map[y+2][x-1]==0) and (y+2 >= wall_pattern_size or x+1 >= wall_pattern_size or map[y+2][x+1]==0):
        wall_pattern(map, x, y+1)
    if random.randrange(10)>6 and  x > 0 and (x-2 < 0 or map[y][x-2]==0) and (y-1 < 0 or map[y-1][x-1]==0) and (y+1 >= wall_pattern_size or map[y+1][x-1]==0) and (x-2 < 0 or y-1 < 0 or map[y-1][x-2]==0) and (x-2 < 0 or y+1 >= wall_pattern_size or map[y+1][x-2]==0):
        wall_pattern(map, x-1, y)
    if random.randrange(10)>6 and  y > 0 and (y-2 < 0 or map[y-2][x]==0) and (x-1 < 0 or map[y-1][x-1]==0) and (x+1 >= wall_pattern_size or map[y-1][x+1]==0) and (x+1 >= wall_pattern_size or y-2 < 0 or map[y-2][x+1]==0) and (x-1 < 0 or y-2 < 0 or map[y-2][x-1]==0):
        wall_pattern(map, x, y-1)
    return map

def delete_sprite(input_sprite):
    input_sprite.kill()
    '''
    referrers = gc.get_referrers(input_sprite)
    for referrer in referrers:
        if type(referrer) == dict:
            for key, value in referrer.items():
                if value is input_sprite:
                    referrer[key] = None
    '''
    #gc.collect()
    del input_sprite





# 스프라이트 클래스 정의
class player(pygame.sprite.Sprite): #sprite 0
    def __init__(self, x_weight, y_weight): # 생성자 파라미터로 스프라이트에 사용될 이미지 경로와 스프라이트 초기 위치를 받는다
        global player_remain
        player_remain += 1
        print("player generated", player_remain)
        pygame.sprite.Sprite.__init__(self)
        self.position = (size[0]//2+x_weight, size[1]//2+y_weight)
        self.image = image_player # 스프라이트에 사용될 이미지를 저장할 사용자 변수
        self.image = pygame.transform.scale(self.image, (player_size,player_size))
        self.image = pygame.transform.rotate(self.image, 0) # 이미지를 회전 각도 만큼 회전시킨다
        self.rect = self.image.get_rect()
        self.rect.center = self.position # 이미지의 출력 위치를 정한다
    def update(self):
        self.position = self.position
        self.rect = self.image.get_rect()
        self.rect.center = self.position # 이미지의 출력 위치를 정한다
        global player_draw_cache
        player_draw_cache.append(self)
    def __del__(self):
        global player_remain
        player_remain -= 1
        print("player deleted", player_remain)

class bullet(pygame.sprite.Sprite): #sprite 1
    def __init__(self, position, direction): # 생성자 파라미터로 스프라이트에 사용될 이미지 경로와 스프라이트 초기 위치를 받는다
        global bullet_remain
        bullet_remain += 1
        print("bullet generated",bullet_remain)
        pygame.sprite.Sprite.__init__(self)
        self.position = position # 스프라이트의 위치를 저장할 사용자 변수
        self.direction = direction
        self.image = image_bullet # 스프라이트에 사용될 이미지를 저장할 사용자 변수
        self.image = pygame.transform.scale(self.image, (size[0]//50,size[0]//200))
        self.image = pygame.transform.rotate(self.image, direction) # 이미지를 회전 각도 만큼 회전시킨다
        self.remain_frame = 0
        self.rect = self.image.get_rect()
        self.rect.center = self.position # 이미지의 출력 위치를 정한다
    def update(self): # 스프라이트의 상태를 업데이트 하는 함수. 필요에 따라 파라미터가 추가될 수도 있다.
        self.remain_frame +=1
        global bullet_draw_cache
        if self.direction == 0:
            self.position=(round(self.position[0]+bullet_velocity+x_weight), round(self.position[1]+y_weight))
            if self.position[0] <= size[0]+size[0]//50/2: bullet_draw_cache.append(self)
        elif self.direction == 90:
            self.position=(round(self.position[0]+x_weight), round(self.position[1]+bullet_velocity+y_weight))
            if self.position[1] <= size[1]+size[0]//50/2: bullet_draw_cache.append(self)
        elif self.direction == 180:
            self.position=(round(self.position[0]-bullet_velocity+x_weight), round(self.position[1]+y_weight))
            if self.position[0] >= -size[0]//50/2: bullet_draw_cache.append(self)
        else:
            self.position=(round(self.position[0]+x_weight), round(self.position[1]-bullet_velocity+y_weight))
            if self.position[1] >= -size[0]//50/2: bullet_draw_cache.append(self)
        # 출력에 사용될 이미지, 위치를 정한다
        self.rect = self.image.get_rect()
        self.rect.center = self.position # 이미지의 출력 위치를 정한다
    def __del__(self):
        global bullet_remain
        bullet_remain -= 1
        print("bullet deleted",bullet_remain)

class wall(pygame.sprite.Sprite): #sprite 2
    def __init__(self, position): # 생성자 파라미터로 스프라이트에 사용될 이미지 경로와 스프라이트 초기 위치를 받는다
        global wall_remain
        wall_remain += 1
        print("wall generated",wall_remain)
        pygame.sprite.Sprite.__init__(self)
        self.image = image_wall # 스프라이트에 사용될 이미지를 저장할 사용자 변수
        self.image = pygame.transform.scale(self.image, (player_size,player_size))
        self.position = position
        self.rect = self.image.get_rect()
        self.rect.center = self.position # 이미지의 출력 위치를 정한다
    def update(self): # 스프라이트의 상태를 업데이트 하는 함수. 필요에 따라 파라미터가 추가될 수도 있다.
        self.position = (round(self.position[0]+x_weight), round(self.position[1]+y_weight))
        self.rect = self.image.get_rect()
        self.rect.center = self.position # 이미지의 출력 위치를 정한다
        global wall_draw_cache
        if -player_size/2<=self.position[0]<=size[0]+player_size/2 and -player_size/2<=self.position[1]<=size[1]+player_size/2:
            wall_draw_cache.append(self)
    def __del__(self):
        global wall_remain
        wall_remain -= 1
        print("wall deleted",wall_remain)

class particle(pygame.sprite.Sprite): #sprite 3
    def __init__(self, position): # 생성자 파라미터로 스프라이트에 사용될 이미지 경로와 스프라이트 초기 위치를 받는다
        global particle_remain
        particle_remain += 1
        print("particle generated",particle_remain)
        pygame.sprite.Sprite.__init__(self)
        self.size = round(size[0]/200*(random.random()*0.5+0.5))
        self.image = image_wall # 스프라이트에 사용될 이미지를 저장할 사용자 변수
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.position = position
        self.remain_frame = 0
        self.rect = self.image.get_rect()
        self.rect.center = self.position # 이미지의 출력 위치를 정한다
        #bouncing parameters
        self.bounce_count = [1,1,1,1,2,2,3][random.randrange(0,7)]
        self.bounce_not_end = True
        bounce_direction_radian = random.random()*math.pi*2
        self.bounce_direction_x = math.cos(bounce_direction_radian)
        self.bounce_direction_y = math.sin(bounce_direction_radian)
        self.bounce_delta_v = size[0]/fps*(0.5+random.random()*0.5)/0.1
        self.bounce_max_v = sorted([size[0]*(0.5+random.random()*0.5) for i in range(self.bounce_count)], reverse=True)
        self.bounce_max_v[0] *=2
        self.bounce_current_count = 0
        self.bounce_mode = 1
        self.bounce_current_v = self.bounce_max_v[0]
    def update(self): # 스프라이트의 상태를 업데이트 하는 함수. 필요에 따라 파라미터가 추가될 수도 있다.
        x_bounce = 0; y_bounce = 0
        new_size = self.size
        if self.bounce_not_end:
            next_v = 0
            if self.bounce_mode == 0:
                if self.bounce_current_v+self.bounce_delta_v > self.bounce_max_v[self.bounce_current_count]:
                    self.bounce_mode = 1
                    next_v = self.bounce_current_v - self.bounce_delta_v
                else:
                    next_v = self.bounce_current_v + self.bounce_delta_v
            else:
                if self.bounce_current_v-self.bounce_delta_v < 0:
                    if self.bounce_current_count == self.bounce_count - 1:
                        self.bounce_current_v = 0
                        self.bounce_not_end = False
                    else:
                        self.bounce_current_count += 1
                        self.bounce_mode = 0
                        next_v = self.bounce_current_v + self.bounce_delta_v
                else:
                    next_v = self.bounce_current_v - self.bounce_delta_v
            distance = (self.bounce_current_v + next_v)/fps/2
            x_bounce = distance*self.bounce_direction_x
            y_bounce = distance*self.bounce_direction_y
            new_size = round(self.size*(1+self.bounce_current_v/size[0]))
            self.image = pygame.transform.scale(self.image, (new_size, new_size))
            self.bounce_current_v = next_v
        else:
            pass

        self.remain_frame += 1
        self.position = (round(self.position[0]+x_weight+x_bounce), round(self.position[1]+y_weight+y_bounce))
        self.rect = self.image.get_rect()
        self.rect.center = self.position # 이미지의 출력 위치를 정한다
        global particle_draw_cache
        if -new_size/2<=self.position[0]<=size[0]+new_size/2 and -new_size/2<=self.position[1]<=size[1]+new_size/2:
            particle_draw_cache.append(self)
    def __del__(self):
        global particle_remain
        particle_remain -= 1
        print("particle deleted",particle_remain)





def game_loop():
    # Initialize the game engine
    pygame.init()
    #tracemalloc.start()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("meaningless : shoot")

    #var init
    global buttons
    global x_weight, y_weight
    global move_x, move_y
    global atk_permission
    global done

    global debug_frame

    buttons = list()
    x_weight, y_weight = 0, 0
    move_x, move_y = 0, 0
    atk_permission = [0,0,0,0]
    done = False

    debug_frame = 0

    group_list = list()
    for cache in cache_list:
        cache.clear()
        group_list.append(pygame.sprite.Group(*cache))

    draw_group_list = list()
    for draw_cache in draw_cache_list:
        draw_cache.clear()
        draw_group_list.append(pygame.sprite.Group(*draw_cache))
    
    #게임 초기조건
    player_cache.append(player(0,0))

    wall_cache.append(wall((size[0]//2+player_size*2.5, size[1]//2+player_size*2.5)))
    wall_cache.append(wall((size[0]//2+player_size*2.5, size[1]//2+player_size*1.5)))
    wall_cache.append(wall((size[0]//2+player_size*2.5, size[1]//2+player_size*0.5)))
    wall_cache.append(wall((size[0]//2+player_size*2.5, size[1]//2-player_size*0.5)))
    wall_cache.append(wall((size[0]//2+player_size*2.5, size[1]//2-player_size*1.5)))
    wall_cache.append(wall((size[0]//2+player_size*2.5, size[1]//2-player_size*2.5)))
    wall_cache.append(wall((size[0]//2+player_size*1.5, size[1]//2-player_size*2.5)))
    wall_cache.append(wall((size[0]//2+player_size*0.5, size[1]//2-player_size*2.5)))
    wall_cache.append(wall((size[0]//2-player_size*0.5, size[1]//2-player_size*2.5)))
    wall_cache.append(wall((size[0]//2-player_size*1.5, size[1]//2-player_size*2.5)))
    wall_cache.append(wall((size[0]//2-player_size*2.5, size[1]//2-player_size*2.5)))
    wall_cache.append(wall((size[0]//2-player_size*2.5, size[1]//2-player_size*1.5)))
    wall_cache.append(wall((size[0]//2-player_size*2.5, size[1]//2-player_size*0.5)))
    wall_cache.append(wall((size[0]//2-player_size*2.5, size[1]//2+player_size*0.5)))
    wall_cache.append(wall((size[0]//2-player_size*2.5, size[1]//2+player_size*1.5)))
    wall_cache.append(wall((size[0]//2-player_size*2.5, size[1]//2+player_size*2.5)))
    wall_cache.append(wall((size[0]//2-player_size*1.5, size[1]//2+player_size*2.5)))
    wall_cache.append(wall((size[0]//2-player_size*0.5, size[1]//2+player_size*2.5)))
    wall_cache.append(wall((size[0]//2+player_size*0.5, size[1]//2+player_size*2.5)))
    wall_cache.append(wall((size[0]//2+player_size*1.5, size[1]//2+player_size*2.5)))

    #main game loop
    while not done:

        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(fps)
        screen.fill(COLOR_BG)

        # Main Event Loop
        for event in pygame.event.get():# User did something
            if event.type == pygame.KEYDOWN:# If user release what he pressed.
                buttons = [pygame.key.name(k) for k,v in enumerate(pygame.key.get_pressed()) if v]
            elif event.type == pygame.KEYUP:
                buttons = [pygame.key.name(k) for k,v in enumerate(pygame.key.get_pressed()) if v]
            elif event.type == pygame.QUIT:# If user clicked close
                done = True # Flag that we are done so we exit this loop

        for i in range(len(bullet_cache)-1,-1,-1):
            hit_wall_list = pygame.sprite.spritecollide(bullet_cache[i],wall_cache,False)
            if len(hit_wall_list) > 0:
                delete_sprite(bullet_cache.pop(i))
                for j in hit_wall_list:
                    index = wall_cache.index(j)
                    for k in range(random.randrange(5,11)):
                        particle_cache.append(particle(wall_cache[index].position))
                    delete_sprite(wall_cache.pop(index))
            elif bullet_cache[i].remain_frame > fps*1:
                delete_sprite(bullet_cache.pop(i))
        #총알 처리

        for i in range(len(particle_cache)-1,-1,-1):
            if particle_cache[i].remain_frame > fps*particle_remain_time or len(pygame.sprite.spritecollide(particle_cache[i],wall_cache,False)) > 0:
                delete_sprite(particle_cache.pop(i))
        #파티클 처리

        # 키 입력 해석 시작
        if 'escape' in buttons:
            print("ecs entered")
            done=True
        if 'r' in buttons:
            done=True

        if 'right' in buttons and atk_permission[0] == 0:
            bullet_cache.append(bullet((size[0]/2,size[1]/2),0))
            atk_permission[0] = round(bullet_cool*fps)
        if 'down' in buttons and atk_permission[1] == 0:
            bullet_cache.append(bullet((size[0]/2,size[1]/2),90))
            atk_permission[1] = round(bullet_cool*fps)
        if 'left' in buttons and atk_permission[2] == 0:
            bullet_cache.append(bullet((size[0]/2,size[1]/2),180))
            atk_permission[2] = round(bullet_cool*fps)
        if 'up' in buttons and atk_permission[3] == 0:
            bullet_cache.append(bullet((size[0]/2,size[1]/2),270))
            atk_permission[3] = round(bullet_cool*fps)

        for i in range(4):
            if atk_permission[i] > 0 : atk_permission[i] -= 1

        if 'w' in buttons and move_y != 1 : move_y = -1
        elif 's' in buttons and move_y != -1 : move_y = 1
        else : move_y = 0
        if 'a' in buttons and move_x != 1 : move_x = -1
        elif 'd' in buttons and move_x != -1 : move_x = 1
        else : move_x = 0

        #키 입력 해석 끝

        x_weight, y_weight = 0, 0
        if move_x != 0 or move_y != 0:
            for i in range(round(player_velocity)):
                if len(pygame.sprite.spritecollide(player(x_weight+move_x, y_weight+move_y),wall_cache,False)) != 0:
                    if len(pygame.sprite.spritecollide(player(x_weight, y_weight + move_y),wall_cache,False)) == 0:
                        for j in range(round(player_velocity) - i):
                            if len(pygame.sprite.spritecollide(player(x_weight, y_weight + move_y), wall_cache, False)) == 0:
                                y_weight += move_y
                            else: break
                    elif len(pygame.sprite.spritecollide(player(x_weight+ move_x, y_weight),wall_cache,False)) == 0:
                        for j in range(round(player_velocity) - i):
                            if len(pygame.sprite.spritecollide(player(x_weight+ move_x, y_weight ), wall_cache,False)) == 0:
                                x_weight += move_x
                            else: break
                    break
                x_weight += move_x; y_weight += move_y
            x_weight, y_weight = -x_weight, -y_weight
        #플레이어 이동

        if random.randrange(fps*1) == 1 and (move_x != 0 or move_y != 0):
            if move_x == -1: init_x = -size[0] // 20 * wall_pattern_size
            elif move_x == 0: init_x = size[0] // 2 - size[0] // 20 * (wall_pattern_size // 2)
            else: init_x = size[0] + size[0] // 20
            if move_y == -1: init_y = -size[0] // 20 * wall_pattern_size
            elif move_y == 0: init_y = size[1] // 2 - size[0] // 20 * (wall_pattern_size // 2)
            else: init_y = size[1] + size[0] // 20

            temp_wall = [[0]*wall_pattern_size for i in range(wall_pattern_size)]
            if random.randrange(10) == 1:
                rect = random.randrange(1,wall_pattern_size+1)
                for i in range(rect):
                    for j in range(rect):
                        temp_wall[i][j] = 1
            else : temp_wall = wall_pattern(temp_wall, wall_pattern_size//2, wall_pattern_size//2)
            new_wall_cache = list(); is_it_overlayed = False
            for i in range(wall_pattern_size):
                for j in range(wall_pattern_size):
                    if temp_wall[i][j] == 1:
                        new_wall = wall((init_x+size[0]//20*i, init_y+size[0]//20*j))
                        if len(pygame.sprite.spritecollide(new_wall,wall_cache,False)) != 0 : is_it_overlayed = True
                        new_wall_cache.append(new_wall)
            if is_it_overlayed == False : wall_cache.extend(new_wall_cache)
        #벽 생성

        # 게임 상태 업데이트시 해야할 부분
        for index in range(4):
            draw_cache_list[index].clear()
            draw_group_list[index].empty()
            group_list[index].empty()
            group_list[index].add(*cache_list[index])
            group_list[index].update()
            draw_group_list[index].add(*draw_cache_list[index])

        #화면에 먼저 그릴 것부터 호출할 것
        draw_group_list[3].draw(screen) #particle
        draw_group_list[1].draw(screen) #bullet
        draw_group_list[0].draw(screen) #player
        draw_group_list[2].draw(screen) #wall
        # Go ahead and update the screen with what we've drawn.
        # This MUST happen after all the other drawing commands.
        pygame.display.flip()

        if debug_frame == 0:
            debug_frame = 10*fps
            print("\nwall:",wall_remain,"bullet:",bullet_remain)
            print("particle:",particle_remain,"player:",player_remain,"\n")
            '''
            top = tracemalloc.take_snapshot().statistics('lineno')
            for i in top[:10]:
                print(i)
            '''
        else: debug_frame -= 1

        #gc.collect()

    # Be IDLE friendly
    for i in range(4):
        for j in range(len(cache_list[i])-1,-1,-1): delete_sprite(cache_list[i].pop(j))
        for j in range(len(draw_cache_list[i])-1,-1,-1): delete_sprite(draw_cache_list[i].pop(j))
    pygame.quit()

#game_loop()