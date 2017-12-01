""" Reads joystick values and uses these to send servo control instructions
"""

import asyncio
import logging

import pygame

import libs.input.xbox360_controller as xbox360_controller
from libs.config.device_config import DeviceConfig
from app.servo_control.joystick_control.joystick_servo_map import JoystickServoMap, JoystickAxes
from app.servo_control.servo_limits import ServoLimits

class JoystickServoController:
    def __init__(self, servo_communicator):
        self._logger = logging.getLogger('joystick_servo_controller')
        self._servo_communicator = servo_communicator
        self._should_quit = False
        self._controller = xbox360_controller.Controller(0)
        self._map = JoystickServoMap()
        self._limits = ServoLimits()

        config = DeviceConfig.Instance()
        joystick_config = config.options['JOYSTICK_CONTROL']
        self._min_move_time_ms = joystick_config.getint('MIN_MOVE_TIME_MS')
        self._max_move_time_ms = joystick_config.getint('MAX_MOVE_TIME_MS')
        self._update_period_seconds = joystick_config.getfloat('UPDATE_PERIOD_SECONDS')

    @asyncio.coroutine
    def run(self):
        while not self._should_quit:
            self._process_pygame_events()
            self._process_joystick_axes()
            yield from asyncio.sleep(self._update_period_seconds)

    def stop(self):
        self._should_quit = True

    # INTERNAL METHODS
    # =========================================================================

    def _process_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._should_quit = True

    def _process_joystick_axes(self):
        left_x, left_y = self._controller.get_left_stick()
        right_x, right_y = self._controller.get_right_stick()

        # REVISE: Consider how we would map multiple servos to a single axis (e.g. LEFT Y Opens/Closes mouth)
        self._handle_axis_position(JoystickAxes.LEFT_STICK_X, left_x)
        self._handle_axis_position(JoystickAxes.LEFT_STICK_Y, left_y)
        self._handle_axis_position(JoystickAxes.RIGHT_STICK_X, right_x)
        self._handle_axis_position(JoystickAxes.RIGHT_STICK_Y, right_y)

    def _handle_axis_position(self, axis, value):
        pos_dict = self._to_position_dict(axis, value)
        self._servo_communicator.move_to(pos_dict, self._value_to_time(value))

        # TODO: Write position + time to CSV if flag set

    def _to_position_dict(self, axis, value):
        """ Takes the axis value and returns a position dictionary to be passed to the communicator
        """

        servo = self._map[axis]

        if value > 0:
            target_position = self._limits[servo].upper
        elif value < 0:
            target_position = self._limits[servo].lower
        else:
            # TODO: Need to send stop command for target servo
            self._logger.debug("Sending stop command for servo")
            target_position = -1

        return {servo.value : target_position}

    def _value_to_time(self, value):
        """ Takes an axis value and uses it to determine how the how long the servos should take to reach their target position.
            Movement speed is directly proportional to joystick value, so time is inversely proportional
        """

        # Value is effectively a %, so can use this to lerp between our min/max times
        percentage = abs(value)
        return round((percentage * self._min_move_time_ms) + ((1-percentage) * self._max_move_time_ms), 2)
