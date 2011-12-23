Shelve command-line tool
------------------------

This shelve command-line tool ``shelve.py`` supports shelving changes for
Mercurial and Subversion (1.7.x+) repositories similar to ``git stash``.  One
major difference with ``git stash`` is that changes are not stored in a stack,
but rather as a named patch in a predefined location (``~/.shelf``).

Shelve allows to user to temporarily shelve all changes in a dirty working
directory away to the shelf. All changes in the repository are reverted, and the
repository is back in a clean state.

Usage
=====

To temporarily shelve all changes including all added and removed files in a
repository issue:

.. code-block:: none

    $ shelve.py <patch name>

``<patch name>`` is a user-defined name that describes the contents of the
patch. In case a patch with the given name already exists, shelve will ask to
user to either overwrite the existing patch, or specify an alternative name for
the patch. The shelve command can be issued from any path within a repository,
provided it is either a Mercurial or Subversion respository.

All changes that are shelved in this way can be inspected using ``shelve.py
-l``, and shown using ``shelve.py -s <patch name>``.

Changes that were previously saved can be restored again using ``shelve.py -a
<patch name>``,  potentially on top of a different commit. In case the changes
applied cleanly to the current repository, the entry for the patch is
automatically removed from the shelf.  Otherwise, the files will be merged in
place (similar to ``merge``), and the patch will remain in the shelf.

For more information on the usage of shelve:

.. code-block:: none

    $ shelve.py -h

Bash completion support
=======================

When installing shelve, a command-line completion script is automatically
installed to ``/etc/bash_completion.d``. This provides support for auto
completing patch names in Bash.
