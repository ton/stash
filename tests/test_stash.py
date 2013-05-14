import os

from nose.tools import assert_equal, assert_raises

from shelf.shelf import Shelf, ShelfException
from shelf.test_case import ShelfTestCase

class TestShelf(ShelfTestCase):

    def setUp(self):
        """Initialize each unit test by creating three patches a, b, and c with
        their contents equal to their filename in upper case.
        """
        for patch_name in ['a', 'b', 'c']:
            open(os.path.join(self.SHELF_PATH, patch_name), 'w').write(patch_name.upper())

    def test_get_patches(self):
        """Tests that it is possible to retrieve all shelved patches."""
        assert_equal(Shelf.get_patches(), ['a', 'b', 'c'])

    def test_removing_patch(self):
        """Tests that it is possible to remove shelved patches."""
        Shelf.remove_patch('b')
        assert_equal(Shelf.get_patches(), ['a', 'c'])

        Shelf.remove_patch('c')
        assert_equal(Shelf.get_patches(), ['a'])

        Shelf.remove_patch('a')
        assert_equal(Shelf.get_patches(), [])

    def test_removing_non_existent_patch_raises_exception(self):
        """Tests that removing a non existent patch raises an exception."""
        assert_raises(ShelfException, Shelf.remove_patch, 'd')

    def test_get_patch(self):
        """Tests that it is possible to retrieve the contents of shelved
        patches.
        """
        assert_equal(Shelf.get_patch('a'), 'A')
        assert_equal(Shelf.get_patch('b'), 'B')
        assert_equal(Shelf.get_patch('c'), 'C')

    def test_getting_non_existent_patch_raises_exception(self):
        """Tests that showing a non existent patch raises an exception."""
        assert_raises(ShelfException, Shelf.get_patch, 'd')
