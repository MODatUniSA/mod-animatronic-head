from unittest.mock import call
import copy

import pytest

from app.servo_control.servo_positions import ServoPositions
from app.servo_control.servo_map import ServoMap

def patch_servo_limits(mocker):
    mocked_servo_limits = mocker.patch('app.servo_control.servo_positions.ServoLimits')
    mocked_servo_limits.Instance().to_limited_position.return_value = 1

# TODO: Test #merge, #within_threshold

class TestPositions:
    def test_positions_passed_without_speed(self, mocker):
        patch_servo_limits(mocker)
        pos_dict = { ServoMap.JAW.value : { 'position' : 1 }, ServoMap.LIPS_UPPER.value : { 'position' : 1 } }
        # Taking a deepcopy of the input dict so we can compare the two knowing pos_dict has not been modified by ServoPositions
        sp = ServoPositions(copy.deepcopy(pos_dict))

        assert sp.positions == pos_dict

    def test_positions_passed_with_speed(self, mocker):
        patch_servo_limits(mocker)
        pos_dict = { ServoMap.JAW.value : { 'position' : 1, 'speed' : 2 }, ServoMap.LIPS_UPPER.value : { 'position' : 1, 'speed' : 3 } }

        sp = ServoPositions(copy.deepcopy(pos_dict))
        assert sp.positions == pos_dict

    def test_positions_passed_with_basic_structure(self, mocker):
        """ Ensures input dict will be convered to the standard structure and given values based on ServoLimits
        """
        patch_servo_limits(mocker)
        in_dict = { ServoMap.JAW.value : 123, ServoMap.LIPS_UPPER.value : 456 }
        expected_dict = { ServoMap.JAW.value : { 'position' : 1 }, ServoMap.LIPS_UPPER.value : { 'position' : 1 } }

        sp = ServoPositions(copy.deepcopy(in_dict))
        assert sp.positions == expected_dict

    def test_positions_limited(self, mocker):
        """ Ensures positions are limited by passing input values for each servo to ServoLimits
        """
        mocked_servo_limits = mocker.patch('app.servo_control.servo_positions.ServoLimits')

        pos_dict = { ServoMap.JAW.value : { 'position' : 5 }, ServoMap.LIPS_UPPER.value : { 'position' : 10 } }
        sp = ServoPositions(copy.deepcopy(pos_dict))

        calls = [call(ServoMap.JAW.value, 5), call(ServoMap.LIPS_UPPER.value, 10)]
        mocked_servo_limits.Instance().to_limited_position.assert_has_calls(calls)

class TestPositionString:
    def test_string_without_speed(self, mocker):
        patch_servo_limits(mocker)

        pos_dict = { ServoMap.JAW.value : { 'position' : 1 }, ServoMap.LIPS_UPPER.value : { 'position' : 1 } }
        sp = ServoPositions(copy.deepcopy(pos_dict))

        assert sp.positions_str == '#0P1#1P1'

    def test_string_with_speed(self, mocker):
        patch_servo_limits(mocker)

        pos_dict = {
            ServoMap.JAW.value : { 'position' : 1, 'speed' : 5 },
            ServoMap.LIPS_UPPER.value : { 'position' : 1, 'speed' : 10 }
        }
        sp = ServoPositions(copy.deepcopy(pos_dict))

        assert sp.positions_str == '#0P1S5#1P1S10'

class TestToStr:
    def setup_method(self, fn):
        self.pos_dict = {
            ServoMap.JAW.value : { 'position' : 1, 'speed' : 5 },
            ServoMap.LIPS_UPPER.value : { 'position' : 1, 'speed' : 10 }
        }

    def test_with_no_servos_specified(self, mocker):
        """ Ensures normal string for all servos returned
        """

        patch_servo_limits(mocker)
        sp = ServoPositions(copy.deepcopy(self.pos_dict))

        assert sp.to_str() == sp.positions_str

    def test_with_servos_specified(self, mocker):
        """ Ensures string for only specified servos returned
        """

        patch_servo_limits(mocker)
        sp = ServoPositions(copy.deepcopy(self.pos_dict))

        assert sp.to_str(without=[ServoMap.JAW.value]) == '#1P1S10'

class TestSetSpeed:
    def setup_method(self, fn):
        self.pos_dict = {
            ServoMap.JAW.value : { 'position' : 1, 'speed' : 5 },
            ServoMap.LIPS_UPPER.value : { 'position' : 1, 'speed' : 10 }
        }

    def test_value_passed(self, mocker):
        patch_servo_limits(mocker)
        sp = ServoPositions(copy.deepcopy(self.pos_dict))
        sp.set_speeds(50)

        expected = {
            ServoMap.JAW.value : { 'position' : 1, 'speed' : 50 },
            ServoMap.LIPS_UPPER.value : { 'position' : 1, 'speed' : 50 }
        }

        assert sp.positions == expected

    def test_positions_string_updated(self, mocker):
        patch_servo_limits(mocker)
        sp = ServoPositions(copy.deepcopy(self.pos_dict))
        sp.set_speeds(50)
        expected = "#{}P1S50#{}P1S50".format(ServoMap.JAW.value, ServoMap.LIPS_UPPER.value)

        assert sp.to_str() == expected
