import pytest

from libs.helpers import list_helpers as lh

class TestFlatten:
    def test_flat_list(self):
        in_list = [1,2,3,4]
        assert list(lh.flatten(in_list)) == in_list

    def test_single_nested_list(self):
        in_list = [[1,2],[3,4]]
        expected = [1,2,3,4]
        assert list(lh.flatten(in_list)) == expected

    def test_unevenly_nested_list(self):
        in_list = [[1,[2]],[[3,4]]]
        expected = [1,2,3,4]
        assert list(lh.flatten(in_list)) == expected
