""" Null Servo Communicator to use when the head isn't connected
"""

import logging

from app.servo_control.servo_communicator import ServoCommunicator

class NullServoCommunicator:
    def __init__(self):
        self._logger = logging.getLogger('null_servo_communicator')

    def move_to(self, positions, in_milliseconds=None):
        self._logger.info("Moving Servo Positions: %s, in %s mS", positions, in_milliseconds)

    def stop_servos(self, servos):
        self._logger.info("Stopping Servos: %s", servos)

    def stop(self):
        self._logger.info("Stopping")
