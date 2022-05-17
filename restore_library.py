import os
import json
import time
from pathlib import Path
from win32_setctime import setctime


def load_json(dir_val):
    with open(dir_val) as f:
        return json.load(f)


def dump_json(location, db):
    with open(location, "w") as f:
        json.dump(db, f, indent=4)


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
    accepted = input(msg)
    if accepted.lower() == 'y':
        pass
    else:
        exit()

    # get the path relative to the .py file itself
    source_path = Path(__file__).resolve()
    source_dir = str(source_path.parent).replace(os.sep, '/')

    original_library_dir = input('absolute directory of original-library.json to read from: ')
    new_library_dir = input('absolute directory of new library.json to read from: ')

    folder_name = input('name of folder to save output JSON to?')
    if not os.path.isdir(f'{source_dir}/merger-outputs'):
        os.mkdir(f'{source_dir}/merger-outputs')

    while os.path.isdir(f'{source_dir}/merger-outputs/{folder_name}'):
        folder_name = input("folder already exists, try again: ")

    os.mkdir(f'{source_dir}/merger-outputs/{folder_name}')

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
            print('found duplicate')
            list_of_duplicates[hash_num] = occurrences
    total_dups = 0
    for hash_val in list_of_duplicates:
        total_dups = total_dups + list_of_duplicates[hash_val]
    print(f'total duplicate files found: {total_dups}')

    list_of_duplicate_files = {}
    for file_dir, file in new_lib.items():
        hashed_val = file['hash']
        if hashed_val in list_of_duplicates:
            if hashed_val in list_of_duplicate_files:
                list_of_duplicate_files[hashed_val].append(file_dir)
            else:
                list_of_duplicate_files[hashed_val] = [file_dir]
    export_now = input(f'we found {total_dups} duplicated files in your new library, would you like to export this to JSON file? (y/n): ')
    if export_now.lower() == 'y':
        dump_json(f'{source_dir}/merger-outputs/{folder_name}/newlib-duplicated-files.json', list_of_duplicate_files)
    remove_now = input(
        f'would you like us to delete them from your hard drive and remove them from new library db? THIS CAN NOT BE UNDONE (y/n): ')
    if remove_now.lower() == 'y':
        prog = 0
        print_progress_bar(prog, len(list_of_duplicate_files), prefix='Progress:', suffix='Complete', length=50)
        error_count = 0
        for file_hash, files in list_of_duplicate_files:
            num_of_files = len(files)
            current_index = 1
            for file_dir_val in files:
                if current_index == num_of_files:
                    # if we are at last file, leave it as we want to leave at least one of the duplicate files right?
                    break
                current_index += 1
                # delete file from HDD and remove from new_lib in memory
                new_lib.pop(file_dir_val)
                try:
                    os.remove(file_dir_val)
                except Exception as e:
                    print(f'failed to delete file {file_dir_val} due to {e}')
                    error_count += 1
            prog += 1
            print_progress_bar(prog, len(list_of_duplicate_files), prefix='Progress:', suffix='Complete', length=50)
        print()
        print(f'deleted {total_dups - error_count} files, now checking for duplicates in original library...')
    print('now checking for duplicates in original library...')

    temp_new_lib = {}
    items_num = len(new_lib)
    prog = 0
    print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
    list_of_hashes = []
    list_of_duplicates = {}
    for file_dir, file in new_lib.items():
        hashed_val = file['hash']
        list_of_hashes.append(hashed_val)
    for hash_num in list_of_hashes:
        occurrences = list_of_hashes.count(hash_num)
        if occurrences > 1:
            print('found duplicate')
            list_of_duplicates[hash_num] = occurrences
    total_dups = 0
    for hash_val in list_of_duplicates:
        total_dups = total_dups + list_of_duplicates[hash_val]
    print(f'total duplicate files found: {total_dups}')

    list_of_duplicate_files = {}
    for file_dir, file in new_lib.items():
        hashed_val = file['hash']
        if hashed_val in list_of_duplicates:
            if hashed_val in list_of_duplicate_files:
                list_of_duplicate_files[hashed_val].append(file_dir)
    export_now = input(
        f'we found {total_dups} duplicated files in your original library, would you like to export this to JSON file?')
    if export_now.lower() == 'y':
        dump_json(f'{source_dir}/merger-outputs/{folder_name}/origlib-duplicated-files.json', list_of_duplicate_files)
        print('finished exporting to json file, now sorting libraries in memory...')
    print('now sorting libraries in memory...')

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
    print('finished sorting original library, now sorting new library')

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

    missing_from_new_lib = {}
    check_for_missing = input(
        'finished sorting new lib, would you like us to scan and see if there are any files in the original lib that are missing from the new lib?')
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
        save = input(f'found {missing_from_new_lib_count} missing files from new library, would you like to save these to a JSON file? (y/n): ')
        if save.lower() == 'y':
            dump_json(f'{source_dir}/merger-outputs/{folder_name}/files-missing-from-new-lib.json', missing_from_new_lib)
            print('saved')

    ready = input('are you ready to process the new library database? Nothing will be written to disk (y/n): ')
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
                print(f'{new_file["dir"]}:  {orig["m"]} / {date_modified}')
                if not orig['m'] == date_modified:
                    amount_of_modifications_made += 1
                    merged_library[new_file['dir']] = {'m': orig['m'], 'c': orig['c'], 'hash': file_hash}
            else:
                stats['singles'].append(new_file['dir'])
                print("POOP")
            prog += 1
            print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
        print()

        print(f'{amount_of_modifications_made} file differences were found')
        print(f'total number of missing files from new library is {len(sorted_original_lib) - len(sorted_new_lib)}')
        print(f'here are stats for new library: {stats}')

        dump_json(f'{source_dir}/merger-outputs/{folder_name}/merged-lib.json', merged_library)

        # now ask user if they want to continue modifying all files in new library to fix metadata:
        fix_now = input(f'do you now want to fix the {amount_of_modifications_made} files from new library?')
        if int(amount_of_modifications_made) == 0:
            print('0 changes to be made, exiting...')
            exit()
        if fix_now:
            errors = []
            starting_time = time.time()
            items_num = len(merged_library)
            prog = 0
            print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
            for file_dir, file in merged_library.items():
                try:
                    setctime(file_dir, file['m'])  # set time modified
                except Exception as error:
                    errors.append({'dir': file_dir, 'error': error})
                prog += 1
                print_progress_bar(prog, items_num, prefix='Progress:', suffix='Complete', length=50)
            print()
            time_elapsed = int(time.time() - starting_time)
            print(f"finished modifying all files after {time_elapsed} seconds, {len(errors)} errors encountered")
            if len(errors) > 0:
                save_or_not = input('would you like to export writing_errors to a json file? this will show you what went wrong when writing exif data. (y/n): ')
                if save_or_not.lower() == 'y':
                    dump_json(f'{source_dir}/merger-outputs/{folder_name}/writing_errors.json', errors)
