from enum import Enum
import re


class TokenType(Enum):
    WHITESPACE = 1
    COMMENT = 2
    KEYWORD = 3
    IDENTIFIER = 4
    SEPARATOR = 5
    OPERATOR = 6
    NUMBER_LITERAL = 7
    STRING_LITERAL = 8
    ANNOTATION = 9


class Token:
    def __init__(self, value, token_type, position=None):
        self.__value = value
        self.__token_type = token_type
        self.__position = position

    def __repr__(self):
        if self.__position is None:
            return f'Token: [Value: {ord(self.__value) if self.__token_type == TokenType.WHITESPACE else self.__value}], Type: [{self.__token_type}]'
        return f'Token: [Value: {ord(self.__value) if self.__token_type == TokenType.WHITESPACE else self.__value}], Type: [{self.__token_type}], Position: [{self.__position[0]}:{self.__position[1]}]]'

    def get_value(self):
        return self.__value

    def set_value(self, value):
        self.__value = value

    def get_token_type(self):
        return self.__token_type

    def get_position(self):
        return self.__position
    

class Lexer:
    __keywords = (
        'as', 'break', 'class', 'continue', 'do', 'else', 'false', 'for', 'fun', 'if', 'in', 'interface', 'is',
        'null', 'object', 'package', 'return', 'super', 'this', 'throw', 'true', 'try', 'typealias', 'typeof',
        'val', 'var', 'when', 'while', 'by', 'catch', 'constructor', 'delegate', 'dynamic', 'field', 'file',
        'finally', 'get', 'import', 'init', 'param', 'property', 'receiver', 'set', 'setparam', 'where', 'actual',
        'abstract', 'annotation', 'companion', 'const', 'crossinline', 'data', 'enum', 'expect', 'external',
        'final', 'infix', 'inline', 'inner', 'internal', 'lateinit', 'noinline', 'open', 'operator', 'out',
        'override', 'private', 'protected', 'public', 'reified', 'sealed', 'suspend', 'tailrec', 'vararg', 'field',
        'it')

    __operators = (
        '+', '-', '*', '/', '%', '=', '+=', '-=', '*=', '/=', '%=', '++', '--', '&&', '--', '!', '==', '!=', '===',
        '!==',
        '<', '>', '<=', '>=', '[', ']', '!!', '?.', '?:', '::', '..', ':', '?', '->', '@', ';', '$')

    __separators = (';', ',', '.', '(', ')', '{', '}', '[', ']')

    def __init__(self, file_path, config):
        self.__file_path = file_path
        self.__config = config

        self.__tokens = []
        self.__position = 0
        # Position of token on line
        self.__row = 0
        self.__column = 0

    def get_tokens(self):
        if len(self.__tokens) == 0:
            self.tokenize_file()
        return self.__tokens

    def tokenize_file(self):
        code = open(self.__file_path, 'r').read()
        self.__tokenize(code)

    def __tokenize(self, code):
        while self.__position < len(code):
            character = code[self.__position]
            # Whitespace
            if character.isspace():
                self.__parse_whitespace(character)
            # Comments
            elif character == '/':
                self.__parse_comment(code)
            # Keyword or identifier
            elif character.isalpha() or character == '_':
                self.__parse_keyword_or_id(code)
            # Number literal
            elif character.isdigit():
                self.__parse_number_literal(code)
            # String literal
            elif character == '"' or character == "'":
                self.__parse_string_literal(character, code)
            # Annotation
            elif character == '@':
                self.__parse_annotation(code)
            # Separator
            elif self.__is_separator(character):
                self.__column += 1
                self.__add_token(character, TokenType.SEPARATOR)
                self.__position += 1
            # Operator
            else:
                self.__parse_operator(code)

    def __add_token(self, value, token_type):
        self.__tokens.append(Token(value, token_type, (self.__row, self.__column)))

    def __parse_whitespace(self, value):
        if value == ' ':
            self.__column += 1
        elif value == '\n':
            self.__row += 1
            self.__column = 0
        elif value == '\t':
            self.col = self.__config["TabsAndIndents"]["TabSize"] - (
                    (self.col - 1) % self.__config["TabsAndIndents"]["TabSize"])
        self.__add_token(value, TokenType.WHITESPACE)
        self.__position += 1

    def __parse_comment(self, code):
        if code[self.__position + 1] == '/':
            self.__parse_single_line_comment(code)
        elif code[self.__position + 1] == '*':
            self.__parse_multiple_line_comment(code)

    def __parse_single_line_comment(self, code):
        comment_end = code.find('\n', self.__position + 2)
        if comment_end == -1:
            comment_end = len(code)

        comment = code[self.__position:comment_end]
        self.__column += comment_end - self.__position
        self.__add_token(comment, TokenType.COMMENT)
        self.__position = comment_end

    def __parse_multiple_line_comment(self, code):
        comment_end = code.find('*/', self.__position + 2)
        comment = code[self.__position:comment_end]
        self.__column = comment_end + 2 - self.__position
        last_line = code.rfind('\n', self.__position, comment_end)
        if code.rfind('\n', self.__position, comment_end):
            self.__row += code.count('\n', self.__position, comment_end)
            self.__column = comment_end + 2 - last_line
        self.__add_token(comment, TokenType.COMMENT)
        self.__position = comment_end + 2

    def __parse_keyword_or_id(self, code):
        position = self.__parse_id(code)
        self.__column += position - self.__position
        identifier = code[self.__position:position]
        if identifier in self.__keywords:
            self.__add_token(identifier, TokenType.KEYWORD)
        else:
            self.__add_token(identifier, TokenType.IDENTIFIER)
        self.__position = position
        return

    def __parse_id(self, code):
        position = self.__position + 1
        while position < len(code) and (code[position].isdigit() or code[position].isalpha() or code[position] == '_'):
            position += 1
        return position

    def __parse_number_literal(self, code):
        regex = re.compile("([0-9]*[.])?[0-9]+")
        result = regex.search(code, self.__position)
        number_literal = code[self.__position:result.span()[1]]
        self.__column += result.span()[1] - self.__position
        self.__add_token(number_literal, TokenType.NUMBER_LITERAL)
        self.__position = result.span()[1]

    def __parse_string_literal(self, character, code):
        string_literal_end = code.find(character, self.__position + 1)
        string_literal = code[self.__position: string_literal_end + 1]
        self.__column += string_literal_end - self.__position
        self.__add_token(string_literal, TokenType.STRING_LITERAL)
        self.__position = string_literal_end + 1

    def __parse_annotation(self, code):
        position = self.__parse_id(code)
        annotation = code[self.__position:position]
        self.__column += position - self.__position
        self.__add_token(annotation, TokenType.ANNOTATION)
        self.__position = position

    def __is_separator(self, character):
        if character in self.__separators:
            return True

    def __parse_operator(self, code):
        for i in range(4, 0, -1):
            if self.__position + i > len(code):
                continue
            if code[self.__position:self.__position + i] in self.__operators:
                self.__column += i
                self.__add_token(code[self.__position:self.__position + i], TokenType.OPERATOR)
                self.__position = self.__position + i
                return
