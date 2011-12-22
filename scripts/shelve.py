#!python

import argparse
import os

from shelf import Shelf, ShelfException

parser = argparse.ArgumentParser(description='Shelve HG changes to the shelf directory (~/.shelf).')
parser.add_argument('-l', '--list', dest='show_list', action='store_true', help='list all currently shelved patches')
parser.add_argument('-r', '--remove', dest='remove_patch', action='store_true', \
        help='remove the specified patch from the shelf')
parser.add_argument('-s', '--show', dest='show_patch', action='store_true', \
        help='shows the contents of the specified patch from the shelf')
parser.add_argument('-a', '--apply', dest='apply_patch', action='store_true', \
        help='apply the specified patch in the shelf, and remove it in case it applied successfully')
parser.add_argument('patch_name', nargs='?', metavar='<patch name>', help='name of the patch to operate on')

args = parser.parse_args()

try:
    if args.show_list:
        for patch in Shelf.get_patches():
            print patch
    elif args.remove_patch:
        Shelf.remove_patch(args.patch_name)
        print("Patch '%s' successfully removed." % args.patch_name)
    elif args.show_patch:
        print Shelf.get_patch(args.patch_name)
    elif args.patch_name is not None:
        shelf = Shelf.create(os.getcwd())
        if args.apply_patch:
            shelf.apply_patch(args.patch_name)
        else:
            # Check if patch already exists, if it does, issue a warning and
            # give the user an option to overwrite the patch.
            while args.patch_name in shelf.get_patches():
                yes_no_answer = input("Warning, patch '%s' already exists, overwrite [Y/n]? " % args.patch_name)
                if not yes_no_answer or yes_no_answer.lower() == 'y':
                    shelf.remove_patch(args.patch_name)
                elif yes_no_answer.lower() == 'n':
                    args.patch_name = None
                    while not args.patch_name:
                        args.patch_name = input("Please provide a different patch name: ")

            shelf.create_patch(args.patch_name)
    else:
        parser.print_help()
except ShelfException as e:
    print("Error: %s." % e)
