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
                    parameters, i = self.__get_field_names(pos)
                    if self.__is_final(pos):
                        for parameter in parameters:
                            if not Formatter.is_snake_upper_case(parameter):
                                self.__to_fix[parameter] = Formatter.to_snake_upper_case(parameter)
                    else:
                        for parameter in parameters:
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

    def __get_field_names(self, i):
        params = []
        while self.__tokens[i].get_value() != ';':
            if self.__tokens[i + 1].get_value() in (';', '=', ','):
                pos = i
                while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
                    pos -= 1

                field_name = self.__tokens[pos].get_value()
                is_value = False
                if self.__tokens[i + 1].get_value() in (';', ','):
                    while pos > 0 and self.__tokens[pos].get_value() not in (';', '}'):
                        if self.__tokens[pos].get_value() == '=':
                            is_value = True
                        pos -= 1
                if not is_value:
                    params.append(field_name)
            i += 1
        end = i
        return params, end

    def __is_final(self, i):
        while self.__tokens[i].get_value() not in (';', '=', '('):
            if self.__tokens[i].get_value() == 'final':
                return True
            i += 1
        return False

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
                i = self.__fix_class_comments(i)
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
            elif self.__tokens[pos].get_type() in (TokenType.IDENTIFIER, TokenType.KEYWORD) and self.__tokens[
                pos + 1].get_value() != '.' and self.__tokens[pos].get_value() not in ('class', 'interface'):
                if self.__is_parameter(pos):
                    pos = self.__fix_field_comment(pos)
                else:
                    pos = self.__fix_method_comment(pos)
            pos += 1
        return pos

    def __fix_field_comment(self, pos):
        comment_token = self.__find_doc_comment_before(pos)
        indent = self.__get_indent(pos)
        if comment_token is None:
            field_names = ', '.join(self.__get_field_names(pos)[0])
            visibility = self.__find_visibility(pos)

            comment_token = Token(None, TokenType.COMMENT)
            comment_string = comment_string = f'{indent}/**\n' \
                                              f'{indent} * The {visibility} {field_names} {"constant" if self.__is_final(pos) else "variable"}{"s" if len(field_names) > 0 else ""}\n' \
                                              f'{indent} */'
            update_token_value(self.__file, comment_token, comment_string)

            insert_pos = self.__find_token_before(pos, '\n')
            self.__tokens.insert(insert_pos, Token('\n', TokenType.WHITESPACE))
            self.__tokens.insert(insert_pos + 1, comment_token)
        else:
            self.__fix_comment_links(comment_token)
        return self.__find_token_after(pos, ';')

    def __find_visibility(self, pos):
        pos = self.__find_token_before(pos, '\n')
        while self.__tokens[pos].get_value() not in ('=', ';', '('):
            if self.__tokens[pos].get_value() in ('private', 'public', 'protected'):
                return self.__tokens[pos].get_value()
            pos += 1
        return 'package-private'

    def __fix_method_comment(self, pos):
        comment_token = self.__find_doc_comment_before(pos)
        indent = self.__get_indent(pos)
        all_params = []
        if comment_token is None:
            params = self.__get_parameter_list(pos)
            params.extend(self.__get_type_parameter_list(pos))
            if len(params) > 0:
                all_params.append("\n".join([f"{indent} * @param {param}" for param in params]))
            throws = self.__get_throws(pos)
            if len(throws) > 0:
                all_params.append("\n".join([f"{indent} * @throws {param}" for param in throws]))
            return_type = self.__get_return_type(pos)
            if len(return_type) > 0:
                all_params.append(f"{indent} * @return {self.__get_return_type(pos)}")

            comment_token = Token(None, TokenType.COMMENT)
            comment_string = f'{indent}/**\n' + \
                             '\n'.join(all_params) + \
                             ('' if len(params) <= 0 else ' ') + \
                             f'\n{indent} */'
            update_token_value(self.__file, comment_token, comment_string)
            insert_pos = self.__find_token_before(pos, '\n')
            self.__tokens.insert(insert_pos, Token('\n', TokenType.WHITESPACE))
            self.__tokens.insert(insert_pos + 1, comment_token)
        else:
            self.__fix_comment_links(comment_token)

            params_list = self.__get_parameter_list(pos)
            params_list.extend(self.__get_type_parameter_list(pos))
            throws_list = self.__get_throws(pos)
            return_type_value = self.__get_return_type(pos)

            params, throws, return_type = self.__fix_comment_params(comment_token)
            comment_string = comment_token.get_value()

            append_string = ''
            i = 0
            if len(params) < len(params_list):
                append_string += "\n" + "\n".join(
                    [f"{indent} * @param {param}" for param in Formatter.get_missing(params, params_list)])
                i = comment_string.rfind('@param')
                if i != -1:
                    i = comment_string.find('\n', i) if comment_string.find('\n',
                                                                            i) != -1 else comment_string.find('*',
                                                                                                              i) - 1
                    comment_string = comment_string[:i] + append_string + comment_string[i:]
                    append_string = ''
            if len(throws) < len(throws_list):
                append_string += "\n" + "\n".join(
                    [f"{indent} * @throws {param}" for param in Formatter.get_missing(throws, throws_list)])
                i = comment_string.rfind('@throws')
                if i != -1:
                    i = comment_string.find('\n', i) if comment_string.find('\n',
                                                                            i) != -1 else comment_string.find('*',
                                                                                                              i) - 1
                    comment_string = comment_string[:i] + append_string + comment_string[i:]
                    append_string = ''
            i = comment_string.find('\n', i)
            if len(return_type) == '':
                append_string += "\n" + f"\n{indent} * @return {return_type_value}"
            else:
                i = comment_string.rfind('@return')
                while comment_string[i] != '\n':
                    i -= 1
            comment_string = comment_string[:i] + append_string + comment_string[i:]
            if comment_string != comment_token.get_value():
                update_token_value(self.__file, comment_token, comment_string)
        return self.__skip_method(pos)

    @staticmethod
    def get_missing(before, after):
        missing_params = []
        for value in after:
            if value not in before:
                missing_params.append(value)
        return missing_params

    def __get_parameter_list(self, pos):
        parameters = []
        while self.__tokens[pos].get_value() != '(':
            pos += 1
        while self.__tokens[pos].get_value() != ')':
            if self.__tokens[pos + 1].get_value() in (')', ','):
                i = pos
                while self.__tokens[i].get_type() == TokenType.WHITESPACE:
                    i -= 1
                parameters.append(self.__tokens[i].get_value())
            pos += 1
        return parameters

    def __get_type_parameter_list(self, pos):
        parameters = []
        while self.__tokens[pos].get_value() != '<':
            if self.__tokens[pos].get_value() == '(':
                return parameters
            pos += 1
        i = pos - 1
        while self.__tokens[i].get_type() == TokenType.WHITESPACE:
            i -= 1
        if self.__tokens[i].get_type() != TokenType.KEYWORD or self.__tokens[i].get_value() not in ('}', ';'):
            return parameters
        while self.__tokens[pos].get_value() != '>':
            if self.__tokens[pos - 1].get_value() in ('<', ','):
                i = pos
                while self.__tokens[i].get_type() == TokenType.WHITESPACE:
                    i += 1
                parameters.append(self.__tokens[i].get_value())
            pos += 1
        return parameters

    def __get_throws(self, pos):
        throws = []
        is_throws = False
        while self.__tokens[pos].get_value() not in ('{', ';'):
            if self.__tokens[pos].get_value() == 'throws':
                is_throws = True
            elif is_throws and self.__tokens[pos].get_type() == TokenType.IDENTIFIER:
                throws.append(self.__tokens[pos].get_value())
            pos += 1
        return throws

    def __get_return_type(self, pos):
        return_type = []
        while self.__tokens[pos].get_value() != '(':
            pos += 1
        pos -= 1
        while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
            pos -= 1
        while self.__tokens[pos].get_type() != TokenType.WHITESPACE:
            pos -= 1
        while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
            pos -= 1
        if self.__tokens[pos].get_value() == '>':
            while self.__tokens[pos].get_value() != '<':
                return_type.append(self.__tokens[pos].get_value())
                pos -= 1
            return_type.append(self.__tokens[pos].get_value())
            pos -= 1
        while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
            return_type.append(self.__tokens[pos].get_value())
            pos -= 1
        return_type.append(self.__tokens[pos].get_value())
        return_type.reverse()
        return ''.join(return_type)

    def __fix_comment_params(self, comment_token):
        i = 0
        params = []
        throws = []
        return_type = ''

        comment_string = comment_token.get_value()
        while i < len(comment_string):
            if comment_string[i] == '@':
                start = comment_string.find(' ', i)
                macro = comment_string[i:start]
                end = min(comment_string.find(' ', start + 1), comment_string.find('\n', start + 1))
                end = end if end >= 0 else max(comment_string.find(' ', start + 1),
                                               comment_string.find('\n', start + 1))
                if end > 0:
                    value = comment_string[start + 1:end]
                    new_value = self.__fix_link(value)
                    if value != new_value:
                        comment_string = comment_string.replace(value, new_value)
                        update_token_value(self.__file, comment_token, comment_string)
                        value = new_value
                    if macro == '@param':
                        params.append(value)
                    elif macro == '@throws':
                        throws.append(value)
                    elif macro == '@return':
                        return_type = value
            i += 1
        return params, throws, return_type

    def __skip_method(self, pos):
        while self.__tokens[pos].get_value() != '{':
            if self.__tokens[pos].get_value() == ';':
                return pos + 1
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
        i = 0
        link = None
        comment_string = comment_token.get_value()
        while i < len(comment_string):
            if comment_string[i] == '@':
                start = comment_string.find(' ', i)
                if comment_string[i:start] != '@see':
                    i += 1
                    continue
                end = comment_string.find('\n', i)
                link = comment_string[start:end]
            elif comment_string[i] == '{':
                start = comment_string.find(' ', i)
                end = comment_string.find('}', i)
                link = comment_string[start:end]
            if link is not None:
                new_link = self.__fix_link(link)
                comment_string = comment_string.replace(link, new_link)
                link = None
            i += 1
        if comment_string != comment_token.get_value():
            update_token_value(self.__file, comment_token, comment_string)

    def __fix_link(self, link):
        for name in self.__to_fix.keys():
            pos = link.find(name)
            if pos != -1 and not (link[pos - 1].isalpha() or link[
                pos - 1].isdigit() or link[pos - 1] == '_'):
                link = link.replace(name, self.__to_fix[name])

        return link

    def __get_indent(self, pos):
        pos = self.__find_token_before(pos, '\n')
        count = 0
        while self.__tokens[pos].get_type() == TokenType.WHITESPACE:
            if self.__tokens[pos].get_value() == ' ':
                count += 1
            pos += 1
        return ' ' * count

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
