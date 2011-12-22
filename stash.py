import argparse
import os
import subprocess

def enum(*sequential, **named):
  """Utility function to create named or automatically numbered enumeration
  types.

  Use like this::

    Vehicles = enum(CAR=1, PLANE=2, HOVERCRAFT=1337)
    Animals = enum('CAT', 'DOG', 'PARAKEET')

    vehicle = Vehicles.HOVERCRAFT
    animal = Animals.PARAKEET
  """
  enums = dict(zip(sequential, range(len(sequential))), **named)

  return type('Enum', (), enums)

RepositoryTypes = enum(
  MERCURIAL = 'Mercurial'
  )
"""Enumeration type for the supported repository types.

  * ``MERCURIAL = 'Mercurial'``
"""

# Ensure Python 2.x compatability.
try: input = raw_input
except: pass

class StashException(Exception):
    pass

class Stash(object):

    PATCHES_PATH = os.path.expanduser('~/.patches')

    def __init__(self, repository_root):
        # Check if the patches path exists, and in case it does not, create it.
        if not os.path.exists(self.PATCHES_PATH):
            os.mkdir(self.PATCHES_PATH)

        self.repository_root = repository_root

    @classmethod
    def create(cls, path):
        # Determine the repository type, and the root directory for the
        # repository.
        (repository_root, repository_type) = cls._get_repository_path_and_type(path)

        if repository_type == RepositoryTypes.MERCURIAL:
            return MercurialStash(repository_root)

    @classmethod
    def _get_patch_path(cls, patch_name):
        """Returns the absolute path for patch *patch_name*."""
        return os.path.join(cls.PATCHES_PATH, patch_name) if patch_name else None

    @classmethod
    def _get_repository_path_and_type(cls, path):
        """Returns a tuple of the root directory and type of the repository
        located at *path*.

        :raises: :py:exc:`~StashException` in case no repository was found.
        """
        # Look at the directories present in the current working directory. In case
        # a .hg directory is present, we know we are in the root directory of a
        # Mercurial repository. In case no repository specific folder is found, and
        # the current directory has a parent directory, look if a repository
        # specific directory can be found in the parent directory.
        while path != '/':
            if '.hg' in os.listdir(path):
                return (path, RepositoryTypes.MERCURIAL)
            path = os.path.abspath(os.path.join(path, os.pardir))
        raise StashException("no valid repository found")

    @classmethod
    def get_patches(cls):
        """Returns the names of all currently stashed patches."""
        return os.listdir(cls.PATCHES_PATH)

    @classmethod
    def remove_patch(cls, patch_name):
        """Removes patch *patch_name* from the stash (in case it exists).

        :raises: :py:exc:`~StashException` in case *patch_name* does not exist.
        """
        try:
            os.unlink(cls._get_patch_path(patch_name))
        except:
            raise StashException("patch '%s' does not exist" % patch_name)

    @classmethod
    def get_patch(cls, patch_name):
        """Returns the contents of the specified patch *patch_name*.

        :raises: :py:exc:`~StashException` in case *patch_name* does not exist.
        """
        try:
            return open(cls._get_patch_path(patch_name), 'r').read()
        except:
            raise StashException("patch '%s' does not exist" % patch_name)

    def run(self, command_line, stdin=None, silent=False):
        """Returns a tuple representing the return code and the resulting output
        after running the specified *command_line*. All input for
        the process can be specified using *stdin*. In case *silent*
        is ``True``, all output of the process is redirected to /dev/null, and
        ``None`` is returned for the process output.
        """
        if silent:
            fnull = open(os.devnull, 'w')
            return (subprocess.Popen(command_line, shell=True, stdin=stdin, stdout=fnull, stderr=fnull, cwd=self.repository_root).wait(), None)
        else:
            p = subprocess.Popen(command_line, shell=True, stdin=stdin, stdout=subprocess.PIPE, cwd=self.repository_root)
        return (p.wait(), p.communicate()[0].decode('utf-8'))

