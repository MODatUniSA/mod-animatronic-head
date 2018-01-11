""" Test using xbox360controller and pygame to get controller input
"""

import time

import pygame

import libs.input.xbox360_controller as xbox360_controller

pygame.init()

pygame.joystick.init()
my_controller = xbox360_controller.Controller(0)

while True:
    # Event processing - Need to use this to ensure joystick values are correct
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break

    left_x, left_y = my_controller.get_left_stick()
    right_x, right_y = my_controller.get_right_stick()

    print("LEFT - X:{}, Y:{}".format(left_x, left_y))
    print("RIGHT - X:{}, Y:{}".format(right_x, right_y))
    print("BUTTONS {}".format(my_controller.get_buttons()))

    axis = my_controller.joystick.get_axis( 0 )
    print("Axis {} value: {:>6.3f}".format(0, axis) )

    time.sleep(0.05)
