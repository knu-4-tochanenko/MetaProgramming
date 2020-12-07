from lexer import parse
from token import TokenType


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
                i = self.__fix_package(i)
            elif token in ('class', 'interface'):
                pass
            i += 1

    def __fix_package(self, pos):
        pos = self.__skip_ws_tokens(pos)
        while self.__tokens[pos] != ';':
            if self.__tokens[pos].get_type() == TokenType.IDENTIFIER and not Formatter.is_lower_case(
                    self.__tokens[pos].get_value()):
                self.__to_fix[self.__tokens[pos]] = Formatter.to_lower_case((self.__tokens[pos]))
            pos += 1

        return pos

    def __fix_class_name(self):
        pass

    def __fix_class_body(self):
        pass

    def __fix(self):
        pass

    def __fix_comments(self):
        pass

    def __skip_ws_tokens(self, pos):
        while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
            pos += 1
        return pos

    @staticmethod
    def is_lower_case(naming):
        if naming.find('_') != -1 or not naming.islower():
            return False

    @staticmethod
    def to_lower_case(naming):
        return ''.join([component.lower() for component in naming.split('_')])

    @staticmethod
    def is_camel_lower_case(naming):
        pass

    @staticmethod
    def is_camel_upper_case(naming):
        pass

    @staticmethod
    def is_snake_lower_case(naming):
        pass

    @staticmethod
    def is_snake_upper_case(naming):
        pass
