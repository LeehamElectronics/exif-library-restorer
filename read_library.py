#!/usr/bin/python3
# exif-library-restorer
# built by leeham 2022 https://github.com/LeehamElectronics

########################################################################################################################
#                                                 What it does                                                         #
########################################################################################################################
# this script simply walks through a given directory finding all the files in them. It then generates a json file
# containing hashed values of the file, the date modified, and the date of creation of each file. It also generates
# a second json file containing any errors and duplicate files it encountered. Whe the script is finished running it
# also prints some statistics into the console such as file extension types.

########################################################################################################################
#                                                                                                                      #
#                                                   note to user                                                       #
#                                                                                                                      #
########################################################################################################################
# DO NOT RUN this script on a library that is not local to your machine. For example, do not run this script on your
# remote windows share library because it will try to download the entire library to your computer.

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


def process_file_worker(file_info_dict, return_dict_val):
    md5 = hashlib.md5()
    buffer_size = 65536  # size to read files in, recommended size is 64kb chunks
    file_absolute_directory = file_info_dict['dir']

    # try to open the file, generate hash, and read metadata
    try:
        with open(file_absolute_directory, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                md5.update(data)

        print(f'{str(md5.hexdigest())}: {file_absolute_directory}')
        date_created = os.path.getctime(file_absolute_directory)
        date_modified = os.path.getmtime(file_absolute_directory)
        return_dict_val[file_absolute_directory] = {'hash': str(md5.hexdigest()), 'c': date_created, 'm': date_modified}

    except Exception as error:
        return_dict_val[file_absolute_directory] = ({'error': error})
        print(error)


def create_dictionary_db(number_of_files):
    library_statistics = {}  # contains general stats about your library
    amount_of_folders = 0
    progress = 0
    starting_time = time.time()

    if core_count > 1:
        # Start a Pool with 4 processes
        pool = Pool(processes=files_open_limit)
        pool_jobs = []

    md5 = hashlib.md5()
    buffer_size = 65536  # size to read files in, recommended size is 64kb chunks

    print("reading...")
    for file_path, sub_directories, file_vals in os.walk(path_to_library):
        amount_of_folders += 1
        for short_name in file_vals:
            if short_name.lower() == 'thumbs.db':
                if 'thumbs.db' in library_statistics.keys():
                    library_statistics['thumbs.db'] += 1
                else:
                    library_statistics['thumbs.db'] = 1
                progress += 1
                continue

            file_info_dict = {}

            file_absolute_directory = os.path.join(file_path, short_name)
            file_absolute_directory = os.path.normpath(file_absolute_directory)

            file_info_dict['dir'] = file_absolute_directory

            # get file extension and add it to stats:
            filename, file_extension = os.path.splitext(file_absolute_directory)
            if file_extension in library_statistics.keys():
                library_statistics[file_extension] += 1
            else:
                library_statistics[file_extension] = 1

            ###########################################################################
            #                                                                         #
            #                           multicore processing                          #
            #                                                                         #
            ###########################################################################
            if core_count > 1:
                proc = pool.apply_async(func=process_file_worker, args=(file_info_dict, return_dict))
                pool_jobs.append(proc)

                progress += 1
                print_progress_bar(progress, number_of_files, prefix='Progress:', suffix='Complete', length=50)
            else:   # single core implementation
                # try to open the file, generate hash, and read metadata
                md5 = hashlib.md5()
                try:
                    with open(file_absolute_directory, 'rb') as f:
                        while True:
                            data = f.read(buffer_size)
                            if not data:
                                break
                            md5.update(data)

                    date_created = os.path.getctime(file_absolute_directory)
                    date_modified = os.path.getmtime(file_absolute_directory)

                    return_dict[file_absolute_directory] = {'hash': str(md5.hexdigest()), 'c': date_created,
                                                            'm': date_modified}
                except Exception as error:
                    return_dict[file_absolute_directory] = ({'error': error})

                progress += 1
                print_progress_bar(progress, number_of_files, prefix='Progress:', suffix='Complete', length=50)

    if core_count > 1:
        print()
        print("finished spawning processes, now closing pools...")
        number_of_procs = len(pool_jobs)
        # Wait for jobs to complete before exiting
        while not all([p.ready() for p in pool_jobs]):
            finished_jobs = 0
            for process in pool_jobs:
                if process.ready():
                    finished_jobs += 1
            print_progress_bar(finished_jobs, number_of_procs, prefix='Progress:', suffix='Complete', length=50)
            time.sleep(1)
        # Safely terminate the pool
        pool.close()
        pool.join()
        print()

    errors_db = {}
    number_of_files_proc = 0
    error_count = 0
    for file_dir, file in return_dict.items():
        number_of_files_proc += 1
        if 'error' in file.keys():
            errors_db[file_dir] = file
            error_count += 1

    # save data to disk
    print(f"Finished processing {number_of_files_proc} files, {number_of_files - number_of_files_proc} were skipped, now saving to disk... ", end=' ')
    dump_json(data_output_save_location, return_dict.copy())
    dump_json(error_output_save_location, errors_db)
    print("saved!")

    print('here are statistics about the types of files in your library:')
    for file_ext in library_statistics.keys():
        print(f'{file_ext}: {library_statistics[file_ext]}, ', end=' ')
    print(f'{error_count} errors found')
    print(f'{amount_of_folders - 1} folders found')

    print(f'time elapsed was {int(time.time() - starting_time)} seconds')

    size_of_output = int(sys.getsizeof(return_dict) + sys.getsizeof(errors_db) / 1000000)
    file_size_measurement = 'bytes'
    if size_of_output > 999999999:
        # measured in gb
        file_size_measurement = 'gb'
    elif size_of_output > 999999:
        # measure in mb
        file_size_measurement = 'mb'
    elif size_of_output > 999:
        # measure in kb
        file_size_measurement = 'kb'

    print(
        f"finished processing files from {path_to_library}. The output is saved in folder: {data_output_folder_name} (size:{size_of_output} {file_size_measurement})")


if __name__ == '__main__':
    # get the path relative to the .py file itself
    source_path = Path(__file__).resolve()
    source_dir = str(source_path.parent).replace(os.sep, '/')

    if not os.path.isdir(f'{source_dir}/output'):
        os.mkdir(f'{source_dir}/output')

    ##################################
    #          input data:           #
    ##################################
    start = input(
        'This script simply collates data from your library by hashing each file, do not run this script on a remote NAS or share folder, understand? (y/n): ')
    if not start.lower() == 'y':
        print('wrong answer')
        exit()
    path_to_library = input("absolute path to library for reading: ")
    data_output_folder_name = input("name of the folder you would like to save json data too: ")

    while os.path.isdir(f'{source_dir}/output/{data_output_folder_name}'):
        data_output_folder_name = input("folder already exists, try again: ")

    os.mkdir(f'{source_dir}/output/{data_output_folder_name}')

    if input("would you like to use multi-core processing? (y/n): ") == 'y':
        core_count = multiprocessing.cpu_count()
        cpus_syntax = "CPU's"

        default_os_limit = 50
        os_type = platform.system()
        if os_type == 'Linux':
            default_os_limit = 700

        files_open_limit = input(f'we recommend limiting the amount of files open at a time, we will use your operating systems default value, otherwise specify how many you would like. (default={default_os_limit}):')
        if files_open_limit == '':
            files_open_limit = default_os_limit
        else:
            files_open_limit = int(files_open_limit)
    else:
        files_open_limit = 1
        core_count = 1
        cpus_syntax = "CPU"
    print(
        f"reading from {path_to_library}, saving into output/{data_output_folder_name}, using {core_count} {cpus_syntax} and a limit of {files_open_limit} files open at a time")

    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")

    # global variables:
    data_output_save_location = f'{source_dir}/output/{data_output_folder_name}/{current_time}_json_data.json'
    error_output_save_location = f'{source_dir}/output/{data_output_folder_name}/{current_time}_error_data.json'

    number_of_files_found = 0
    print("finding total number of items to be processed... ", end=' ')
    for file_paths, sub_dirs, files in os.walk(path_to_library):
        for i in files:
            number_of_files_found += 1
    print(f"{number_of_files_found} files found")

    # multiprocessing
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    json.dumps(dict(return_dict.copy()))
    jobs = []
    begin = input('would you like to start processing your library now? (y/n):')
    if begin.lower() == 'y':
        create_dictionary_db(number_of_files_found)