Introduction
------------

This script supports shelving changes for Mercurial repositories similar to `git
stash`. One major difference with `git stash` is that changes are not stored in
a stack, but rather as a named patch in a predefined location (`~/.shelf`).

Usage
-----

The following is a listing of the help instructions from `shelve`::

    usage: shelve.py [-h] [-l] [-r] [-s] [-a] [<patch name>]

    Stash HG changes to the patch directory (~/.shelf).

    positional arguments:
    <patch name>  name of the patch to operate on

    optional arguments:
    -h, --help    show this help message and exit
    -l, --list    list all currently shelved patches
    -r, --remove  remove the specified patch from the shelf
    -s, --show    shows the contents of the specified patch from the shelf
    -a, --apply   apply the specified patch in the shelf, and remove it in case
                  it applied successfully

Note that in case applying a patch causes a conflict, the patch will be merged
into the original conflicting file similar to `merge`. For more information, see
the man page of `patch`, specifically the description of the `--merge` command
line option.

Bash completion support
-----------------------

To get support for auto completing patch names in BASH, make sure that the
`shelve-completion.bash` script is sourced in your `.bashrc` or something
similar, and that you execute the shelve script by directly executing
`shelve.py`.
