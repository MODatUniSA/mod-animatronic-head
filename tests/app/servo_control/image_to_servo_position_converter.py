import pytest

import app.servo_control.image_to_servo_position_converter
from app.servo_control.image_to_servo_position_converter import ImageToServoPositionConverter, DimensionsNotSpecifiedError
from app.servo_control.servo_map import ServoMap

@pytest.fixture
def converter(mocker=None):
    converter = ImageToServoPositionConverter()
    converter.set_image_dimensions((1080, 1920))
    converter._servos = {
        'width' : {
            ServoMap.EYE_LEFT_Y.value : { 'min' : 0, 'max':100 },
            ServoMap.EYE_RIGHT_Y.value : { 'min' : 100, 'max':200 }
        },
        'height' : {
            ServoMap.EYES_X.value : { 'min' : 0, 'max':100 },
        }
    }

    # Overwrite method to ensure servo limits don't affect our results
    if mocker is not None:
        def to_limited_positions(self, positions):
            return positions

        mocker.patch.object(app.servo_control.image_to_servo_position_converter.ServoPositions, '_to_limited_positions', to_limited_positions)

    return converter

class TestSetImageDimensions:
    def test_not_called(self):
        converter = ImageToServoPositionConverter()
        dimensions = (converter._image_width_pixels, converter._image_height_pixels)
        assert dimensions == (None, None)

    def test_called(self):
        converter = ImageToServoPositionConverter()
        input_dimensions = (1080, 1920)
        converter.set_image_dimensions(input_dimensions)
        dimensions = (converter._image_height_pixels, converter._image_width_pixels)
        assert dimensions == input_dimensions

class TestToServoPosition:
    def test_when_image_dimensions_unset(self):
        converter = ImageToServoPositionConverter()
        with pytest.raises(DimensionsNotSpecifiedError, message="Image dimensions must be set before finding servo positions"):
            converter.to_servo_positions((10,20))

    def test_point_top_left(self, mocker):
        image_converter = converter(mocker)
        expected = {
            ServoMap.EYES_X.value : { 'position' : 0 },
            ServoMap.EYE_LEFT_Y.value : { 'position' : 0 },
            ServoMap.EYE_RIGHT_Y.value : { 'position' : 100 }
        }
        assert image_converter.to_servo_positions((0,0)).positions == expected

    def test_point_top_right(self, mocker):
        image_converter = converter(mocker)
        expected = {
            ServoMap.EYES_X.value : { 'position' : 0 },
            ServoMap.EYE_LEFT_Y.value : { 'position' : 100 },
            ServoMap.EYE_RIGHT_Y.value : { 'position' : 200 }
        }
        assert image_converter.to_servo_positions((1920,0)).positions == expected

    def test_point_bottom_left(self, mocker):
        image_converter = converter(mocker)
        expected = {
            ServoMap.EYES_X.value : { 'position' : 100 },
            ServoMap.EYE_LEFT_Y.value : { 'position' : 0 },
            ServoMap.EYE_RIGHT_Y.value : { 'position' : 100 }
        }
        assert image_converter.to_servo_positions((0,1080)).positions == expected

    def test_point_bottom_right(self, mocker):
        image_converter = converter(mocker)
        expected = {
            ServoMap.EYES_X.value : { 'position' : 100 },
            ServoMap.EYE_LEFT_Y.value : { 'position' : 100 },
            ServoMap.EYE_RIGHT_Y.value : { 'position' : 200 }
        }
        assert image_converter.to_servo_positions((1920,1080)).positions == expected

    def test_point_center(self, mocker):
        image_converter = converter(mocker)
        expected = {
            ServoMap.EYES_X.value : { 'position' : 50 },
            ServoMap.EYE_LEFT_Y.value : { 'position' : 50 },
            ServoMap.EYE_RIGHT_Y.value : { 'position' : 150 }
        }
        assert image_converter.to_servo_positions((1920/2,1080/2)).positions == expected
