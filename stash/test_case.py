import os
import shutil
import unittest

from .stash import Stash

class StashTestCase(unittest.TestCase):
    """Base class for test cases that test stash functionality.

    This base class makes sure that all unit tests are executed in a sandbox
    environment.
    """

    STASH_PATH = os.path.join('tests', '.stash')
    REPOSITORY_URI = os.path.join('tests', '.repo')

    @classmethod
    def setUpClass(cls):
        """Makes sure that stash will look for patches in the patches path in
        the test directory, and that the repository directory exists.
        """
        if not os.path.exists(cls.REPOSITORY_URI):
            os.mkdir(cls.REPOSITORY_URI)

        if not os.path.exists(cls.STASH_PATH):
            os.mkdir(cls.STASH_PATH)

        Stash.STASH_PATH = cls.STASH_PATH

    @classmethod
    def tearDownClass(cls):
        """Cleans up the temporary patches path used for the unit tests."""
        if os.path.exists(cls.STASH_PATH):
            shutil.rmtree(cls.STASH_PATH)

        # Clean up the temporary repository.
        if os.path.exists(cls.REPOSITORY_URI):
            shutil.rmtree(cls.REPOSITORY_URI)

    def tearDown(self):
        """Removes all stashed patches."""
        for patch_name in os.listdir(self.STASH_PATH):
            os.unlink(os.path.join(self.STASH_PATH, patch_name))
