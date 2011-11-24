#!/usr/bin/env python

import argparse
import os
import subprocess

def run(command_line, stdin=None, silent=False):
    """Returns a tuple representing the return code and the resulting output
    after running the specified *command_line*. All input for
    the process can be specified using *stdin*. In case *silent*
    is ``True``, all output of the process is redirected to /dev/null, and
    ``None`` is returned for the process output.
    """
    if silent:
        fnull = open(os.devnull, 'w')
        return (subprocess.Popen(command_line, shell=True, stdin=stdin, stdout=fnull, stderr=fnull).wait(), None)
    else:
        p = subprocess.Popen(command_line, shell=True, stdin=stdin, stdout=subprocess.PIPE)
        return (p.wait(), p.communicate()[0])

class StashException(Exception):
    pass

class Stash(object):

    def __init__(self):
        # Check if the patches path exists, and in case it does not, create it.
        self.patches_path = os.path.expanduser('~/.patches')
        if not os.path.exists(self.patches_path):
            os.mkdir(self.patches_path)

        self.patches = os.listdir(self.patches_path)

    def _get_patch_path(self, patch_name):
        """Returns the absolute path for patch *patch_name*."""
        return os.path.join(self.patches_path, patch_name) if patch_name else None

    def list_patches(self):
        """Prints a list of all patches present in the current stash."""
        for patch in self.patches:
            print patch

    def show_patch(self, patch_name):
        """Prints the specified patch *patch_name* to standard out."""
        if patch_name in self.patches:
            print open(self._get_patch_path(patch_name), 'r').read()
        else:
            raise StashException("patch '%s' does not exist" % patch_name)

class MercurialStash(Stash):

    def apply_patch(self, patch_name):
        """Applies the patch *patch_name* on to the current working directory in
        case the patch exists. In case applying the patch was successfull, the
        patch is automatically removed from the stash.
        """
        if patch_name in self.patches:
            pre_file_status = set(run('hg stat')[1].splitlines())

            # Apply the patch, and merge with local changes.
            (patch_returncode, _) = run('patch -p1 --merge', stdin=open(self._get_patch_path(patch_name), 'r'))

            post_file_status = set(run('hg stat')[1].splitlines())
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
                run('hg add %s' % (' '.join(added_files)))
            if removed_files:
                run('hg rm %s' % (' '.join(removed_files)))

            if patch_returncode == 0:
                # Applying the patch succeeded, remove stashed patch.
                print "Applying patch '%s' succeeded, removing stashed patch." % patch_name
                os.unlink(self._get_patch_path(patch_name))
            else:
                # The patch did not apply cleanly, inform the user that the
                # patch will not be removed.
                print "Patch '%s' did not apply successfully, stashed patch will not be removed." % patch_name
        else:
            raise StashException("patch '%s' does not exist" % patch_name)

    def remove_patch(self, patch_name):
        """Removes patch *patch_name* from the stash (in case it exists)."""
        if patch_name in self.patches:
            os.unlink(self._get_patch_path(patch_name))
        else:
            raise StashException("patch '%s' does not exist" % patch_name)

    def create_patch(self, patch_name):
        """Creates a patch based on the changes in the current repository. In
        case the specified patch *patch_name* already exists, ask the user to
        overwrite the patch. In case creating the patch was successfull, all
        changes in the current repository are reverted.
        """
        # Determine the contents for the new patch.
        (diff_process_return_code, patch) = run('hg diff -a')

        if diff_process_return_code == 0 and patch:
            # Check if patch already exists, if it does, issue a warning and
            # give the user an option to overwrite the patch.
            patch_path = self._get_patch_path(patch_name)
            while os.path.exists(patch_path):
                yes_no_answer = raw_input("Warning, patch '%s' already exists, overwrite [Y/n]? " % patch_name)
                if not yes_no_answer or yes_no_answer.lower() == 'y':
                    os.unlink(patch_path)
                elif yes_no_answer.lower() == 'n':
                    patch_name = None
                    while not patch_name:
                        patch_name = raw_input("Please provide a different patch name: ")
                    patch_path = self._get_patch_path(patch_name)

            # Create the patch.
            patch_file = open(patch_path, 'w')
            patch_file.write(patch)
            patch_file.close()

            pre_file_status = set(run('hg stat')[1].splitlines())

            if diff_process_return_code == 0:
                run('hg revert --all', silent=True)
                print "Done stashing changes for patch '%s'." % patch_name

            post_file_status = set(run('hg stat')[1].splitlines())
            changed_file_status = post_file_status.difference(pre_file_status)

            # Remove all files that are created by the patch that is now being
            # stashed.
            added_files = []
            for status_line in changed_file_status:
                if status_line[0] == '?':
                    os.unlink(status_line[2:])
        else:
            print "No changes to stash, patch '%s' not created." % patch_name

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
        stash = MercurialStash()
        if args.show_list:
            stash.list_patches()
        elif args.patch_name is not None:
            if args.remove_patch:
                stash.remove_patch(args.patch_name)
            elif args.show_patch:
                stash.show_patch(args.patch_name)
            elif args.apply_patch:
                stash.apply_patch(args.patch_name)
            else:
                stash.create_patch(args.patch_name)
        else:
            parser.print_help()
    except StashException as e:
        print "Error: %s." % e