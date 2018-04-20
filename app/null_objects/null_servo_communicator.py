""" Null Servo Communicator to use when the head isn't connected
"""

import logging

from app.servo_control.servo_positions import ServoPositions
from libs.config.device_config import DeviceConfig

class NullServoCommunicator:
    def __init__(self):
        self._logger = logging.getLogger('null_servo_communicator')
        config = DeviceConfig.Instance()
        logging_config = config.options['LOGGING']
        self._log_instructions = logging_config.getboolean('LOG_SERVO_INSTRUCTIONS')


    def move_to(self, positions, in_milliseconds=None):
        if isinstance(positions, ServoPositions):
            positions = positions.positions_str

        if self._log_instructions:
            self._logger.debug("Moving Servo Positions: %s, in %s mS", positions, in_milliseconds)

    def stop_servos(self, servos):
        self._logger.debug("Stopping Servos: %s", servos)

    def stop(self):
        self._logger.info("Stopping")
