import os
import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path
import time
import multiprocessing
from multiprocessing import Pool
import platform

from win32_setctime import setctime
from exif import Image


# to modify time modified: setctime("my_file.txt", 1561675987.509)
# to modify time created: os.utime("a2.py",(1330712280, 1330712292))
def load_json(dir_val):
    with open(dir_val) as f:
        return json.load(f)


def dump_json(location, db):
    with open(location, "w") as f:
        json.dump(db, f, indent=4)


if __name__ == '__main__':
    # get the path relative to the .py file itself
    source_path = Path(__file__).resolve()
    source_dir = str(source_path.parent).replace(os.sep, '/')

    original_library_dir = input('name of original library to read from: ')
    new_library_dir = input('name of new library to read from: ')

    original_lib = load_json(original_library_dir)
    new_lib = load_json(new_library_dir)

    print('successfully read JSON files into memory...')

    # for loop here for now since i need to update read_library.py
    # sort original library by hash
    sorted_original_lib = {}
    for file_dir, file in original_lib.items():
        hashed_val = file['hash']
        date_modified = file['m']
        date_created = file['c']
        sorted_original_lib[hashed_val] = {'dir': file_dir, 'm': date_modified, 'c': date_created}

    # sort new library by hash
    sorted_new_lib = {}
    for file_dir, file in new_lib.items():
        hashed_val = file['hash']
        date_modified = file['m']
        date_created = file['c']
        sorted_new_lib[hashed_val] = {'dir': file_dir, 'm': date_modified, 'c': date_created}

    missing_from_new_lib = {}
    check_for_missing = input(
        'finished sorting original lib, would you like us to scan and see if there are any files in the original lib that are missing from the new lib?')
    if check_for_missing == 'y':
        for orig_file_hash, orig_file in sorted_original_lib.items():
            if orig_file_hash not in sorted_new_lib.keys():
                missing_from_new_lib[orig_file['dir']] = orig_file_hash

    # create new merged lib
    merged_library = {}
    stats = {'errors': [], 'duplicates': [], 'singles': [], 'pairs': 0}

    for file_hash, new_file in sorted_new_lib.items():
        date_modified = new_file['m']
        date_created = new_file['c']
        if file_hash in sorted_original_lib.keys():
            stats['pairs'] += 1
            orig = sorted_original_lib[file_hash]
            merged_library[new_file['dir']] = {'m': orig['m'], 'c': orig['c'], 'hash': file_hash}
        else:
            stats['singles'].append(new_file['dir'])

    print(stats)
    dump_json(input('name of file to save to?'), merged_library)
    print('done')
    print('these files were missing from the new library: ')
    print(missing_from_new_lib)
    print(f'total number of missing files from new library is {len(sorted_original_lib) - len(sorted_new_lib)}')

    # now ask user if they want to continue modifying all files in new library to fix metadata:
    fix_now = input('do you now want to fix the new library?')
    if fix_now:
        pass