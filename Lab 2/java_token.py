from enum import Enum
import logging


class TokenType(Enum):
    WHITESPACE = 1
    ANNOTATION = 2
    COMMENT = 3
    KEYWORD = 4
    IDENTIFIER = 5
    SEPARATOR = 6
    OPERATOR = 7
    STRING_LITERAL = 8
    NUMBER_LITERAL = 9


class Token:
    def __init__(self, value, _type):
        self.__value = value
        self.__type = _type
        self.__is_fixed = False

    def get_value(self):
        return self.__value

    def set_value(self, value):
        self.__value = value

    def get_type(self):
        return self.__type

    def is_fixed(self):
        return self.__is_fixed

    def set_fixed(self, fixed):
        self.__is_fixed = fixed


def update_token_value(file, token, value):
    if token.get_value() != value:
        logging.warning(
            f'{file}: Incorrect code style for token value: Expected {value}, but found {token.get_value()}')
        token.set_value(value)
        token.set_fixed(True)
