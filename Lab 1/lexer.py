from enum import Enum


class Token(Enum):
    TAB = 0,
    SPACE = 1,
    KEYWORD = 2,
    COMMENT = 3,
    IDENTIFIER = 4,
    OPERATOR = 5,
    SEPARATOR = 6,
    LITERAL_NUMBER = 7,
    STRING_LITERAL = 8,
    NEWLINE = 9,
    ANNOTATION = 10


special_symbols = ['(', ')', '{', '}', '!', '@', '#', '$', '%', '^', '&', '*', '-', '_', '=', '+', '\'', '"', '[', ']',
                   '\\', '|', '`', '~', ';', ':', '<', '>', ',', '.', '/', '?']
keywords = ['as', 'break', 'class', 'continue', 'do', 'else', 'false', 'for', 'fun', 'if', 'in', 'interface', 'is',
            'null', 'object', 'package', 'return', 'super', 'this', 'throw', 'true', 'try', 'typealias', 'typeof',
            'val', 'var', 'when', 'while', 'by', 'catch', 'constructor', 'delegate', 'dynamic', 'field', 'file',
            'finally', 'get', 'import', 'init', 'param', 'property', 'receiver', 'set', 'setparam', 'where', 'actual',
            'abstract', 'annotation', 'companion', 'const', 'crossinline', 'data', 'enum', 'expect', 'external',
            'final', 'infix', 'inline', 'inner', 'internal', 'lateinit', 'noinline', 'open', 'operator', 'out',
            'override', 'private', 'protected', 'public', 'reified', 'sealed', 'suspend', 'tailrec', 'vararg', 'field',
            'it']


class Lexer:
    def __init__(self, path):
        self.__path = path
        self.__res = []

    def run(self):
        file = open(self.__path, 'r')
        lines = file.readlines()

        for line in lines:
            pass
            # parse_line(line)

    def add_token(self, token_type, token_string):
        self.__res.append((token_type, token_string))

    def parse_token(self, token):
        if token in keywords:
            self.add_token(Token.KEYWORD, token)


    def parse_line(self, line):
        cur_string = ''
        for i in range(0, len(line)):
            if line[i] in special_symbols or line[i] == ' ' or line[i] == '\n':
                self.parse_token(cur_string)
                cur_string = line[i]
            else:
                cur_string += line[i]
        if len(cur_string) > 0:
            self.parse_token(cur_string)

