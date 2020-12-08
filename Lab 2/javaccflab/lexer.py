import re
from java_token import Token, TokenType

keywords = ('abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue',
            'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float', 'for', 'goto', 'if',
            'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new', 'package', 'private',
            'protected', 'public', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this',
            'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while')
operators = (
    '++', '--', '!', '~', '+', '-', '*', '/', '%', '<<', '>>', '>>>', '<', '>', '<=', '>=', '==', '!=', '&', '^', '|',
    '&&',
    '||', ':', '::', '=', '+=', '-=', '*=', '/=', '%=', '&=', '^=', '|=', '<<=', '>>=', '>>>=')
separators = (';', ',', '.', '(', ')', '{', '}', '[', ']')


def parse(code):
    tokens = []
    i = 0
    while i < len(code):
        current_char = code[i]
        if current_char.isspace():
            tokens.append(Token(current_char, TokenType.WHITESPACE))
            i += 1
        elif current_char.isalpha() or current_char == '_':
            identifier, i = parse_identifier(code, i)
            if identifier in keywords:
                tokens.append(Token(identifier, TokenType.KEYWORD))
            else:
                tokens.append(Token(identifier, TokenType.IDENTIFIER))
        elif current_char == '@':
            identifier, i = parse_identifier(code, i + 1)
            tokens.append(Token('@' + identifier, TokenType.ANNOTATION))
        elif current_char == '/' and code[i + 1] in ('/', '*'):
            if code[i + 1] == '*':
                comment, i = parse_multiple_line_comment(code, i)
                tokens.append(Token(comment, TokenType.COMMENT))
            elif code[i + 1] == '/':
                comment, i = parse_single_line_comment(code, i)
                tokens.append(Token(comment, TokenType.COMMENT))
        elif current_char.isdigit():
            literal, i = parse_number_literal(code, i)
            tokens.append(Token(literal, TokenType.NUMBER_LITERAL))
        elif current_char in ('"', "'"):
            literal, i = parse_sting_literal(code, current_char, i)
            tokens.append(Token(literal, TokenType.STRING_LITERAL))
        elif current_char in separators:
            tokens.append(Token(current_char, TokenType.SEPARATOR))
            i += 1
        else:
            operator, i = parse_operator(code, i)
            tokens.append(Token(operator, i))
    return tokens


def parse_identifier(code, pos):
    i = pos + 1
    while pos < len(code) and (code[i].isalpha() or code[i] == '_' or code[i].isdigit()):
        i += 1
    return code[pos:i], i


def parse_sting_literal(code, separator, pos):
    end = pos
    while end < len(code):
        end = code.find(separator, end + 1)
        if code[end - 1] != '\\':
            break

    return code[pos:end + 1], end + 1


def parse_number_literal(code, pos):
    regex = re.compile(
        "(0x([0-9a-fA-F]*_?)*)|((?:\d*[a-zA-Z]*)*)|(\d*(?:(?=\d*)\.\d*)(?:E?(?=[-|\d]*)-?\d*))|(([0-9]*[.])?[0-9]+)|").search(
        code, pos)
    literal = code[pos:regex.span()[1]]
    return literal, regex.span()[1]


def parse_operator(code, pos):
    for i in range(4, 0, -1):
        if not (pos + i > len(code)) and code[pos:pos + i] in operators:
            return code[pos:pos + i], pos + i


def parse_single_line_comment(code, pos):
    end = code.find('\n', pos + 1)
    if end == -1:
        end = len(code) - 1
    return code[pos:end], end


def parse_multiple_line_comment(code, pos):
    end = code.find('\n', pos + 1)
    if end == -1:
        end = len(code) - 1
    return code[pos:end], end
