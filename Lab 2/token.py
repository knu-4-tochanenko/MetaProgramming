from enum import Enum
import logging


class TokenType(Enum):
    WHITESPACE = 1
    COMMENT = 2
    KEYWORD = 3
    IDENTIFIER = 4
    SEPARATOR = 5
    OPERATOR = 6
    LITERAL = 7
    ANNOTATION = 8


class Token:
    def __init__(self, value, _type):
        self.__value = value
        self.__type = _type

    def get_value(self):
        return self.__value

    def set_value(self, value):
        self.__value = value

    def get_type(self):
        return self.__type


def update_token_value(file, token, value):
    if token.get_value() != value:
        logging.warning(
            f'{file}: Incorrect code style for token value: Expected {value}, but found {token.get_value()}')
        token.set_value(value)
