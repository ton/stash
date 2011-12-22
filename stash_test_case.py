import os
import shutil
import subprocess
import unittest

from stash import Stash

class StashTestCase(unittest.TestCase):
    """Base class for test cases that test stash functionality.

    This base class makes sure that all unit tests are executed in a sandbox
    environment.
    """

    PATCHES_PATH = '.patches'
    REPOSITORY_URI = '.repo'

    @classmethod
    def setUpClass(cls):
        """Makes sure that stash will look for patches in the patches path in
        the test directory, and that the repository directory exists.
        """
        if not os.path.exists(cls.REPOSITORY_URI):
            os.mkdir(cls.REPOSITORY_URI)

        if not os.path.exists(cls.PATCHES_PATH):
            os.mkdir(cls.PATCHES_PATH)

        Stash.PATCHES_PATH = cls.PATCHES_PATH

    @classmethod
    def tearDownClass(cls):
        """Cleans up the temporary patches path used for the unit tests."""
        if os.path.exists(cls.PATCHES_PATH):
            shutil.rmtree(cls.PATCHES_PATH)

        # Clean up the temporary repository.
        if os.path.exists(cls.REPOSITORY_URI):
            shutil.rmtree(cls.REPOSITORY_URI)
