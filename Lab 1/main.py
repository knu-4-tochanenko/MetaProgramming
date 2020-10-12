from file_finder import find_kt_files

if __name__ == '__main__':
    directory = input("Enter project directory: ")
    kt_files = find_kt_files(directory)
    print(kt_files)
