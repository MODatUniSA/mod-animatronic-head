""" Reads joystick values and uses these to send servo control instructions
"""

import asyncio
import logging
import time
from enum import Enum, auto

import pygame

import libs.input.xbox360_controller as xbox360_controller
from libs.config.device_config import DeviceConfig
from app.servo_control.joystick_control.joystick_servo_map import JoystickServoMap, JoystickAxes
from app.servo_control.servo_positions import ServoPositions
from app.servo_control.instruction_list import InstructionTypes
from app.servo_control.instruction_writer import InstructionWriter

class JoystickServoController:
    def __init__(self, servo_communicator, playback_controller=None):
        self._logger = logging.getLogger('joystick_servo_controller')
        self._write_csv = False
        self._playback_controller = playback_controller
        self._control_time_start = time.time()
        self._servo_communicator = servo_communicator
        self._should_quit = False
        self._map = JoystickServoMap()
        config = DeviceConfig.Instance()
        joystick_config = config.options['JOYSTICK_CONTROL']
        self._fixed_move_speed = joystick_config.getint('MOVE_SPEED')
        self._update_period_seconds = joystick_config.getfloat('UPDATE_PERIOD_SECONDS')
        self._position_threshold = joystick_config.getint('POSITION_DEDUPLICATE_THRESHOLD')
        self._deadzone = joystick_config.getfloat('STICK_DEADZONE')
        self._controller = xbox360_controller.Controller(0, self._deadzone)
        self._axis_stop_sent = {}
        self._last_sent = {}
        self._last_pressed_states = []

        # Default to not overwrite control if we're playing back existing instructions
        self._use_left_stick = (playback_controller is None)
        self._use_right_stick = (playback_controller is None)

    def record_to_file(self, output_filename):
        """ Tells this class to record servo positions to a file, and which file to write to
        """
        self._write_csv = True
        self._instruction_writer = InstructionWriter(output_filename)
        if self._playback_controller is not None:
            self._playback_controller.add_move_instruction_callback(self._write_position_instruction)
            self._playback_controller.add_stop_instruction_callback(self._write_stop_instruction)

    @asyncio.coroutine
    def run(self):
        """ Start processing joystick control.
            If playing back existing instructions, this starts them running.
        """
        if self._playback_controller is not None:
            self._playback_controller.execute_instructions()

        while not self._should_quit:
            self._process_pygame_events()
            self._process_buttons()
            self._process_joystick_axes()
            yield from asyncio.sleep(self._update_period_seconds)

    def stop(self):
        """ Stop the joystick control.
            Ensures control positions written to CSV if recording
        """
        if self._write_csv:
            self._instruction_writer.stop()

        self._should_quit = True

    # PYGAME EVENT PROCESSING
    # =========================================================================

    def _process_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._should_quit = True

    # JOYSTICK HANDLING
    # =========================================================================

    def _process_buttons(self):
        pressed_buttons = self._controller.get_buttons()
        if self._just_pressed(pressed_buttons, xbox360_controller.LEFT_BUMP):
            self._use_left_stick = not self._use_left_stick
            self._logger.info("Processing Left Stick Events: %s", self._use_left_stick)
            if not self._use_left_stick:
                self._clear_control_override([JoystickAxes.LEFT_STICK_X, JoystickAxes.LEFT_STICK_Y])

        if self._just_pressed(pressed_buttons, xbox360_controller.RIGHT_BUMP):
            self._use_right_stick = not self._use_right_stick
            self._logger.info("Processing Right Stick Events: %s", self._use_right_stick)

            if not self._use_right_stick:
                self._clear_control_override([JoystickAxes.RIGHT_STICK_X, JoystickAxes.RIGHT_STICK_Y])

        # Cache current pressed states so we can detect when buttons are first pressed
        self._last_pressed_states = pressed_buttons

    def _clear_control_override(self, axes):
        if self._playback_controller is None:
            return

        # Uncache the last positions sent for these axes
        for axis in axes:
            self._last_sent.pop(axis, None)

        self._playback_controller.clear_control_override(self._map.controlled_servos(axes))

    def _just_pressed(self, pressed_buttons, button_id):
        """ Returns whether this button was just pressed. Useful when we want to take an action
            on the button just being pressed, rather than every time we detect it as pressed
        """

        return pressed_buttons[button_id] and \
            not self._last_pressed_states[button_id]

    def _process_joystick_axes(self):
        left_x, left_y = self._controller.get_left_stick()
        right_x, right_y = self._controller.get_right_stick()
        triggers = self._controller.get_triggers()

        if self._use_left_stick:
            self._handle_axis_position(JoystickAxes.LEFT_STICK_X, left_x)
            self._handle_axis_position(JoystickAxes.LEFT_STICK_Y, left_y)
        if self._use_right_stick:
            self._handle_axis_position(JoystickAxes.RIGHT_STICK_X, right_x)
            self._handle_axis_position(JoystickAxes.RIGHT_STICK_Y, right_y)

        self._handle_axis_position(JoystickAxes.TRIGGERS, triggers)

    def _handle_axis_position(self, axis, value):
        pos_dict = self._to_position_dict(axis, value)

        if pos_dict is None:
            return

        servo_positions = ServoPositions(pos_dict)

        # Don't send duplicate values successively
        if servo_positions.within_threshold(self._last_sent.get(axis), self._position_threshold):
            return

        self._last_sent[axis] = servo_positions

        # If we have a playback controller, pass it position overrides for any
        # control it is performing independently
        if self._playback_controller is not None:
            self._playback_controller.override_control(servo_positions)
            return

        # We only perform movement and writing in here if we don't have a playback controller
        if self._write_csv:
            self._write_position_instruction(pos_dict)
        self._servo_communicator.move_to(servo_positions)

    # INTERNAL HELPERS
    # =========================================================================

    def _to_position_dict(self, axis, value):
        """ Takes the axis value and returns a position dictionary to be passed to the communicator.
            Uses axis position to determine target position. Movement speed is fixed, set in the config.
        """

        positions = self._map.get(axis)
        if positions is None:
            return

        target_positions = positions.interpolated_position_for_percentage(value)
        target_positions.set_speed(self._fixed_move_speed)
        return target_positions.positions

    def _control_time_offset(self, round_digits=2):
        """ Returns the number of seconds we've been running this program execution
        """

        return round(time.time() - self._control_time_start, round_digits)

    # CSV WRITING
    # =========================================================================

    def _write_position_instruction(self, positions):
        self._instruction_writer.write_instruction(self._control_time_offset(), InstructionTypes.POSITION, positions)

    def _write_stop_instruction(self, servos):
        self._instruction_writer.write_instruction(self._control_time_offset(), InstructionTypes.STOP, list(servos))
