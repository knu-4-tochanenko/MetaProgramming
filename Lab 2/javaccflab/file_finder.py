from os import listdir
from os.path import isfile, join


def find_java_files(directory):
    directory_entries = listdir(directory)
    kt_files = []

    for element in directory_entries:
        current_path = join(directory, element)
        if isfile(current_path) and element.endswith('.java'):
            kt_files.append(current_path)
        elif not isfile(current_path) and not element.startswith('.'):
            kt_files_in_subdir = find_java_files(current_path)
            if len(kt_files_in_subdir) > 0:
                kt_files += find_java_files(current_path)

    return kt_files
