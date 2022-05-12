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

##################################
#          input data:           #
##################################
start = input('This script simply collates data from your library by hashing each file, do not run this script on a remote NAS or share folder, understand? (y/n): ')
if not start.lower() == 'y':
    print('wrong answer')
    exit()
path_to_library = input("absolute path to library for reading: ")
data_output_folder_name = input("name of the folder you would like to save json data too: ")
print(f"reading files from {path_to_library} and saving extrapolated data into local folder: {data_output_folder_name}")

##################################
#        global variables:       #
##################################
now = datetime.now()
current_time = now.strftime("%H-%M-%S")

# get the path relative to the .py file itself
source_path = Path(__file__).resolve()
source_dir = str(source_path.parent).replace(os.sep, '/')

os.mkdir(f'{source_dir}/{data_output_folder_name}')
data_output_save_location = f'{source_dir}/{data_output_folder_name}/{current_time}_json_data.json'
error_output_save_location = f'{source_dir}/{data_output_folder_name}/{current_time}_error_data.json'
buffer_size = 65536  # size to read files in, recommended size is 64kb chunks

md5 = hashlib.md5()


def dump_json(location, db):
    with open(location, "w") as f:
        json.dump(db, f, indent=4)


# step one is to go through every single file in library A (organised lib) and save its complete path and hash value

number_of_files_found = 0
print("now finding total number of items to be processed...")
for file_paths, sub_dirs, files in os.walk(path_to_library):
    for i in files:
        number_of_files_found += 1
print(f"found {number_of_files_found} files")


def create_dictionary_db():
    library_db = []  # a list that contains a separate dictionary for each file found
    errors_db = []  # a list that contains a separate dictionary for each file that errors
    library_statistics = {}  # contains general stats about your library
    amount_of_folders = 0
    progress = 0
    # record time:
    starting_time = time.time()

    for file_path, sub_directories, files in os.walk(path_to_library):
        for short_name in files:
            if short_name.lower() == 'thumbs.db':
                if 'thumbs.db' in library_statistics.keys():
                    library_statistics['thumbs.db'] += 1
                else:
                    library_statistics['thumbs.db'] = 1
                progress += 1
                continue

            file_absolute_directory = os.path.join(file_path, short_name)
            file_absolute_directory = os.path.normpath(file_absolute_directory)

            # try to open the file, generate hash, and read metadata
            try:
                with open(file_absolute_directory, 'rb') as f:
                    while True:
                        data = f.read(buffer_size)
                        if not data:
                            break
                        md5.update(data)

                date_created = os.path.getctime(file_absolute_directory)
                date_modified = os.path.getmtime(file_absolute_directory)

                # get file extension and add it to stats:
                filename, file_extension = os.path.splitext(file_absolute_directory)
                if file_extension in library_statistics.keys():
                    library_statistics[file_extension] += 1
                else:
                    library_statistics[file_extension] = 1

                library_db.append(
                    {'dir': file_absolute_directory, 'hash': str(md5.hexdigest()), 'c': date_created, 'm': date_modified})
            except Exception as error:
                errors_db.append({'error': error, 'dir': file_absolute_directory})

            progress += 1
        # send progress bar everytime we finish a folder
        print(f'progress: {progress}/{number_of_files_found}')
        amount_of_folders += 1

    # save data to disk
    print("Finished processing data, now saving to disk... ", end=' ')
    dump_json(data_output_save_location, library_db)
    dump_json(error_output_save_location, errors_db)
    print("done")

    print('here are statistics about the types of files in your library:')
    for file_ext in library_statistics.keys():
        print(f'{file_ext}: {library_statistics[file_ext]}')
    print(f'number of folders within your library: {amount_of_folders - 1}')

    print(f'time elapsed was {int(time.time() - starting_time)} seconds')

    size_of_output = int(sys.getsizeof(library_db) + sys.getsizeof(errors_db) / 1000000)
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
        f"Finished processing files from {path_to_library}. The output is saved in folder: {data_output_folder_name} (size:{size_of_output} {file_size_measurement})")


create_dictionary_db()