import os
import subprocess

from exception import StashException
from repository import Repository, FileStatus

class Stash(object):
    """This class manages the collection of patches that have been stashed from
    various repositories. It provides functionality to list all available
    patches, to add, remove, and show individual patches, as well as applying
    stashed patches on a repository.
    """

    STASH_PATH = os.path.expanduser('~/.stash')

    def __init__(self, path):
        """To instantiantate a stash, provide a path that points to a location
        somewhere in a repository.
        """
        # Check if the patches path exists, and in case it does not, create it.
        if not os.path.exists(self.STASH_PATH):
            os.mkdir(self.STASH_PATH)

        self.repository = Repository(path)

        super(Stash, self).__init__()

    @classmethod
    def _get_patch_path(cls, patch_name):
        """Returns the absolute path for patch *patch_name*."""
        return os.path.join(cls.STASH_PATH, patch_name) if patch_name else None

    @classmethod
    def get_patches(cls):
        """Returns the names of all stashed patches."""
        return sorted(os.listdir(cls.STASH_PATH))

    @classmethod
    def remove_patch(cls, patch_name):
        """Removes patch *patch_name* from the stash (in case it exists).

        :raises: :py:exc:`~stash.exception.StashException` in case *patch_name* does not exist.
        """
        try:
            os.unlink(cls._get_patch_path(patch_name))
        except:
            raise StashException("patch '%s' does not exist" % patch_name)

    @classmethod
    def get_patch(cls, patch_name):
        """Returns the contents of the specified patch *patch_name*.

        :raises: :py:exc:`~stash.exception.StashException` in case *patch_name* does not exist.
        """
        try:
            return open(cls._get_patch_path(patch_name), 'r').read()
        except:
            raise StashException("patch '%s' does not exist" % patch_name)

    def apply_patch(self, patch_name):
        """Applies the patch *patch_name* on to the current working directory in
        case the patch exists. In case applying the patch was successful, the
        patch is automatically removed from the stash. Returns ``True`` in case
        applying the patch was successful, otherwise ``False`` is returned.

        :raises: :py:exc:`~stash.exception.StashException` in case *patch_name* does not exist.
        """
        if patch_name in self.get_patches():
            patch_path = self._get_patch_path(patch_name)

            # Apply the patch, and determine the files that have been added and
            # removed.
            pre_file_status = self.repository.status()
            patch_return_code = self.repository.apply_patch(patch_path)
            changed_file_status = self.repository.status().difference(pre_file_status)

            # Determine all files that have been added.
            for status, file_name in changed_file_status:
                if status == FileStatus.Added:
                    self.repository.add([file_name])
                elif status == FileStatus.Removed:
                    self.repository.remove([file_name])

            if patch_return_code == 0:
                # Applying the patch succeeded, remove stashed patch.
                os.unlink(patch_path)

            return patch_return_code == 0
        else:
            raise StashException("patch '%s' does not exist" % patch_name)

    def create_patch(self, patch_name):
        """Creates a patch based on the changes in the current repository. In
        case the specified patch *patch_name* already exists, ask the user to
        overwrite the patch. In case creating the patch was successful, all
        changes in the current repository are reverted. Returns ``True`` in case
        a patch was created, and ``False`` otherwise.

        :raises: :py:exc:`~stash.exception.StashException` in case *patch_name* already exists.
        """
        # Raise an exception in case the specified patch already exists.
        patch_path = self._get_patch_path(patch_name)
        if os.path.exists(patch_path):
            raise StashException("patch '%s' already exists" % patch_name)

        # Determine the contents for the new patch.
        patch = self.repository.diff()
        if patch != '':
            # Create the patch.
            patch_file = open(patch_path, 'wb')
            patch_file.write(patch.encode('utf-8'))
            patch_file.close()

            # Undo all changes in the repository, and determine which files have
            # been added or removed. Files that were added, need to be removed
            # again.
            pre_file_status = self.repository.status()
            self.repository.revert_all()
            changed_file_status = self.repository.status().difference(pre_file_status)

            # Remove all files that are created by the patch that is now being
            # stashed.
            for status, file_name in changed_file_status:
                if status == FileStatus.Added:
                    os.unlink(os.path.join(self.repository.root_path, file_name))

        # Return whether a non-empty patch was created.
        return patch != ''
