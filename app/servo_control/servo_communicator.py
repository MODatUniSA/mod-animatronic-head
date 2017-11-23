""" Communicates with the servos via serial
"""

import logging

import serial

from libs.config.device_config import DeviceConfig

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
            Accepts an array of pin:position pairs
        """
        instruction = "{}T{}\r".format(type(self)._to_position_string(positions), in_milliseconds)
        self._logger.debug("Sending Instruction: %s", instruction)
        self._serial.write(instruction.encode('utf-8'))

    # INTERNAL METHODS
    # =========================================================================

    # REVISE: Create a ServoPositions object so we only need to perform this once per phoneme
    @staticmethod
    def _to_position_string(positions):
        return ''.join("#{!s}P{!s}".format(pin,post) for (pin,post) in positions.items())
