import os
import shutil
import subprocess

from nose.tools import assert_in, assert_equal, assert_not_in, assert_raises, assert_true

from stash import MercurialStash, Stash, StashException
from stash_test_case import StashTestCase

class TestMercurialStash(StashTestCase):

    PATCH_NAME = __name__
    SUB_DIRECTORY_NAME = 'sub'

    def setUp(self):
        # Initialize a Mercurial repository in the repository directory.
        subprocess.Popen('hg init', shell=True, cwd=self.REPOSITORY_URI).wait()

        # Create a few files that can be modified later on.
        for file_name in ['a', 'b', 'c']:
            file_name = os.path.join(self.REPOSITORY_URI, file_name)

            f = open(file_name, 'w')
            f.write('123')
            f.close()

            # Add the newly created file to the repository.
            subprocess.Popen('hg add %s' % file_name, shell=True).wait()

        # Create a subdirectory.
        sub_directory = os.path.join(self.REPOSITORY_URI, self.SUB_DIRECTORY_NAME)
        keep_file_name = os.path.join(sub_directory, '.keep')
        os.mkdir(sub_directory)
        open(keep_file_name, 'w').close()

        # Add the subdirectory to the repository.
        subprocess.Popen('hg add %s' % keep_file_name, shell=True).wait()

        # Finally, commit the changes.
        subprocess.Popen('hg ci -m "Initial commit." -u anonymous', shell=True, cwd=self.REPOSITORY_URI).wait()

    def tearDown(self):
        # Empty the repository directory.
        if os.path.exists(self.REPOSITORY_URI):
            for filename in os.listdir(self.REPOSITORY_URI):
                filename = os.path.join(self.REPOSITORY_URI, filename)
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.unlink(filename)

        super(TestMercurialStash, self).tearDown()

    def test_creating_stash_outside_repository_raises_exception(self):
        """Tests that creating a stash in case the current working directory
        does not point to a repository raises an exception.
        """
        assert_raises(StashException, Stash.create, self.PATCHES_PATH)

    def test_creating_stash_in_subdirectory(self):
        """Tests that creating a stash from within a subdirectory of a
        repository will properly find the repository root.
        """
        stash = Stash.create(os.path.join(self.REPOSITORY_URI, self.SUB_DIRECTORY_NAME))
        assert_equal(stash.repository_root, os.path.abspath(self.REPOSITORY_URI))

    def test_stash_and_apply_change(self):
        """Tests that it is possible to stash changes in a repository.
        """
        stash = Stash.create(self.REPOSITORY_URI)

        # Modify a committed file.
        file_name = os.path.join(self.REPOSITORY_URI, 'a')
        f = open(file_name, 'w+')
        f.write('321')
        f.close()

        # Create the patch.
        stash.create_patch(self.PATCH_NAME)
        assert_in(self.PATCH_NAME, stash.get_patches())

        # The file should contain the original contents.
        assert_equal(open(file_name, 'r').read(), '123')

        # Revert the changes to the file, and apply the patch to see whether we
        # get the expected result.
        stash.apply_patch(self.PATCH_NAME)

        # The file should contain the expected changes.
        assert_equal(open(file_name, 'r').read(), '321')

    def test_stash_and_apply_conflicting_change(self):
        """Test that applying a conflicting stashed patch results in a merged
        file.
        """
        stash = Stash.create(self.REPOSITORY_URI)

        # Modify a committed file.
        file_name = os.path.join(self.REPOSITORY_URI, 'a')
        f = open(file_name, 'w+')
        f.write('321')
        f.close()

        # Create the patch.
        stash.create_patch(self.PATCH_NAME)
        assert_in(self.PATCH_NAME, stash.get_patches())

        # The file should again contain the original contents.
        assert_equal(open(file_name, 'r').read(), '123')

        # Modify the file such that it contains conflicting changes.
        f = open(file_name, 'w+')
        f.write('456')
        f.close()

        # Revert the changes to the file, and apply the patch to see whether we
        # get the expected result.
        stash.apply_patch(self.PATCH_NAME)

        # The file should contain the expected changes.
        assert_equal(open(file_name, 'r').read(), '<<<<<<<\n=======\n321\n>>>>>>>\n456')

        # Since the patch did not apply cleanly, the patch is not removed and
        # should still be present.
        assert_in(self.PATCH_NAME, stash.get_patches())

    def test_stashing_added_file(self):
        """Test that stashing an added file will remove it, and again recreate
        it when applying the patch.
        """
        stash = Stash.create(self.REPOSITORY_URI)

        # Create a new file.
        file_name = os.path.join(self.REPOSITORY_URI, 'd')
        f = open(file_name, 'w+')
        f.write('123')
        f.close()

        # Add the file to the repository.
        subprocess.Popen('hg add %s' % file_name, shell=True).wait()

        # Create the patch.
        stash.create_patch(self.PATCH_NAME)
        assert_in(self.PATCH_NAME, stash.get_patches())

        # The newly created file should no longer exist.
        assert_true(not os.path.exists(file_name))

        # Apply the stashed patch, the file should exist again, and should have
        # been added to the repository.
        stash.apply_patch(self.PATCH_NAME)

        # The patch applied cleanly, so it should no longer exist.
        assert_not_in(self.PATCH_NAME, stash.get_patches())

    def test_stashing_removed_file(self):
        """Test that stashing a removed file will recreate it, and again remove
        it when applying the patch.
        """
        stash = Stash.create(self.REPOSITORY_URI)

        # Remove a file from the repository.
        file_name = os.path.join(self.REPOSITORY_URI, 'b')
        subprocess.Popen('hg remove %s' % file_name, shell=True).wait()
        assert_true(not os.path.exists(file_name))

        # Create the patch.
        stash.create_patch(self.PATCH_NAME)
        assert_in(self.PATCH_NAME, stash.get_patches())

        # The removed file should exist again.
        assert_true(os.path.exists(file_name))

        # Apply the stashed patch, the file should exist again, and should have
        # been added to the repository.
        stash.apply_patch(self.PATCH_NAME)

        # The file that was removed should again be removed.
        assert_true(not os.path.exists(file_name))

        # The patch applied cleanly, so it should no longer exist.
        assert_not_in(self.PATCH_NAME, stash.get_patches())
