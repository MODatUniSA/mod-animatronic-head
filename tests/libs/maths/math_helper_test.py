import pytest

from libs.maths import math_helper as mh

class TestLerp:
    def test_lerp_start(self):
        assert mh.lerp(5, 10, 0) == 5

    def test_lerp_mid(self):
        assert mh.lerp(5, 10, 0.5) == 7.5

    def test_lerp_end(self):
        assert mh.lerp(5, 10, 1) == 10

    def test_lerp_negative_percentage(self):
        with pytest.raises(ValueError, message="Can't lerp to a negative percent (-1)"):
            mh.lerp(5, 10, -1)

    def test_lerp_negative_values(self):
        assert mh.lerp(-5,-10,0.5) == -7.5
