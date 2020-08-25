import time
import meaningless_shoot

meaningless_shoot.fps = int(input())
meaningless_shoot.game_loop()

while 'r' in meaningless_shoot.buttons:
    print("\nreloading game\n")
    time.sleep(0.5)
    meaningless_shoot.game_loop()
