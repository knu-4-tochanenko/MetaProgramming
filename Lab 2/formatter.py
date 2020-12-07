import logging
from lexer import parse


class Formatter:
    def __init__(self, files):
        self.__files = files
        self.__tokens = []
        self.__to_fix = dict()

    def process(self):
        tokens = []
        for file in self.__files:
            tokens.append(parse(open(file, 'r').read()))
        i = 0
        while i < len(tokens):
            self.__tokens = tokens[i]
            self.__find_to_fix()
            tokens[i] = self.__tokens
        while i < len(tokens):
            self.__tokens = tokens[i]
            self.__fix()
            self.__fix_comments()
            tokens[i] = self.__tokens

    def __find_to_fix(self):
        i = 0
        while i < len(self.__tokens):
            token = self.__tokens[i]
            if token == 'package':
                pass
            elif token in ('class', 'interface'):
                pass

    def __fix_package(self):
        pass

    def __fix_class_name(self):
        pass

    def __fix_class_body(self):
        pass

    def __fix(self):
        pass

    def __fix_comments(self):
        pass
