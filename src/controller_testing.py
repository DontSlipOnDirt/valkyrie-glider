import pygame
import time

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Axes: {joystick.get_numaxes()}")
print("Move ONE control at a time and watch which axis index changes.\n")

while True:
    pygame.event.pump()
    values = [round(joystick.get_axis(i), 2) for i in range(joystick.get_numaxes())]
    print(values, end='\r')
    time.sleep(0.05)