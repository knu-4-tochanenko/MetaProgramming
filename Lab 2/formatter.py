import re
from lexer import parse
from java_token import TokenType, update_token_value


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
            elif token.get_value() in ('class', 'interface'):
                i = self.__skip_ws_tokens(i + 1)
                if not Formatter.is_camel_upper_case(self.__tokens[i].get_value()):
                    self.__to_fix[self.__tokens[i].get_value()] = Formatter.to_camel_upper_case(
                        self.__tokens[i].get_value())
                self.__fix_class_body(i, self.__tokens[i].get_value())
            i += 1

    def __fix_package(self, pos):
        pos = self.__skip_ws_tokens(pos)
        while self.__tokens[pos].get_value() != ';':
            if self.__tokens[pos].get_type() == TokenType.IDENTIFIER and not Formatter.is_lower_case(
                    self.__tokens[pos].get_value()):
                self.__to_fix[self.__tokens[pos]] = Formatter.to_lower_case((self.__tokens[pos]))
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
        while self.__tokens[i].get_value() != '{':
            if self.__tokens[i].get_value() in method_parameters.keys():
                update_token_value(self.__file, self.__tokens[i], method_parameters[self.__tokens[i].get_value()])
            i += 1
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
        components = [component.lower() if component.isupper() else component[0].upper() + component[1:] for component
                      in naming.split('_')]
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
