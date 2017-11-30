""" Reads joystick values and uses these to send servo control instructions
"""

import asyncio

import pygame
import libs.input.xbox360_controller as xbox360_controller

class JoystickServoController:
    def __init__(self, servo_communicator):
        self._servo_communicator = servo_communicator
        self._should_quit = False
        self._controller = xbox360_controller.Controller(0)

    @asyncio.coroutine
    def run(self):
        while not self._should_quit:
            self.process_pygame_events()
            self.process_joystick_axes()
            yield from asyncio.sleep(0.5)

    def stop(self):
        self._should_quit = True

    # INTERNAL METHODS
    # =========================================================================

    def process_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._should_quit = True

    def process_joystick_axes(self):
        left_x, left_y = self._controller.get_left_stick()
        right_x, right_y = self._controller.get_right_stick()

        print("LEFT - X:{}, Y:{}".format(left_x, left_y))
        print("RIGHT - X:{}, Y:{}".format(right_x, right_y))

        # TODO: Get servo mapped to each axis
        # TODO: Determine direction based on value, and speed based on absolute value
