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
        joystick_config = config.options['JOYSTICK_CONTROL']
        self._port = serial_config['PORT']
        self._timeout = serial_config.getfloat('TIMEOUT')
        self._speed = serial_config.getint('SPEED')
        self._position_threshold = joystick_config.getint('POSITION_DEDUPLICATE_THRESHOLD')

        self._logger.debug("Opening serial port %s", self._port)
        self._serial = serial.Serial(self._port, self._speed, timeout=self._timeout)
        self._logger.debug("Serial port open")

        self._previous_positions = None

    def stop(self):
        self._logger.info("Stopping. Closing serial port.")
        self._serial.close()

    def move_to(self, positions, in_milliseconds=None):
        """ Move a collection of servos to a position in milliseconds of time.
            Accepts an array of pin:position pairs, ServoPositions object, or raw positions instruction string
            If in_milliseconds is None, assumes individual servo speeds are specified in the positions
            If ServoPositions object passed, deduplicates instructions
        """

        if self._ignore_duplicate_positions(positions):
            self._logger.debug("Ignoring duplicate positions")
            return

        positions_str = self._to_position_string(positions)
        if positions_str is None:
            self._logger.error("Can't perform move.")
            return

        if in_milliseconds is None:
            instruction = "{}\r".format(positions_str)
        else:
            instruction = "{}T{}\r".format(positions_str, in_milliseconds)

        # self._logger.debug("Sending Instruction: %s", instruction)
        self._serial.write(instruction.encode('utf-8'))

    def stop_servos(self, servos):
        """ Accepts an array of servo pins to stop moving
        """

        self._logger.debug("Stopping Servos: %s", servos)

        for servo in servos:
            instruction = "STOP {}\r".format(servo)
            self._serial.write(instruction.encode('utf-8'))

    # INTERNAL METHODS
    # =========================================================================

    def _ignore_duplicate_positions(self, positions):
        if not isinstance(positions, ServoPositions):
            return False

        should_ignore = positions.within_threshold(self._previous_positions, self._position_threshold)
        self._previous_positions = positions
        return should_ignore

    def _to_position_string(self, positions):
        """ Converts whatever object is passed to a position string. Accepts a string, dict, or ServoPositions object
        """

        if isinstance(positions, ServoPositions):
            return positions.to_str()
        if isinstance(positions, dict):
            return ServoPositions(positions).to_str()
        elif isinstance(positions, str):
            # WARNING: No limit clamping is performed if a string is passed directly!
            return positions
        else:
            self._logger.error("Unexpected object passed to move_to. Can't convert to positions string.")
            return None
