""" Communicates with the servos via serial
"""

import logging

import serial

from libs.config.device_config import DeviceConfig
from app.servo_control.servo_positions import ServoPositions

class ServoCommunicator:
    def __init__(self):
        self._logger = logging.getLogger("servo_communicator")

        config = DeviceConfig.Instance()
        serial_config = config.options['SERIAL']
        self._port = serial_config['PORT']
        self._timeout = serial_config.getfloat('TIMEOUT')
        self._speed = serial_config.getint('SPEED')

        self._logger.debug("Opening serial port %s", self._port)
        self._serial = serial.Serial(self._port, self._speed, timeout=self._timeout)
        self._logger.debug("Serial port open")

    def stop(self):
        # TODO: Check if we need to do any checks/cleanup on servos

        self._logger.info("Stopping. Closing serial port.")
        self._serial.close()

    def move_to(self, positions, in_milliseconds):
        """ Move a collection of servos to a position in milliseconds of time.
            Accepts an array of pin:position pairs.
            If in_milliseconds is None, assumes individual servo speeds are specified in the positions
        """

        positions_str = self._to_position_string(positions)
        if positions_str is None:
            self._logger.error("Can't perform move.")
            return

        if in_milliseconds is None:
            instruction = "{}\r".format(positions_str)
        else:
            instruction = "{}T{}\r".format(positions_str, in_milliseconds)

        self._logger.debug("Sending Instruction: %s", instruction)
        self._serial.write(instruction.encode('utf-8'))

    # INTERNAL METHODS
    # =========================================================================

    def _to_position_string(self, positions):
        """ Converts whatever object is passed to a position string. Accepts a string, dict, or ServoPositions object
        """

        if isinstance(positions, ServoPositions):
            return positions.positions_str
        if isinstance(positions, dict):
            return ServoPositions(positions).positions_str
        elif isinstance(positions, str):
            return positions
        else:
            self._logger.error("Unexpected object passed to move_to. Can't convert to positions string.")
            return None
