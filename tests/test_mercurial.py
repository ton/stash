import os
import shutil
import subprocess

from nose.tools import assert_in, assert_equal, assert_not_in, assert_raises, assert_true

from shelf.exception import ShelfException
from shelf.repository import MercurialRepository
from shelf.shelf import Shelf
from shelf.test_case import ShelfTestCase

class TestRepository(ShelfTestCase):

    PATCH_NAME = __name__
    SUB_DIRECTORY_NAME = 'sub'

    # This is a mixin class that should not be executed on its own.
    __test__ = False

    def setUp(self):
        # Create a few files that can be modified later on.
        file_names = ['a', 'b', 'c']
        for file_name in file_names:
            file_name = os.path.join(self.REPOSITORY_URI, file_name)

            f = open(file_name, 'w')
            f.write('123')
            f.close()

        self.repository.add(file_names)

        # Create a subdirectory.
        sub_directory = os.path.join(self.REPOSITORY_URI, self.SUB_DIRECTORY_NAME)
        keep_file_name = os.path.join(sub_directory, '.keep')
        os.mkdir(sub_directory)
        open(keep_file_name, 'w').close()

        # Add the subdirectory to the repository.
        self.repository.add([os.path.join(self.SUB_DIRECTORY_NAME, '.keep')])

        # Finally, commit the changes.
        self.repository.commit('Initial commit.')

    def tearDown(self):
        # Empty the repository directory.
        if os.path.exists(self.REPOSITORY_URI):
            for filename in os.listdir(self.REPOSITORY_URI):
                filename = os.path.join(self.REPOSITORY_URI, filename)
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.unlink(filename)

        super(TestRepository, self).tearDown()

    def test_creating_patch_outside_repository_raises_exception(self):
        """Tests that creating a patch in case the current working directory
        does not point to a repository raises an exception.
        """
        assert_raises(ShelfException, Shelf, self.SHELF_PATH)

    def test_creating_patch_in_subdirectory(self):
        """Tests that creating a patch from within a subdirectory of a
        repository will properly find the repository root.
        """
        shelf = Shelf(os.path.join(self.REPOSITORY_URI, self.SUB_DIRECTORY_NAME))
        assert_equal(shelf.repository.root_path, os.path.abspath(self.REPOSITORY_URI))

    def test_shelve_and_apply_change(self):
        """Tests that it is possible to shelve changes in a repository.
        """
        shelf = Shelf(self.REPOSITORY_URI)

        # Modify a committed file.
        file_name = os.path.join(self.REPOSITORY_URI, 'a')
        f = open(file_name, 'w+')
        f.write('321')
        f.close()

        # Create the patch.
        shelf.create_patch(self.PATCH_NAME)
        assert_in(self.PATCH_NAME, shelf.get_patches())

        # The file should contain the original contents.
        assert_equal(open(file_name, 'r').read(), '123')

        # Revert the changes to the file, and apply the patch to see whether we
        # get the expected result.
        shelf.apply_patch(self.PATCH_NAME)

        # The file should contain the expected changes.
        assert_equal(open(file_name, 'r').read(), '321')

    def test_shelve_and_apply_conflicting_change(self):
        """Test that applying a conflicting patch results in a merged file.
        """
        shelf = Shelf(self.REPOSITORY_URI)

        # Modify a committed file.
        file_name = os.path.join(self.REPOSITORY_URI, 'a')
        f = open(file_name, 'w+')
        f.write('321')
        f.close()

        # Create the patch.
        shelf.create_patch(self.PATCH_NAME)
        assert_in(self.PATCH_NAME, shelf.get_patches())

        # The file should again contain the original contents.
        assert_equal(open(file_name, 'r').read(), '123')

        # Modify the file such that it contains conflicting changes.
        f = open(file_name, 'w+')
        f.write('456')
        f.close()

        # Revert the changes to the file, and apply the patch to see whether we
        # get the expected result.
        shelf.apply_patch(self.PATCH_NAME)

        # The file should contain the expected changes.
        assert_equal(open(file_name, 'r').read(), '<<<<<<<\n=======\n321\n>>>>>>>\n456')

        # Since the patch did not apply cleanly, the patch is not removed and
        # should still be present.
        assert_in(self.PATCH_NAME, shelf.get_patches())

    def test_shelving_added_file(self):
        """Test that shelving an added file will remove it, and again recreate
        it when applying the patch.
        """
        shelf = Shelf(self.REPOSITORY_URI)

        # Create a new file.
        file_name = os.path.join(self.REPOSITORY_URI, 'd')
        f = open(file_name, 'w+')
        f.write('123')
        f.close()

        # Add the file to the repository.
        shelf.repository.add(['d'])

        # Create the patch.
        shelf.create_patch(self.PATCH_NAME)
        assert_in(self.PATCH_NAME, shelf.get_patches())

        # The newly created file should no longer exist.
        assert_true(not os.path.exists(file_name))

        # Apply the patch, the file should exist again, and should have been
        # added to the repository.
        shelf.apply_patch(self.PATCH_NAME)

        # The patch applied cleanly, so it should no longer exist.
        assert_not_in(self.PATCH_NAME, shelf.get_patches())

    def test_shelving_removed_file(self):
        """Test that shelving a removed file will recreate it, and again remove
        it when applying the patch.
        """
        shelf = Shelf(self.REPOSITORY_URI)

        # Remove a file from the repository.
        file_name = os.path.join(self.REPOSITORY_URI, 'b')
        shelf.repository.remove(['b'])
        assert_true(not os.path.exists(file_name))

        # Create the patch.
        shelf.create_patch(self.PATCH_NAME)
        assert_in(self.PATCH_NAME, shelf.get_patches())

        # The removed file should exist again.
        assert_true(os.path.exists(file_name))

        # Apply the patch, the file should exist again, and should have been
        # added to the repository.
        shelf.apply_patch(self.PATCH_NAME)

        # The file that was removed should again be removed.
        assert_true(not os.path.exists(file_name))

        # The patch applied cleanly, so it should no longer exist.
        assert_not_in(self.PATCH_NAME, shelf.get_patches())

    def test_shelving_existing_patch_raises_exception(self):
        """Test that shelving an already existing patch raises an exception."""
        shelf = Shelf(self.REPOSITORY_URI)

        # Create a bogus patch.
        open(os.path.join(self.SHELF_PATH, self.PATCH_NAME), 'w').close()

        # Modify a file, and create a patch that conflicts with the already
        # existing patch.
        file_name = os.path.join(self.REPOSITORY_URI, 'a')
        f = open(file_name, 'w+')
        f.write('321')
        f.close()

        # Creating a patch with an existing name should raise an exception.
        assert_raises(ShelfException, shelf.create_patch, self.PATCH_NAME)

class TestMercurialRepository(TestRepository):

    # Make sure to execute this test case.
    __test__ = True

    def setUp(self):
        # Initialize a Mercurial repository in the repository directory.
        self.repository = MercurialRepository(self.REPOSITORY_URI, create=True)

        super(TestMercurialRepository, self).setUp()
