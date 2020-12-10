import re
import datetime
from javaccflab.lexer import parse
from javaccflab.java_token import TokenType, Token, update_token_value


class Formatter:
    def __init__(self, files):
        self.__files = files
        self.__file = None
        self.__tokens = []
        self.__to_fix = dict()

    def process(self):
        tokens = []
        for file in self.__files:
            tokens.append(parse(open(file, 'r').read()))
        i = 0
        while i < len(tokens):
            self.__tokens = tokens[i]
            self.__file = self.__files[i]
            self.__find_to_fix()
            tokens[i] = self.__tokens
            i += 1
        i = 0
        while i < len(tokens):
            self.__tokens = tokens[i]
            self.__file = self.__files[i]
            self.__fix()
            self.__fix_comments()
            tokens[i] = self.__tokens
            i += 1
        return tokens

    def __find_to_fix(self):
        i = 0
        while i < len(self.__tokens):
            token = self.__tokens[i]
            if token.get_value() == 'package':
                i = self.__fix_package(i)
            elif token.get_value() in ('class', 'interface') and self.__tokens[i - 1].get_value() != '.':
                i = self.__skip_ws_tokens(i + 1)
                if not Formatter.is_camel_upper_case(self.__tokens[i].get_value()):
                    self.__to_fix[self.__tokens[i].get_value()] = Formatter.to_camel_upper_case(
                        self.__tokens[i].get_value())
                i = self.__fix_class_body(i, self.__tokens[i].get_value())
            i += 1

    def __fix_package(self, pos):
        pos = self.__skip_ws_tokens(pos)
        while self.__tokens[pos].get_value() != ';':
            if self.__tokens[pos].get_type() == TokenType.IDENTIFIER and not Formatter.is_lower_case(
                    self.__tokens[pos].get_value()):
                self.__to_fix[self.__tokens[pos].get_value()] = Formatter.to_lower_case(
                    (self.__tokens[pos].get_value()))
            pos += 1

        return pos

    def __fix_class_body(self, pos, class_name):
        while self.__tokens[pos].get_value() != '{':
            pos += 1
        count = 1
        pos += 1
        while count != 0:
            if self.__tokens[pos].get_value() == '{':
                count += 1
            elif self.__tokens[pos].get_value() == '}':
                count -= 1
            elif self.__tokens[pos].get_value() == 'static':
                i = self.__skip_ws_tokens(pos + 1)
                if self.__tokens[i].get_value() == '{':
                    pos = i + 1
                    count += 1
                    continue
            elif self.__tokens[pos].get_type() in (TokenType.IDENTIFIER, TokenType.KEYWORD):
                if self.__is_parameter(pos):
                    parameter, i = self.__get_parameter_name(pos)
                    if self.__is_final(pos):
                        if not Formatter.is_snake_upper_case(parameter):
                            self.__to_fix[parameter] = Formatter.to_snake_upper_case(parameter)
                    else:
                        if not Formatter.is_camel_lower_case(parameter):
                            self.__to_fix[parameter] = Formatter.to_camel_lower_case(parameter)
                    pos = i
                else:
                    self.__fix_method_name(pos, class_name)
                    parameters = self.__get_method_parameters(pos)
                    pos = self.__fix_method_body(pos, parameters)
            pos += 1
        return pos

    def __fix_method_name(self, i, class_name):
        while self.__tokens[i].get_value() not in ('(', ';'):
            i += 1
        i -= 1
        while self.__tokens[i].get_type() == TokenType.WHITESPACE:
            i -= 1
        if self.__tokens[i].get_value() != class_name and not Formatter.is_snake_lower_case(
                self.__tokens[i].get_value()):
            self.__to_fix[self.__tokens[i].get_value()] = Formatter.to_snake_lower_case(self.__tokens[i].get_value())

    def __get_method_parameters(self, i):
        parameters = dict()
        while self.__tokens[i].get_value() != '(':
            i += 1
        while self.__tokens[i].get_value() != ')':
            if self.__tokens[i + 1].get_value() in (')', ','):
                pos = i
                while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
                    pos -= 1
                if not Formatter.is_camel_lower_case(self.__tokens[pos].get_value()):
                    fixed_value = Formatter.to_camel_lower_case(self.__tokens[pos].get_value())
                    parameters[self.__tokens[pos].get_value()] = fixed_value
                    update_token_value(self.__file, self.__tokens[pos], fixed_value)
            i += 1
        return parameters

    def __fix_method_body(self, i, method_parameters):
        params = dict()
        while self.__tokens[i].get_value() not in ('{', ';'):
            if self.__tokens[i].get_value() in method_parameters.keys():
                update_token_value(self.__file, self.__tokens[i], method_parameters[self.__tokens[i].get_value()])
            i += 1

        if self.__tokens[i].get_value() == ';':
            return i + 1
        brace_count = 1
        i += 1
        while brace_count != 0:
            if self.__tokens[i].get_value() == '{':
                brace_count += 1
            elif self.__tokens[i].get_value() == '}':
                brace_count -= 1
            elif self.__tokens[i].get_value() in ('=', ';'):
                naming_pos = i - 1
                while self.__tokens[naming_pos].get_type() == TokenType.WHITESPACE:
                    naming_pos -= 1
                if self.__tokens[naming_pos].get_type() == TokenType.IDENTIFIER:
                    type_pos = naming_pos - 1
                    while self.__tokens[type_pos].get_type() == TokenType.WHITESPACE:
                        type_pos -= 1
                    if (self.__tokens[type_pos].get_type() in (TokenType.IDENTIFIER, TokenType.KEYWORD) and \
                        self.__tokens[type_pos].get_value() not in ('class', 'identifier')) or self.__tokens[
                        type_pos].get_value() == ',':
                        if not Formatter.is_camel_lower_case(self.__tokens[naming_pos].get_value()):
                            fixed_value = Formatter.to_camel_lower_case(self.__tokens[naming_pos].get_value())
                            params[self.__tokens[naming_pos].get_value()] = fixed_value
                            update_token_value(self.__file, self.__tokens[naming_pos], fixed_value)
            elif self.__tokens[i].get_type() == TokenType.IDENTIFIER and self.__tokens[
                i].get_value() in params.keys():
                update_token_value(self.__file, self.__tokens[i], params[self.__tokens[i].get_value()])
            elif self.__tokens[i].get_type() == TokenType.IDENTIFIER and self.__tokens[
                i].get_value() in method_parameters.keys():
                update_token_value(self.__file, self.__tokens[i], method_parameters[self.__tokens[i].get_value()])
            i += 1
        return i

    def __get_parameter_name(self, i):
        while self.__tokens[i].get_value() not in (';', '='):
            i += 1
        end = i
        i -= 1
        while self.__tokens[i].get_type() == TokenType.WHITESPACE:
            i -= 1

        if self.__tokens[end].get_value() != ';':
            while self.__tokens[end].get_value() != ';':
                end += 1

        return self.__tokens[i].get_value(), end

    def __is_final(self, i):
        while self.__tokens[i].get_value() not in (';', '=', '('):
            if self.__tokens[i].get_value() == 'final':
                return True
            i += 1
        return False

    def __fix_constant(self, i):
        parameter, end = self.__get_parameter_name(i)
        if not Formatter.is_snake_upper_case(parameter):
            self.__to_fix[parameter] = Formatter.to_snake_upper_case(parameter)
        return parameter, end

    def __is_parameter(self, pos):
        while self.__tokens[pos].get_value() != ';' and pos < len(self.__tokens):
            if self.__tokens[pos].get_value() == '=':
                return True
            elif self.__tokens[pos].get_value() in ('class', 'interface', '(', ')'):
                return False
            pos += 1
        return True

    def __fix(self):
        for token in self.__tokens:
            if token.get_value() in self.__to_fix and not token.is_fixed():
                update_token_value(self.__file, token, self.__to_fix[token.get_value()])

    def __fix_comments(self):
        self.__add_start_comment()

        i = 0
        while i < len(self.__tokens):
            if self.__tokens[i].get_value() in ('class', 'interface'):
                pass
                # TODO: increment i
                self.__fix_class_comments(i)
                i += 1
            i += 1

    #  Fix start comment
    def __add_start_comment(self):
        if not self.__is_start_comment_exists():
            comment_token = Token(None, TokenType.COMMENT)
            comment_string = f'/*\n' \
                             f' * {self.__find_class_name()}\n' \
                             f' *\n' \
                             f' * {datetime.date.today().strftime("%B %d, %Y")}\n' \
                             f' */'
            update_token_value(self.__file, comment_token, comment_string)
            self.__tokens.insert(0, comment_token)
            self.__tokens.insert(1, Token('\n', TokenType.WHITESPACE))
            self.__tokens.insert(1, Token('\n', TokenType.WHITESPACE))

    def __is_start_comment_exists(self):
        i = self.__skip_ws_tokens(0)
        return self.__tokens[i].get_type() == TokenType.COMMENT

    def __find_class_name(self, i=0):
        while self.__tokens[i].get_value() not in ('class', 'interface') and self.__tokens[i - 1].get_value() != '.':
            i += 1
        i = self.__skip_ws_tokens(i + 1)
        return self.__tokens[i].get_value()

    # Fix class comment
    def __fix_class_comments(self, pos):
        comment_token = self.__find_doc_comment_before(pos)
        if comment_token is None:
            comment_token = Token(None, TokenType.COMMENT)
            comment_string = f'/**\n' \
                             f' * Implementation of {self.__find_class_name(pos)}\n' \
                             f' */'
            update_token_value(self.__file, comment_token, comment_string)

            insert_pos = self.__find_token_before(pos, '\n')
            self.__tokens.insert(insert_pos, Token('\n', TokenType.WHITESPACE))
            self.__tokens.insert(insert_pos + 1, comment_token)
        else:
            self.__fix_comment_links(comment_token)

        return self.__fix_class_body_comments(pos)

    # Fix comments for methods and fields
    def __fix_class_body_comments(self, pos):
        while self.__tokens[pos].get_value() != '{':
            pos += 1
        count = 1
        pos += 1
        while count != 0:
            if self.__tokens[pos].get_value() == '{':
                count += 1
            elif self.__tokens[pos].get_value() == '}':
                count -= 1
            elif self.__tokens[pos].get_value() == 'static':
                i = self.__skip_ws_tokens(pos + 1)
                if self.__tokens[i].get_value() == '{':
                    pos = i + 1
                    count += 1
                    continue
            elif self.__tokens[pos].get_type() in (TokenType.IDENTIFIER, TokenType.KEYWORD):
                if self.__is_parameter(pos):
                    pos = self.__fix_field_comment(pos)
                else:
                    pos = self.__fix_method_comment(pos)
            pos += 1
        return pos

    def __fix_field_comment(self, pos):
        comment_token = self.__find_doc_comment_before(pos)
        if comment_token is None:
            field_name = self.__find_field_name(pos)
            visibility = self.__find_visibility(pos)

            comment_token = Token(None, TokenType.COMMENT)
            comment_string = comment_string = f'/**\n' \
                                              f' * The {visibility} {field_name} {"constant" if self.__is_final(pos) else "variable"}\n' \
                                              f' */'
            update_token_value(self.__file, comment_token, comment_string)

            insert_pos = self.__find_token_before(pos, '\n')
            self.__tokens.insert(insert_pos, Token('\n', TokenType.WHITESPACE))
            self.__tokens.insert(insert_pos + 1, comment_token)
        else:
            self.__fix_comment_links(comment_token)
        return self.__find_token_after(pos, ';')

    def __find_field_name(self, pos):
        while self.__tokens[pos].get_value() not in (';', '='):
            pos += 1
        pos -= 1
        while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
            pos -= 1

        return self.__tokens[pos].get_value()

    def __find_visibility(self, pos):
        pos = self.__find_token_before(pos, '\n')
        while self.__tokens[pos].get_value() not in ('=', ';', '('):
            if self.__tokens[pos].get_value() in ('private', 'public', 'protected'):
                return self.__tokens[pos].get_value()
            pos += 1
        return 'package-private'

    def __fix_method_comment(self, pos):
        comment_token = self.__find_doc_comment_before(pos)
        if comment_token is None:
            pass
        else:
            pass
        return self.__skip_method(pos)

    def __skip_method(self, pos):
        while self.__tokens[pos].get_value() != '{':
            pos += 1

        count = 1
        pos += 1

        while count != 0:
            if self.__tokens[pos].get_value() == '{':
                count += 1
            elif self.__tokens[pos].get_value() == '}':
                count -= 1
            pos += 1

        return pos

    def __find_doc_comment_before(self, pos):
        while self.__tokens[pos].get_value() != '\n':
            pos -= 1
        while pos > 0 and self.__tokens[pos].get_type() == TokenType.WHITESPACE:
            pos -= 1
        if self.__tokens[pos].get_type() == TokenType.COMMENT and self.__tokens[pos].get_value().startswith('/**'):
            return self.__tokens[pos]

        return None

    def __find_token_before(self, pos, value):
        while pos > 0 and self.__tokens[pos].get_value() != value:
            pos -= 1
        return pos

    def __find_token_after(self, pos, value):
        while pos < len(self.__tokens) and self.__tokens[pos].get_value() != value:
            pos += 1
        return pos

    def __fix_comment_links(self, comment_token):
        pass

    def __skip_ws_tokens(self, pos):
        while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
            pos += 1
        return pos

    @staticmethod
    def is_lower_case(naming):
        return naming.find('_') == -1 and naming.islower()

    @staticmethod
    def to_lower_case(naming):
        return ''.join([component.lower() for component in naming.split('_')])

    @staticmethod
    def is_camel_lower_case(naming):
        return naming.find('_') == -1 and not naming.isupper() and not naming[0].isupper()

    @staticmethod
    def to_camel_lower_case(naming):
        naming = Formatter.remove_underscores_around(naming)
        components = [
            component[0] + component[1:].lower() if component.isupper() else component[0].upper() + component[1:] for
            component in naming.split('_')]
        return components[0][0].lower() + components[0][1:] + ''.join(components[1:])

    @staticmethod
    def is_camel_upper_case(naming):
        return naming.find('_') == -1 and not naming.isupper() and naming[0].isupper()

    @staticmethod
    def to_camel_upper_case(naming):
        lower = Formatter.to_camel_lower_case(naming)
        return lower[0].upper() + lower[1:]

    @staticmethod
    def is_snake_lower_case(naming):
        return naming.islower()

    @staticmethod
    def to_snake_lower_case(naming):
        naming = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', naming)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', naming).lower()

    @staticmethod
    def is_snake_upper_case(naming):
        return naming.isupper()

    @staticmethod
    def to_snake_upper_case(naming):
        return Formatter.to_snake_lower_case(naming).upper()

    @staticmethod
    def remove_underscores_around(naming):
        i = 0
        while naming[i] == '_':
            i += 1
        naming = naming[i:]
        j = len(naming) - 1
        while naming[j] == '_':
            i -= 1
        naming = naming[:j + 1]
        return naming
