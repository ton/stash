import os
import subprocess

from shelf.exception import ShelfException
from shelf.repository import Repository

class Shelf(object):
    """This class manages the collection of patches that have been shelved from
    various repositories. It provides functionality to list all available
    patches, to add, remove, and show individual patches, as well as applying
    shelved patches on a repository.
    """

    SHELF_PATH = os.path.expanduser('~/.shelf')

    def __init__(self, path):
        """To instantiantate a shelf, provide a path that points to a location
        somewhere in a repository.
        """
        # Check if the patches path exists, and in case it does not, create it.
        if not os.path.exists(self.SHELF_PATH):
            os.mkdir(self.SHELF_PATH)

        self.repository = Repository(path)

        super(Shelf, self).__init__()

    @classmethod
    def _get_patch_path(cls, patch_name):
        """Returns the absolute path for patch *patch_name*."""
        return os.path.join(cls.SHELF_PATH, patch_name) if patch_name else None

    @classmethod
    def get_patches(cls):
        """Returns the names of all shelved patches."""
        return os.listdir(cls.SHELF_PATH)

    @classmethod
    def remove_patch(cls, patch_name):
        """Removes patch *patch_name* from the shelf (in case it exists).

        :raises: :py:exc:`~shelf.exception.ShelfException` in case *patch_name* does not exist.
        """
        try:
            os.unlink(cls._get_patch_path(patch_name))
        except:
            raise ShelfException("patch '%s' does not exist" % patch_name)

    @classmethod
    def get_patch(cls, patch_name):
        """Returns the contents of the specified patch *patch_name*.

        :raises: :py:exc:`~shelf.exception.ShelfException` in case *patch_name* does not exist.
        """
        try:
            return open(cls._get_patch_path(patch_name), 'r').read()
        except:
            raise ShelfException("patch '%s' does not exist" % patch_name)

    def apply_patch(self, patch_name):
        """Applies the patch *patch_name* on to the current working directory in
        case the patch exists. In case applying the patch was successfull, the
        patch is automatically removed from the shelf.

        :raises: :py:exc:`~shelf.exception.ShelfException` in case *patch_name* does not exist.
        """
        if patch_name in self.get_patches():
            pre_file_status = self.repository.status()

            # Apply the patch, and merge with local changes.
            patch_return_code = self.repository.apply_patch(self._get_patch_path(patch_name))

            post_file_status = self.repository.status()
            changed_file_status = post_file_status.difference(pre_file_status)

            # Determine all files that have been added.
            added_files = []
            for status_line in changed_file_status:
                if status_line[0] == '?':
                    added_files.append(status_line[2:])

            # Determine all files that have been removed.
            removed_files = []
            for status_line in changed_file_status:
                if status_line[0] == '!':
                    removed_files.append(status_line[2:])

            # Add and remove all files that have been marked as added or removed
            # respectively.
            if added_files:
                self.repository.add(added_files)
            if removed_files:
                self.repository.remove(removed_files)

            if patch_return_code == 0:
                # Applying the patch succeeded, remove shelved patch.
                print("Applying patch '%s' succeeded, removing shelved patch." % patch_name)
                os.unlink(self._get_patch_path(patch_name))
            else:
                # The patch did not apply cleanly, inform the user that the
                # patch will not be removed.
                print("Patch '%s' did not apply successfully, shelved patch will not be removed." % patch_name)
        else:
            raise ShelfException("patch '%s' does not exist" % patch_name)

    def create_patch(self, patch_name):
        """Creates a patch based on the changes in the current repository. In
        case the specified patch *patch_name* already exists, ask the user to
        overwrite the patch. In case creating the patch was successfull, all
        changes in the current repository are reverted.

        :raises: :py:exc:`~shelf.exception.ShelfException` in case *patch_name* already exists.
        """
        # Raise an exception in case the specified patch already exists.
        patch_path = self._get_patch_path(patch_name)
        if os.path.exists(patch_path):
            raise ShelfException("patch '%s' already exists" % patch_name)

        # Determine the contents for the new patch.
        patch = self.repository.diff()

        if patch:

            # Create the patch.
            patch_file = open(patch_path, 'wb')
            patch_file.write(patch.encode('utf-8'))
            patch_file.close()

            pre_file_status = self.repository.status()

            self.repository.revert_all()
            print("Done shelving changes for patch '%s'." % patch_name)

            post_file_status = self.repository.status()
            changed_file_status = post_file_status.difference(pre_file_status)

            # Remove all files that are created by the patch that is now being
            # shelved.
            added_files = []
            for status_line in changed_file_status:
                if status_line[0] == '?':
                    os.unlink(os.path.join(self.repository.root_path, status_line[2:]))
        else:
            print("No changes in repository, patch '%s' not created." % patch_name)
