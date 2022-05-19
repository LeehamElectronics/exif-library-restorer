#!/usr/bin/python3
# exif-library-restorer
# built by leeham 2022 library_statistics

########################################################################################################################
#                                                 What it does                                                         #
########################################################################################################################
# this script reads your two json files generated with the read_library.py script, one json file is for your original
# library, and the other file is for your new library. This script will show you some statistics about your two
# libraries, it will also ask if you want to record / delete any duplicates in your new library, and of course
# replace all the 'date modified' metadata in your new library with your old library files.

import os
import json
import time
from pathlib import Path


def load_json(dir_val):
    with open(dir_val) as f:
        return json.load(f)


def dump_json(location, db):
    with open(location, "w") as f:
        json.dump(db, f, indent=4)


def show_file_ext_stats(library_db):
    lib_ext_dict = {}

    for file_dir_temp, file_val in library_db.items():
        # get file extension
        # get file extension and add it to stats:
        filename, file_extension = os.path.splitext(file_dir_temp)
        if file_extension in lib_ext_dict.keys():
            lib_ext_dict[file_extension] += 1
        else:
            lib_ext_dict[file_extension] = 1

    return lib_ext_dict


# Print iterations progress
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end=""):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


if __name__ == '__main__':
    # user welcome
    msg = 'this script will read from your original and new library json files that were exported by the ' \
          'read_library.py script, then it will build a new library file in memory and show you information such as ' \
          'mismatched and missing files.'
    print(msg)
    msg = 'once this is done, you will be asked if you want to write the metadata changes over to your new library files, do you understand? (y/n): '
    accepted = input(msg).lower()
    while accepted != 'y':
        if accepted == 'n':
            exit()
        else:
            print('invalid answer, ', end=' ')
            accepted = input(msg).lower()

    # get the path relative to the .py file itself
    source_path = Path(__file__).resolve()
    source_dir = str(source_path.parent).replace(os.sep, '/')

    original_library_dir = input('absolute directory of original-library.json to read from: ')
    new_library_dir = input('absolute directory of new library.json to read from: ')

    folder_name = input('name of folder to save output JSON to?')
    if not os.path.isdir(f'{source_dir}/restorer-outputs'):
        os.mkdir(f'{source_dir}/restorer-outputs')

    while os.path.isdir(f'{source_dir}/restorer-outputs/{folder_name}'):
        folder_name = input("folder already exists, try again: ")

    os.mkdir(f'{source_dir}/restorer-outputs/{folder_name}')

    original_lib = load_json(original_library_dir)
    new_lib = load_json(new_library_dir)

    print('successfully read JSON files into memory, now checking for duplicate hash values in new library...')
    # sort new library by hash
    temp_new_lib = {}
    items_num = len(new_lib)
    list_of_hashes = []
    list_of_duplicates = {}
    for file_dir, file in new_lib.items():
        hashed_val = file['hash']
        list_of_hashes.append(hashed_val)
    for hash_num in list_of_hashes:
        occurrences = list_of_hashes.count(hash_num)
        if occurrences > 1:
            list_of_duplicates[hash_num] = occurrences
    total_dups = 0
    for hash_val in list_of_duplicates:
        total_dups = total_dups + list_of_duplicates[hash_val]

    list_of_duplicate_files = {}
    for file_dir, file in new_lib.items():
        hashed_val = file['hash']
        if hashed_val in list_of_duplicates:
            if hashed_val in list_of_duplicate_files:
                list_of_duplicate_files[hashed_val].append(file_dir)
            else:
                list_of_duplicate_files[hashed_val] = [file_dir]
    export_now = input(f'we found {total_dups} duplicated files in your new library, would you like to export this to JSON file? (y/n): ').lower()

    while export_now != 'y':
        if export_now == 'n':
            break
        else:
            print('invalid answer, ', end=' ')
            export_now = input(f'we found {total_dups} duplicated files in your new library, would you like to export this to JSON file? (y/n): ').lower()
        if export_now == 'y':
            dump_json(f'{source_dir}/restorer-outputs/{folder_name}/newlib-duplicated-files.json',
                      list_of_duplicate_files)

    remove_now = input(
        f'would you like us to delete them from your hard drive and remove them from new library db? THIS CAN NOT BE UNDONE (y/n): ').lower()

    while remove_now != 'y':
        if remove_now == 'n':
            break
        else:
            print('invalid answer, ', end=' ')
            remove_now = input(
                f'would you like us to delete them from your hard drive and remove them from new library db? THIS CAN NOT BE UNDONE (y/n): ').lower()
        if remove_now == 'y':
            break

    if remove_now == 'y':
        prog = 0
        print_progress_bar(prog, len(list_of_duplicate_files), prefix='Progress:', suffix='Complete', length=50)
        error_count = 0
        deleted_files_count = 0
        for file_hash, files in list_of_duplicate_files.items():
            num_of_files = len(files)
            index = 1
            for file_dir_val in files:
                if index == num_of_files:
                    # if we are at last file, leave it as we want to leave at least one of the duplicate files right?
                    break
                index += 1
                # delete file from HDD and remove from new_lib in memory
                new_lib.pop(file_dir_val)
                try:
                    os.remove(file_dir_val)
                    deleted_files_count += 1
                except Exception as e:
                    error_count += 1
            prog += 1
            print_progress_bar(prog, len(list_of_duplicate_files), prefix='Progress:', suffix='Complete', length=50)
        print()
        print(f'deleted {deleted_files_count} files, failed to delete {error_count} files. now checking for duplicates in original library...')
    else:
        print('now checking for duplicates in original library...')

    # put hashes into list
    list_of_hashes = []
    for file_dir, file in original_lib.items():
        hashed_val = file['hash']
        list_of_hashes.append(hashed_val)

    library_statistics = show_file_ext_stats(original_lib)
    print('heres some cool info about file extensions in your original lib')
    for file_ext in library_statistics.keys():
        print(f'{file_ext}: {library_statistics[file_ext]}, ', end=' ')
    print()

    # find duplicate hashes:
    list_of_duplicates = {}
    for hash_num in list_of_hashes:
        occurrences = list_of_hashes.count(hash_num)
        if occurrences > 1:
            list_of_duplicates[hash_num] = occurrences
    total_dups = 0
    for hash_val in list_of_duplicates:
        total_dups = total_dups + list_of_duplicates[hash_val]

    list_of_duplicate_files = {}
    for file_dir, file in original_lib.items():
        hashed_val = file['hash']
        if hashed_val in list_of_duplicates:
            if hashed_val in list_of_duplicate_files:
                list_of_duplicate_files[hashed_val].append(file_dir)
    export_now = input(
        f'we found {total_dups} duplicated files in your original library, would you like to export this to JSON file? (y/n): ').lower()

    while export_now != 'y':
        if export_now == 'n':
            break
        else:
            print('invalid answer, ', end=' ')
            export_now = input(
                f'we found {total_dups} duplicated files in your original library, would you like to export this to JSON file? (y/n): ').lower()
        if export_now == 'y':
            break

    if export_now == 'y':
        dump_json(f'{source_dir}/restorer-outputs/{folder_name}/origlib-duplicated-files.json', list_of_duplicate_files)
        print('finished exporting to json file, now sorting libraries in memory...')
    else:
        print('now sorting original library in memory...')

    # sort original library by hash
    sorted_original_lib = {}
    items_num = len(original_lib)
    prog = 0
    print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
    for file_dir, file in original_lib.items():
        hashed_val = file['hash']
        date_modified = file['m']
        date_created = file['c']
        sorted_original_lib[hashed_val] = {'dir': file_dir, 'm': date_modified, 'c': date_created}
        prog += 1
        print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
    print()

    print('now sorting new library in memory')
    # sort new library by hash
    sorted_new_lib = {}
    items_num = len(new_lib)
    prog = 0
    print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)

    for file_dir, file in new_lib.items():
        hashed_val = file['hash']
        date_modified = file['m']
        date_created = file['c']
        sorted_new_lib[hashed_val] = {'dir': file_dir, 'm': date_modified, 'c': date_created}
        prog += 1
        print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)

    library_statistics = show_file_ext_stats(new_lib)
    print('heres some cool info about file extensions in your new lib')
    for file_ext in library_statistics.keys():
        print(f'{file_ext}: {library_statistics[file_ext]}, ', end=' ')
    print()

    missing_from_new_lib = {}
    check_for_missing = input(
        'finished sorting new lib, would you like us to scan and see if there are any files in the original lib that are missing from the new lib? (y/n): ').lower()

    while check_for_missing != 'y':
        if check_for_missing == 'n':
            break
        else:
            print('invalid answer, ', end=' ')
            check_for_missing = input(
                'finished sorting new lib, would you like us to scan and see if there are any files in the original lib that are missing from the new lib? (y/n): ').lower()
        if check_for_missing == 'y':
            break

    if check_for_missing == 'y':
        prog = 0
        missing_from_new_lib_count = 0
        items_num = len(sorted_original_lib)
        for orig_file_hash, orig_file in sorted_original_lib.items():
            prog += 1
            print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
            if orig_file_hash not in sorted_new_lib.keys():
                missing_from_new_lib[orig_file['dir']] = orig_file_hash
                missing_from_new_lib_count += 1
        print()
        save = input(f'found {missing_from_new_lib_count} missing files from new library, would you like to save these to a JSON file? (y/n): ').lower()

        while save != 'y':
            if save == 'n':
                break
            else:
                print('invalid answer, ', end=' ')
                save = input(
                    f'found {missing_from_new_lib_count} missing files from new library, would you like to save these to a JSON file? (y/n): ').lower()
            if save == 'y':
                break

        if save == 'y':
            dump_json(f'{source_dir}/restorer-outputs/{folder_name}/files-missing-from-new-lib.json', missing_from_new_lib)
            print('saved')

    ready = input('are you ready to process the new library database? Nothing will be written to disk (y/n): ').lower()

    while ready != 'y':
        if ready == 'n':
            break
        else:
            print('invalid answer, ', end=' ')
            ready = input(
                'are you ready to process the new library database? Nothing will be written to disk (y/n): ').lower()
        if ready == 'y':
            break

    if ready.lower() == 'y':
        # create new merged lib
        merged_library = {}
        stats = {'errors': [], 'duplicates': [], 'singles': [], 'pairs': 0}

        amount_of_modifications_made = 0
        items_num = len(sorted_new_lib)
        prog = 0
        print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
        for file_hash, new_file in sorted_new_lib.items():
            date_modified = new_file['m']
            date_created = new_file['c']
            if file_hash in sorted_original_lib.keys():
                stats['pairs'] += 1
                orig = sorted_original_lib[file_hash]
                # check if there was an actual difference:
                if not orig['m'] == date_modified:
                    amount_of_modifications_made += 1
                    merged_library[new_file['dir']] = {'m': orig['m'], 'c': orig['c'], 'hash': file_hash}
            else:
                stats['singles'].append(new_file['dir'])
            prog += 1
            print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
        print()

        print(f'{amount_of_modifications_made} file differences were found')
        print(f'total number of missing files from new library is {len(sorted_original_lib) - (len(sorted_new_lib) - len(stats["singles"]))}')
        print(f'here are stats for new library: {stats}')

        dump_json(f'{source_dir}/restorer-outputs/{folder_name}/merged-lib.json', merged_library)

        # now ask user if they want to continue modifying all files in new library to fix metadata:
        fix_now = input(f'do you now want to fix the {amount_of_modifications_made} files from new library? (y/n): ').lower()

        while fix_now != 'y':
            if fix_now == 'n':
                break
            else:
                print('invalid answer, ', end=' ')
                fix_now = input(
                    f'do you now want to fix the {amount_of_modifications_made} files from new library? (y/n): ').lower()
            if fix_now == 'y':
                break

        if fix_now:
            if int(amount_of_modifications_made) == 0:
                print('0 changes to be made, exiting...')
                exit()
            errors = {}
            starting_time = time.time()
            amount_of_modifications_actually_written = 0
            prog = 0
            print_progress_bar(prog, amount_of_modifications_made, prefix='Progress:', suffix='Complete', length=50)
            for file_hash, new_file in sorted_new_lib.items():
                date_modified = new_file['m']
                date_created = new_file['c']
                if file_hash in sorted_original_lib.keys():
                    orig = sorted_original_lib[file_hash]
                    # check if there was an actual difference:
                    if not orig['m'] == date_modified:
                        amount_of_modifications_actually_written += 1
                        # make changes to HDD
                        try:
                            os.utime(new_file['dir'], (orig['m'], orig['m']))  # set time modified
                        except Exception as error:
                            errors[new_file['dir']] = str(error)
                        prog += 1
                        print_progress_bar(prog, amount_of_modifications_made, prefix='Progress:', suffix='Complete', length=50)
                        # make changes to HDD
                else:
                    stats['singles'].append(new_file['dir'])
            print()

            time_elapsed = int(time.time() - starting_time)

            print(f"finished making {amount_of_modifications_actually_written} exif modifications after {time_elapsed} seconds, {len(errors)} errors encountered")
            if len(errors) > 0:
                save_or_not = input('would you like to export writing_errors to a json file? this will show you what went wrong when writing exif data. (y/n): ')
                if save_or_not.lower() == 'y':
                    dump_json(f'{source_dir}/restorer-outputs/{folder_name}/writing_errors.json', errors)
    print("script finished, if you have any trouble create a new issue @ https://github.com/LeehamElectronics/exif-library-restorer")
