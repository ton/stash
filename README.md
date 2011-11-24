# Introduction

This script supports stashing changes for Mercurial repositories à la `git stash`. The only difference with `git stash`
is that changes are not stored in a stack, but rather as a named patch in a predefined location (`~/.patches`).
location is hardcoded to `~/.patches`.

# Usage

The following is a listing of the help instructions from `stash`:

    usage: stash.py [-h] [-l] [-r] [-s] [-a] [<patch name>]

    Stash HG changes to the patch directory (~/.patches).

    positional arguments:
    <patch name>  name of the patch to operate on

    optional arguments:
    -h, --help    show this help message and exit
    -l, --list    list all currently stashed patches
    -r, --remove  remove the specified patch from the stash
    -s, --show    shows the contents of the specified patch from the stash
    -a, --apply   apply the specified patch in the stash, and remove it in case
                  it applied successfully

Note that in case applying a patch causes a conflict, the patch will be merged into the original conflicting file
similar to `merge`. For more information, see the man page of `patch`, specifically the description of the `--merge`
command line option.
