import logging
import argparse
import os
from file_finder import find_java_files
from formatter import Formatter


def add_argparse():
    ap = argparse.ArgumentParser(description="JavaCCF is utility to fix style in Java files.")
    ap = argparse.ArgumentParser(
        description="ScalaCCF - utility to fix style and documentation comments in Scala files")
    ap.add_argument('-p', type=str, default=None, help="Path to Java project directory to verify or correct mistakes.")
    ap.add_argument('-d', type=str, default=None,
                    help="Path to directory with Java files to verify or correct mistakes.")
    ap.add_argument('-f', type=str, default=None, help="Path to Java file to verify or correct mistakes.")
    ap.add_argument('-v', '--verify', action='store_true', help='Verify code style and documentation comments')
    ap.add_argument('-c', '--correct', action='store_true',
                    help='Correct styling mistakes in code and documentation comments')

    path_arguments = ['p', 'd', 'f']
    mode_arguments = ['verify', 'correct']

    args = ap.parse_args()

    path_results = [arg for arg in path_arguments if getattr(args, arg) is not None]
    mode_results = [arg for arg in mode_arguments if getattr(args, arg) not in (None, False)]

    if len(path_results) != 1:
        raise ValueError('You should specify exactly one path parameter.')

    if len(mode_results) != 1:
        raise ValueError('You should specify exactly one mode parameter.')

    path = path_results[0]
    mode = mode_results[0]

    files = get_files(path, args)

    if mode == 'verify':
        verify(files)
    elif mode == 'correct':
        correct(files)

    if path == 'p':
        rename_dirs(args.p, mode)


def get_files(path_arg, args):
    if path_arg == 'p':
        return find_java_files(args.p)
    if path_arg == 'd':
        return [os.path.join(args.d, f)
                for f in os.listdir(args.d)
                if f.endswith('.java')]
    if path_arg == 'f':
        return [args.f]


def verify(files):
    if not os.path.exists('verification'):
        os.mkdir('verification')
    logging.basicConfig(filename=os.path.join('verification', 'verification.log'),
                        level=logging.WARN)
    formatter = Formatter(files)
    tokens = formatter.process()
    i = 0
    while i < len(files):
        rewrite_file(files[i], tokens[i])
        i += 1


def correct(files):
    if not os.path.exists('fixing'):
        os.mkdir('fixing')
    logging.basicConfig(filename=os.path.join('fixing', 'fixing.log'),
                        level=logging.WARN)
    formatter = Formatter(files)
    tokens = formatter.process()
    i = 0
    while i < len(files):
        rewrite_file(files[i], tokens[i])
        i += 1


def rewrite_file(filename, tokens):
    file = open(filename, mode='w+')
    for token in tokens:
        file.write(token.get_value())
    file.close()


def rename_dirs(path, mode):
    for file in os.listdir(path):
        d = os.path.join(path, file)
        if os.path.isdir(d):
            rename_dirs(d, mode)
            expected = Formatter.to_lower_case(file)
            if expected != file:
                logging.warning(f'{file}: Wrong naming for directory in package path. Expected {expected}, but found {file}')
                if mode == 'correct':
                    os.rename(d, os.path.join(path, expected))
