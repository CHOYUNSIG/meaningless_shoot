import time
import mnlst

mnlst.fps = int(input())
mnlst.game_loop()

while 'r' in mnlst.buttons:
    print("\nreloading game\n")
    time.sleep(0.5)
    mnlst.game_loop()
