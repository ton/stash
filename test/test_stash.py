import os

from nose.tools import assert_equal, assert_raises

from stash import Stash, StashException
from stash_test_case import StashTestCase

class TestStash(StashTestCase):

    def setUp(self):
        """Initialize each unit test by creating three patches a, b, and c with
        their contents equal to their filename in upper case.
        """
        for patch_name in ['a', 'b', 'c']:
            open(os.path.join(self.PATCHES_PATH, patch_name), 'w').write(patch_name.upper())

    def test_get_patches(self):
        """Tests that it is possible to retrieve all stashes patches."""
        assert_equal(Stash.get_patches(), ['a', 'b', 'c'])

    def test_removing_patch(self):
        """Tests that it is possible to remove stashed patches."""
        Stash.remove_patch('b')
        assert_equal(Stash.get_patches(), ['a', 'c'])

        Stash.remove_patch('c')
        assert_equal(Stash.get_patches(), ['a'])

        Stash.remove_patch('a')
        assert_equal(Stash.get_patches(), [])

    def test_removing_non_existent_patch_raises_exception(self):
        """Tests that removing a non existent patch raises an exception."""
        assert_raises(StashException, Stash.remove_patch, 'd')

    def test_get_patch(self):
        """Tests that it is possible to retrieve the contents of stashed
        patches.
        """
        assert_equal(Stash.get_patch('a'), 'A')
        assert_equal(Stash.get_patch('b'), 'B')
        assert_equal(Stash.get_patch('c'), 'C')

    def test_getting_non_existent_patch_raises_exception(self):
        """Tests that showing a non existent patch raises an exception."""
        assert_raises(StashException, Stash.get_patch, 'd')
