import os
import shutil
import unittest

from shelf import Shelf

class ShelfTestCase(unittest.TestCase):
    """Base class for test cases that test shelve functionality.

    This base class makes sure that all unit tests are executed in a sandbox
    environment.
    """

    SHELF_PATH = os.path.join('tests', '.shelf')
    REPOSITORY_URI = os.path.join('tests', '.repo')

    @classmethod
    def setUpClass(cls):
        """Makes sure that shelve will look for patches in the patches path in
        the test directory, and that the repository directory exists.
        """
        if not os.path.exists(cls.REPOSITORY_URI):
            os.mkdir(cls.REPOSITORY_URI)

        if not os.path.exists(cls.SHELF_PATH):
            os.mkdir(cls.SHELF_PATH)

        Shelf.SHELF_PATH = cls.SHELF_PATH

    @classmethod
    def tearDownClass(cls):
        """Cleans up the temporary patches path used for the unit tests."""
        if os.path.exists(cls.SHELF_PATH):
            shutil.rmtree(cls.SHELF_PATH)

        # Clean up the temporary repository.
        if os.path.exists(cls.REPOSITORY_URI):
            shutil.rmtree(cls.REPOSITORY_URI)

    def tearDown(self):
        """Removes all shelved patches."""
        for patch_name in os.listdir(self.SHELF_PATH):
            os.unlink(os.path.join(self.SHELF_PATH, patch_name))
