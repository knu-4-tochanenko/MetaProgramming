from file_finder import find_kt_files
from settings import load_settings

from new_lexer import Lexer

if __name__ == '__main__':
    # directory = input("Enter project directory: ")
    # kt_files = find_kt_files(directory)
    # print(kt_files)

    # print("Settings:")
    # settings = load_settings("config/config.json")
    # print(settings)
    #
    # print(settings['spaces']['before_parentheses']['for'])
    #
    #

    lexer = Lexer()
    lexer.tokenize_file('kotlin/file.kt', )