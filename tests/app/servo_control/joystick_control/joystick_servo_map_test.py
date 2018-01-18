import pytest

from app.servo_control.joystick_control.joystick_servo_map import JoystickServoMap, JoystickAxes, JoystickServoPositions
from app.servo_control.servo_map import ServoMap

@pytest.fixture
def joystick_servo_map():
    servo_map = JoystickServoMap()
    servo_map[JoystickAxes.LEFT_STICK_X] = JoystickServoPositions(
        {
            ServoMap.LIPS_LEFT.value : { 'position' : 0 },
            ServoMap.LIPS_RIGHT.value : { 'position' : 0 }
        },
        {
            ServoMap.LIPS_LEFT.value : { 'position' : 100 },
            ServoMap.LIPS_RIGHT.value : { 'position' : 100 }
        }
    )

    servo_map[JoystickAxes.LEFT_STICK_Y] = JoystickServoPositions(
        {
            ServoMap.LIPS_LOWER.value : { 'position' : 0 },
            ServoMap.LIPS_UPPER.value : { 'position' : 0 }
        },
        {
            ServoMap.LIPS_LOWER.value : { 'position' : 100 },
            ServoMap.LIPS_UPPER.value : { 'position' : 100 }
        }
    )

    servo_map[JoystickAxes.RIGHT_STICK_Y] = JoystickServoPositions({},{})

    return servo_map

class TestMapControlledServos:
    def test_single_axis_passed(self, joystick_servo_map):
        expected = set([ServoMap.LIPS_LEFT.value, ServoMap.LIPS_RIGHT.value])
        assert joystick_servo_map.controlled_servos([JoystickAxes.LEFT_STICK_X]) == expected

    def test_multiple_axes_passed(self, joystick_servo_map):
        expected = set([
            ServoMap.LIPS_LEFT.value,
            ServoMap.LIPS_RIGHT.value,
            ServoMap.LIPS_LOWER.value,
            ServoMap.LIPS_UPPER.value
        ])
        args = [JoystickAxes.LEFT_STICK_X, JoystickAxes.LEFT_STICK_Y]

        assert joystick_servo_map.controlled_servos(args) == expected

    def test_unmapped_axis_passed(self, joystick_servo_map):
        assert joystick_servo_map.controlled_servos(['unmapped_key']) == set()

    def test_unmapped_and_mapped_axes_passed(self, joystick_servo_map):
        expected = set([ServoMap.LIPS_LEFT.value, ServoMap.LIPS_RIGHT.value])
        args = [JoystickAxes.LEFT_STICK_X, 'unmapped_key']

        assert joystick_servo_map.controlled_servos(args) == expected

    def test_empty_axis_passed(self, joystick_servo_map):
        assert joystick_servo_map.controlled_servos([JoystickAxes.RIGHT_STICK_Y]) == set()

    def test_empty_and_populated_axes_passed(self, joystick_servo_map):
        expected = set([ServoMap.LIPS_LEFT.value, ServoMap.LIPS_RIGHT.value])
        args = [JoystickAxes.LEFT_STICK_X, JoystickAxes.RIGHT_STICK_Y]

        assert joystick_servo_map.controlled_servos(args) == expected