class MercurialStash(Stash):

    def apply_patch(self, patch_name):
        """Applies the patch *patch_name* on to the current working directory in
        case the patch exists. In case applying the patch was successfull, the
        patch is automatically removed from the stash.

        :raises: :py:exc:`~StashException` in case *patch_name* does not exist.
        """
        if patch_name in self.get_patches():
            pre_file_status = set(self.run('hg stat')[1].splitlines())

            # Apply the patch, and merge with local changes.
            (patch_returncode, _) = self.run('patch -p1 --no-backup-if-mismatch --merge', stdin=open(self._get_patch_path(patch_name), 'r'))

            post_file_status = set(self.run('hg stat')[1].splitlines())
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
                self.run('hg add %s' % (' '.join(added_files)))
            if removed_files:
                self.run('hg rm %s' % (' '.join(removed_files)))

            if patch_returncode == 0:
                # Applying the patch succeeded, remove stashed patch.
                print("Applying patch '%s' succeeded, removing stashed patch." % patch_name)
                os.unlink(self._get_patch_path(patch_name))
            else:
                # The patch did not apply cleanly, inform the user that the
                # patch will not be removed.
                print("Patch '%s' did not apply successfully, stashed patch will not be removed." % patch_name)
        else:
            raise StashException("patch '%s' does not exist" % patch_name)

    def create_patch(self, patch_name):
        """Creates a patch based on the changes in the current repository. In
        case the specified patch *patch_name* already exists, ask the user to
        overwrite the patch. In case creating the patch was successfull, all
        changes in the current repository are reverted.
        """
        # Determine the contents for the new patch.
        (diff_process_return_code, patch) = self.run('hg diff -a')

        if diff_process_return_code == 0 and patch:
            # Check if patch already exists, if it does, issue a warning and
            # give the user an option to overwrite the patch.
            patch_path = self._get_patch_path(patch_name)
            while os.path.exists(patch_path):
                yes_no_answer = input("Warning, patch '%s' already exists, overwrite [Y/n]? " % patch_name)
                if not yes_no_answer or yes_no_answer.lower() == 'y':
                    os.unlink(patch_path)
                elif yes_no_answer.lower() == 'n':
                    patch_name = None
                    while not patch_name:
                        patch_name = input("Please provide a different patch name: ")
                    patch_path = self._get_patch_path(patch_name)

            # Create the patch.
            patch_file = open(patch_path, 'wb')
            patch_file.write(patch.encode('utf-8'))
            patch_file.close()

            pre_file_status = set(self.run('hg stat')[1].splitlines())

            if diff_process_return_code == 0:
                self.run('hg revert -C --all', silent=True)
                print("Done stashing changes for patch '%s'." % patch_name)

            post_file_status = set(self.run('hg stat')[1].splitlines())
            changed_file_status = post_file_status.difference(pre_file_status)

            # Remove all files that are created by the patch that is now being
            # stashed.
            added_files = []
            for status_line in changed_file_status:
                if status_line[0] == '?':
                    os.unlink(os.path.join(self.repository_root, status_line[2:]))
        else:
            print("No changes to stash, patch '%s' not created." % patch_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stash HG changes to the patch directory (~/.patches).')
    parser.add_argument('-l', '--list', dest='show_list', action='store_true', help='list all currently stashed patches')
    parser.add_argument('-r', '--remove', dest='remove_patch', action='store_true', \
            help='remove the specified patch from the stash')
    parser.add_argument('-s', '--show', dest='show_patch', action='store_true', \
            help='shows the contents of the specified patch from the stash')
    parser.add_argument('-a', '--apply', dest='apply_patch', action='store_true', \
            help='apply the specified patch in the stash, and remove it in case it applied successfully')
    parser.add_argument('patch_name', nargs='?', metavar='<patch name>', help='name of the patch to operate on')

    args = parser.parse_args()

    try:
        if args.show_list:
            for patch in Stash.get_patches():
                print patch
        elif args.remove_patch:
            Stash.remove_patch(args.patch_name)
            print("Patch '%s' successfully removed." % patch_name)
        elif args.show_patch:
            print Stash.get_patch(args.patch_name)
        elif args.patch_name is not None:
            stash = Stash.create(os.getcwd())
            if args.apply_patch:
                stash.apply_patch(args.patch_name)
            else:
                stash.create_patch(args.patch_name)
        else:
            parser.print_help()
    except StashException as e:
        print("Error: %s." % e)
