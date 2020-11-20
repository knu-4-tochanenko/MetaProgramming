# from Lexer import Token, TokenType
#
#
# class Formatter:
#     __formatting_keywords = ('class', 'do', 'else', 'for', 'if', 'interface', 'switch', 'try', 'while')
#     __space_token = Token(' ', TokenType.WHITESPACE)
#     __new_line_token = Token('\n', TokenType.WHITESPACE)
#
#     def __init__(self, tokens, config):
#         self.__tokens = tokens
#         self.__config = config
#         self.__i = 0
#
#         # Indents
#         self.__is_indent = False
#         self.__indent = self.__config.get_tabs_and_indents().get_indent()
#         self.__current_indent = 0
#         self.__additional_indent = 0
#         self.__case_indent = 0
#
#         # New Line
#         self.__new_line_token = Token(TokenType.WHITESPACE, '\n')
#
#         self.__is_generic_found = False
#
#     def format(self):
#         self.__remove_formatting()
#         # format
#         self.__add_blank_lines()
#         self.__add_spaces()
#         self.__add_tabs_and_indents()
#         return self.__tokens
#
#     def __remove_formatting(self):
#         i = 0
#         while i < len(self.__tokens):
#             if self.__tokens[i].get_value() in ('\t', ' '):
#                 self.__tokens.pop(i)
#             else:
#                 i += 1
#
#     # Tabs And Indents
#     def __add_tabs_and_indents(self):
#         self.__i = 0
#         stack = []
#
#         do_not_indent_top_level_class_members = self.__config.get_tabs_and_indents().get_do_not_indent_top_level_class_members()
#
#         while self.__i < len(self.__tokens):
#             # label indent + absolute label indent
#             self.__add_label_indent()
#
#             # keep indents on empty lines
#             self.__add_empty_line_indent(stack)
#
#             if self.__tokens[self.__i].get_value() in self.__formatting_keywords:
#                 stack.append(self.__tokens[self.__i].get_value())
#
#             elif self.__tokens[self.__i].get_value() == '{':
#                 self.__case_indent = 0
#                 if not (do_not_indent_top_level_class_members
#                         and len(stack) >= 1
#                         and stack[-1] == 'class'):
#                     self.__current_indent += self.__indent
#                 stack.append('{')
#
#             elif self.__tokens[self.__i].get_value() == '}':
#                 if len(stack) != 0:
#                     while stack.pop() != '{':
#                         continue
#                 if not (do_not_indent_top_level_class_members
#                         and len(stack) >= 1
#                         and stack[-1] == 'class'):
#                     self.__current_indent -= self.__indent
#                 if len(stack) > 0 and stack[-1] in self.__formatting_keywords:
#                     stack.pop()
#                 if self.__is_indent:
#                     self.__add_indents()
#                     self.__is_indent = False
#                 self.__case_indent = 0
#
#             elif self.__tokens[self.__i].get_value() == 'case' or (
#                     'switch' in stack and self.__tokens[self.__i].get_value() == 'default'):
#                 self.__case_indent = 0
#                 self.__add_indents()
#                 self.__case_indent = self.__indent
#
#             elif self.__tokens[self.__i].get_value() == '\n':
#                 self.__is_indent = True
#                 if len(stack) > 1 and stack[-1] in self.__formatting_keywords:
#                     self.__additional_indent += self.__indent
#                     stack.pop()
#                 elif self.__tokens[self.__i - 1].get_value() == ')' and self.__tokens[self.__i + 1].get_value() == '.':
#                     self.__additional_indent += self.__config.get_tabs_and_indents().get_continuation_indent()
#
#             elif self.__tokens[self.__i].get_value() == ';':
#                 if len(stack) > 1 and stack[-1] in self.__formatting_keywords:
#                     stack.pop()
#                 self.__additional_indent = 0
#             self.__i += 1
#
#     def __add_label_indent(self):
#         if self.__is_indent and self.__is_label(self.__i):
#             label_indent = 0
#             if not self.__config.get_tabs_and_indents().get_absolute_label_indent:
#                 label_indent = self.__current_indent + self.__case_indent + self.__additional_indent
#             label_indent += self.__config.get_tabs_and_indents().get_label_indent()
#             for _ in range(label_indent):
#                 self.__tokens.insert(self.__i, Formatter.__space_token)
#                 self.__i += 1
#             self.__is_indent = False
#             self.__i += 1
#
#     def __add_empty_line_indent(self, stack):
#         if self.__is_indent and self.__is_keep_indents_on_empty_lines_case(self.__i, stack):
#             self.__add_indents()
#
#     def __add_indents(self):
#         for _ in range(self.__current_indent + self.__case_indent + self.__additional_indent):
#             self.__tokens.insert(self.__i, Formatter.__space_token)
#             self.__i += 1
#         self.__additional_indent = 0
#         self.__is_indent = False
#
#     def __is_label(self, i):
#         return self.__tokens[i].get_token_type() == TokenType.IDENTIFIER and \
#                self.__tokens[i + 1].get_value() == ':' and \
#                self.__find_token_by_value('?', i - 10, i) == -1
#
#     def __is_keep_indents_on_empty_lines_case(self, i, stack):
#         return self.__tokens[i].get_value() not in ('}', 'case') \
#                and not ('switch' in stack and self.__tokens[i].get_value() == 'default') \
#                and ((not self.__tokens[i] == '\n')
#                     or self.__config.get_tabs_and_indents().get_keep_indents_on_empty_lines())
#
#     def __find_token_by_value(self, value, range_from=0, range_to=-1):
#         if range_to < 0:
#             range_to = len(self.__tokens) - range_to
#         for i in range(range_from, range_to, 1):
#             if self.__tokens[i].get_value() == value:
#                 return i
#         return -1
#
#     # Spaces
#     def __add_spaces(self):
#         self.__add_spaces_between_tokens()
#         self.__add_spaces_before_parentheses()
#         self.__add_spaces_around_operators()
#         self.__add_spaces_before_keywords()
#         self.__add_spaces_in_ternary_operator()
#         self.__add_spaces_before_left_brace()
#         self.__add_other_spaces()
#         self.__add_spaces_type_parameters_and_arguments()
#
#     def __add_spaces_between_tokens(self):
#         self.__i = 1
#         token_types = (TokenType.KEYWORD, TokenType.IDENTIFIER, TokenType.NUMBER_LITERAL, TokenType.STRING_LITERAL)
#         while self.__i < len(self.__tokens):
#             if self.__tokens[self.__i].get_token_type() in token_types \
#                     and (self.__tokens[self.__i - 1].get_token_type() in token_types
#                          or self.__tokens[self.__i - 1].get_value() == ']'):
#                 self.__tokens.insert(self.__i, Formatter.__space_token)
#                 self.__i += 1
#             self.__i += 1
#
#     # Spaces -> BeforeParentheses
#     def __add_spaces_before_parentheses(self):
#         config = self.__config.get_spaces().get_before_parentheses()
#         self.__add_spaces_before_method_and_annotation(config.get_method_declaration_parentheses(),
#                                                        config.get_method_call_parentheses(),
#                                                        config.get_annotation_parameters())
#         self.__add_space_after_token('if', config.get_if_parentheses())
#         self.__add_space_after_token('for', config.get_for_parentheses())
#         self.__add_space_after_token('while', config.get_while_parentheses())
#         self.__add_space_after_token('switch', config.get_switch_parentheses())
#         self.__add_space_after_token('try', config.get_try_parentheses())
#         self.__add_space_after_token('catch', config.get_catch_parentheses())
#         self.__add_space_after_token('synchronized', config.get_synchronized_parentheses())
#
#     def __add_spaces_before_method_and_annotation(self, method_declaration_rule, method_call_rule, annotation_rule):
#         if method_declaration_rule or method_call_rule or annotation_rule:
#             i = 0
#             while i < len(self.__tokens) - 1:
#
#                 if self.__tokens[i + 1].get_value() == '(':
#                     if self.__tokens[i].get_token_type() == TokenType.IDENTIFIER:
#                         if method_declaration_rule and self.__is_method_declaration(i):
#                             self.__tokens.insert(i + 1, Formatter.__space_token)
#                             i += 1
#                         elif method_call_rule:
#                             self.__tokens.insert(i + 1, Formatter.__space_token)
#                             i += 1
#                     elif annotation_rule and self.__tokens[i].get_token_type() == TokenType.ANNOTATION:
#                         self.__tokens.insert(i + 1, Formatter.__space_token)
#                         i += 1
#                     i += 1
#                 i += 1
#
#     def __add_space_after_method_declaration(self, rule):
#         if rule:
#             for i in range(0, len(self.__tokens) - 1, 1):
#                 if self.__tokens[i].get_token_type() == TokenType.IDENTIFIER \
#                         and self.__tokens[i + 1].get_value() == '(':
#                     if self.__is_method_declaration(i):
#                         self.__tokens.insert(i + 1, Formatter.__space_token)
#
#     def __add_space_after_method_call_or_annotation(self, rule):
#         if rule:
#             for i in range(0, len(self.__tokens) - 1, 1):
#                 if self.__tokens[i].get_token_type() in (TokenType.IDENTIFIER, TokenType.ANNOTATION) \
#                         and self.__tokens[i + 1].get_value() == '(':
#                     self.__tokens.insert(i + 1, Formatter.__space_token)
#
#     def __is_method_declaration(self, pos):
#         while self.__tokens[pos].get_value() != '\n':
#             pos -= 1
#         pos += 1
#         brace_found = False
#         brace_count = 0
#         id_number = 0
#
#         while pos < len(self.__tokens):
#             if self.__tokens[pos].get_value() == ';' and id_number > 1 and brace_found and brace_count == 0:
#                 return True
#             elif self.__tokens[pos].get_value() in (';', '='):
#                 return False
#             elif self.__tokens[pos].get_value() == '(':
#                 brace_found = True
#                 brace_count += 1
#             elif self.__tokens[pos].get_value() == ')':
#                 brace_count -= 1
#             elif brace_found and brace_count == 0 and self.__tokens[pos].get_value() == '{':
#                 return True
#             elif self.__tokens[pos].get_token_type() in (TokenType.IDENTIFIER, TokenType.KEYWORD):
#                 id_number += 1
#             pos += 1
#         return False
#
#     # IfParentheses, ForParentheses, WhileParentheses, SwitchParentheses, TryParentheses, CatchParentheses, SynchronizedParentheses
#     def __add_space_after_token(self, value, rule):
#         if rule:
#             for i in range(0, len(self.__tokens), 1):
#                 if self.__tokens[i].get_value() == value and self.__tokens[i + 1].get_value() == '(':
#                     self.__tokens.insert(i + 1, Formatter.__space_token)
#                     i += 1
#                 i += 1
#
#     def __add_spaces_around_operators(self):
#         self.__i = 0
#         config = self.__config.get_spaces().get_around_operators()
#         while self.__i < len(self.__tokens):
#             if self.__tokens[self.__i].get_token_type() == TokenType.OPERATOR:
#                 if self.__tokens[self.__i].get_value() in ('=', '+='):
#                     self.__add_spaces_around_current_position(config.get_assignment_operators())
#                 elif self.__tokens[self.__i].get_value() in ('&&', '||'):
#                     self.__add_spaces_around_current_position(config.get_logical_operators())
#                 elif self.__tokens[self.__i].get_value() in ('==', '!='):
#                     self.__add_spaces_around_current_position(config.get_equality_operators())
#                 elif self.__tokens[self.__i].get_value() in ('<', '>') and not self.__is_generic(self.__i):
#                     self.__add_spaces_around_current_position(config.get_relational_operators())
#                 elif self.__tokens[self.__i].get_value() in ('<=', '>='):
#                     self.__add_spaces_around_current_position(config.get_relational_operators())
#                 elif self.__tokens[self.__i].get_value() in ('&', '|', '^'):
#                     self.__add_spaces_around_current_position(config.get_bitwise_operators())
#                 elif self.__tokens[self.__i].get_value() in ('*', '/', '%'):
#                     self.__add_spaces_around_current_position(config.get_multiplicative_operators())
#                 elif self.__tokens[self.__i].get_value() in ('<<', '>>', '>>>'):
#                     self.__add_spaces_around_current_position(config.get_shift_operators())
#                 elif self.__tokens[self.__i].get_value() == '->':
#                     self.__add_spaces_around_current_position(config.get_lambda_arrow())
#                 elif self.__tokens[self.__i].get_value() == '::':
#                     self.__add_spaces_around_current_position(config.get_method_reference_double_colon())
#                 elif self.__tokens[self.__i].get_value() in ('!', '++', '--'):
#                     self.__tokens.insert(self.__i + 1, Formatter.__space_token)
#                     self.__i += 1
#                 elif self.__tokens[self.__i].get_value() in ('+', '-'):
#                     if self.__is_unary_operator(self.__i):
#                         self.__tokens.insert(self.__i + 1, Formatter.__space_token)
#                         self.__i += 1
#                     else:
#                         self.__add_spaces_around_current_position(config.get_additive_operators())
#             self.__i += 1
#
#     def __is_unary_operator(self, pos):
#         pos -= 1
#         while self.__tokens[pos].get_value() == ' ':
#             pos -= 1
#         token = self.__tokens[pos]
#         if token.get_token_type() != TokenType.OPERATOR or token.get_value() in ('++', '--'):
#             return False
#         return True
#
#     def __add_spaces_around_current_position(self, rule):
#         if rule:
#             self.__tokens.insert(self.__i, Formatter.__space_token)
#             self.__tokens.insert(self.__i + 2, Formatter.__space_token)
#             self.__i += 2
#
#     def __is_generic(self, pos):
#         if self.__tokens[pos] == '>' and self.__is_generic_found:
#             self.__is_generic_found = False
#             return True
#         if self.__tokens[self.__i].get_value() == '<':
#             pos += 1
#             while self.__tokens[pos].get_token_type() == TokenType.WHITESPACE:
#                 pos += 1
#                 result = self.__tokens[pos].get_value()[0]
#                 self.__is_generic_found = result.isalpha() and result.isupper() or result in ('>', '?')
#                 return self.__is_generic_found
#         return False
#
#     # BeforeKeywords
#     def __add_spaces_before_keywords(self):
#         self.__i = 0
#         config = self.__config.get_spaces().get_before_keywords()
#
#         while self.__i < len(self.__tokens):
#             if self.__tokens[self.__i].get_token_type() == TokenType.KEYWORD:
#                 if self.__tokens[self.__i].get_value() == 'else':
#                     self.__add_space_between_parentheses_and_bracket(config.get_else_keyword())
#                 elif self.__tokens[self.__i].get_value() == 'while':
#                     self.__add_space_between_parentheses_and_bracket(config.get_while_keyword())
#                 elif self.__tokens[self.__i].get_value() == 'catch':
#                     self.__add_space_between_parentheses_and_bracket(config.get_catch_keyword())
#                 elif self.__tokens[self.__i].get_value() == 'finally':
#                     self.__add_space_between_parentheses_and_bracket(config.get_finally_keyword())
#             self.__i += 1
#
#     def __add_space_between_parentheses_and_bracket(self, rule):
#         if rule:
#             if self.__tokens[self.__i - 1].get_value() == '}':
#                 self.__tokens.insert(self.__i, Formatter.__space_token)
#                 self.__i += 1
#
#     # InTernaryOperator
#     def __add_spaces_in_ternary_operator(self):
#         config = self.__config.get_spaces().get_in_ternary_operator()
#         self.__i = 0
#         while self.__i < len(self.__tokens):
#             if self.__tokens[self.__i].get_value() == '?':
#                 colon_pos = self.__find_ternary_colon(self.__i)
#                 if colon_pos != -1:
#                     self.__insert_space_after_single_token(colon_pos + 1, config.get_after_colon())
#                     self.__insert_space_after_single_token(colon_pos, config.get_before_colon())
#                     self.__insert_space_after_single_token(self.__i + 1, config.get_after_question_mark())
#                     self.__insert_space_after_single_token(self.__i, config.get_before_question_mark())
#                     self.__i += 1
#             self.__i += 1
#
#     def __find_ternary_colon(self, pos):
#         brace_count = 0
#         parentheses_count = 0
#         while pos < len(self.__tokens):
#             if self.__tokens[pos].get_value() == '(':
#                 brace_count += 1
#             elif self.__tokens[pos].get_value() == '(':
#                 brace_count -= 1
#                 if brace_count < 0:
#                     return -1
#             elif self.__tokens[pos].get_value() == '(':
#                 parentheses_count += 1
#             elif self.__tokens[pos].get_value() == '(':
#                 parentheses_count -= 1
#                 if parentheses_count < 0:
#                     return -1
#             elif self.__tokens[pos].get_value() == ':' and \
#                     brace_count == 0 and parentheses_count == 0:
#                 return pos
#             pos += 1
#
#         return -1
#
#     def __insert_space_after_single_token(self, pos, rule=True):
#         if rule:
#             self.__tokens.insert(pos, Formatter.__space_token)
#
#     # def __insert_space_before_single_token(self, pos, rule):
#     #     if rule:
#     #         self.__tokens.insert(pos, Formatter.__space_token)
#
#     # BeforeLeftBrace
#     def __add_spaces_before_left_brace(self):
#         self.__i = 0
#         config = self.__config.get_spaces().get_before_left_brace()
#         while self.__i < len(self.__tokens) - 1:
#             token = self.__tokens[self.__i]
#             if token.get_token_type() == TokenType.KEYWORD:
#                 if token.get_value() in ('class', 'interface'):
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_class_left_brace())
#                 elif token.get_value() == 'if':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_if_left_brace())
#                 elif token.get_value() == 'else':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_else_left_brace())
#                 elif token.get_value() == 'for':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_for_left_brace())
#                 elif token.get_value() == 'while':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_while_left_brace())
#                 elif token.get_value() == 'do':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_do_left_brace())
#                 elif token.get_value() == 'switch':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_switch_left_brace())
#                 elif token.get_value() == 'try':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_try_left_brace())
#                 elif token.get_value() == 'catch':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_catch_left_brace())
#                 elif token.get_value() == 'finally':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_finally_left_brace())
#                 elif token.get_value() == 'synchronized':
#                     self.__insert_space_before_left_brace_after_current_pos(config.get_synchronized_left_brace())
#             elif token.get_token_type() == TokenType.ANNOTATION and config.get_annotation_array_initializer_left_brace():
#                 while self.__i < len(self.__tokens) \
#                         and self.__tokens[self.__i].get_token_type() == TokenType.WHITESPACE:
#                     self.__i += 1
#                 self.__i += 1
#                 if self.__tokens[self.__i].get_value() == '(' and self.__tokens[self.__i + 1].get_value() == '{':
#                     self.__insert_space_after_single_token(self.__i + 1,
#                                                            config.get_annotation_array_initializer_left_brace)
#                     self.__i += 1
#             elif self.__tokens[self.__i].get_value() == ']' \
#                     and self.__tokens[self.__i + 1].get_value() == '{' \
#                     and config.get_array_initializer_left_brace():
#                 self.__insert_space_after_single_token(self.__i + 1, config.get_array_initializer_left_brace)
#                 self.__i += 1
#             elif token.get_token_type() == TokenType.IDENTIFIER and config.get_method_left_brace():
#                 while self.__i < len(self.__tokens) \
#                         and self.__tokens[self.__i].get_token_type() == TokenType.WHITESPACE:
#                     self.__i += 1
#                 self.__i += 1
#                 if self.__tokens[self.__i].get_value() == '(':
#                     brace_count = 1
#                     self.__i += 1
#                     while brace_count != 0:
#                         if self.__tokens[self.__i].get_value() == '(':
#                             brace_count += 1
#                         elif self.__tokens[self.__i].get_value() == ')':
#                             brace_count -= 1
#                         self.__i += 1
#                 if self.__tokens[self.__i].get_value() == '{':
#                     self.__tokens.insert(self.__i, Formatter.__space_token)
#                     self.__i += 1
#             self.__i += 1
#
#     def __insert_space_before_left_brace_after_current_pos(self, rule):
#         if rule:
#             braces_end = False
#             while self.__i < len(self.__tokens):
#                 # skip (...) after if, for and others
#                 if self.__tokens[self.__i].get_value() == '(' and not braces_end:
#                     brace_count = 1
#                     self.__i += 1
#                     while brace_count != 0:
#                         if self.__tokens[self.__i].get_value() == '(':
#                             brace_count += 1
#                         elif self.__tokens[self.__i].get_value() == ')':
#                             brace_count -= 1
#                         self.__i += 1
#                     braces_end = True
#                 if self.__tokens[self.__i].get_value() == '{':
#                     self.__tokens.insert(self.__i, Formatter.__space_token)
#                     self.__i += 1
#                     return
#                 self.__i += 1
#             self.__i += 1
#
#     # Spaces -> TypeParameters
#     def __add_spaces_type_parameters_and_arguments(self):
#         self.__i = 0
#         config_parameters = self.__config.get_spaces().get_type_parameters()
#         config_arguments = self.__config.get_spaces().get_type_arguments()
#         brace_count = 0
#         angle_bracket_count = 0
#         while self.__i < len(self.__tokens):
#             token = self.__tokens[self.__i]
#             if token.get_value() == '{':
#                 brace_count += 1
#             elif token.get_value() == '}':
#                 brace_count -= 1
#             elif token.get_value() == '<':
#                 angle_bracket_count += 1
#                 if brace_count == 0 and config_parameters.get_before_opening_angle_bracket():
#                     self.__add_space_before_angle_bracket(config_parameters)
#                 elif brace_count >= 2:
#                     self.__add_space_before_angle_bracket(config_arguments)
#             elif token.get_value() == '>' and angle_bracket_count == 1 and brace_count >= 2:
#                 angle_bracket_count -= 1
#                 if not config_arguments.get_after_closing_angle_bracket() and self.__tokens[
#                     self.__i + 1].get_token_type() == TokenType.WHITESPACE:
#                     self.__i += 1
#                     self.__tokens.pop(self.__i)
#                 elif config_parameters.get_after_closing_angle_bracket() and self.__tokens[
#                     self.__i + 1].get_token_type() != TokenType.WHITESPACE:
#                     self.__i += 1
#                     self.__tokens.insert(self.__i, Formatter.__space_token)
#             elif token.get_value() == ',' and angle_bracket_count == 1 and brace_count >= 2 \
#                     and not config_arguments.get_after_comma():
#                 if not config_arguments.get_after_comma() and self.__tokens[
#                     self.__i + 1].get_token_type() == TokenType.WHITESPACE:
#                     self.__i += 1
#                     self.__tokens.pop(self.__i)
#                 elif config_parameters.get_after_comma() and self.__tokens[
#                     self.__i + 1].get_token_type() != TokenType.WHITESPACE:
#                     self.__i += 1
#                     self.__tokens.insert(self.__i, Formatter.__space_token)
#             elif token.get_value() == '&' and angle_bracket_count == 1 and brace_count == 0 \
#                     and not config_parameters.get_around_type_bounds():
#                 if not config_parameters.get_around_type_bounds() and self.__tokens[
#                     self.__i + 1].get_token_type() == TokenType.WHITESPACE:
#                     self.__tokens.pop(self.__i + 1)
#                 elif config_parameters.get_around_type_bounds() and self.__tokens[
#                     self.__i + 1].get_token_type() != TokenType.WHITESPACE:
#                     self.__i += 1
#                     self.__tokens.insert(self.__i, Formatter.__space_token)
#                 if not config_parameters.get_around_type_bounds() and self.__tokens[
#                     self.__i - 1].get_token_type() == TokenType.WHITESPACE:
#                     self.__tokens.pop(self.__i - 1)
#                 elif config_parameters.get_around_type_bounds() and self.__tokens[
#                     self.__i - 1].get_token_type() != TokenType.WHITESPACE:
#                     self.__tokens.insert(self.__i, Formatter.__space_token)
#                     self.__i += 1
#             elif token.get_value() in ('\n', ';', ')'):
#                 angle_bracket_count = 0
#             self.__i += 1
#
#     def __add_space_before_angle_bracket(self, config_parameters):
#         if not config_parameters.get_before_opening_angle_bracket() and self.__tokens[
#             self.__i - 1].get_token_type() == TokenType.WHITESPACE:
#             self.__tokens.pop(self.__i - 1)
#         elif config_parameters.get_before_opening_angle_bracket() and self.__tokens[
#             self.__i - 1].get_token_type() != TokenType.WHITESPACE:
#             self.__tokens.insert(self.__i, Formatter.__space_token)
#         self.__i += 1
#
#     # Spaces -> Other
#     def __add_other_spaces(self):
#         self.__i = 0
#         config = self.__config.get_spaces().get_other()
#         while self.__i < len(self.__tokens):
#             token = self.__tokens[self.__i]
#             if token.get_value() == ',':
#                 if config.get_before_comma():
#                     self.__tokens.insert(self.__i, Formatter.__space_token)
#                     self.__i += 1
#                 if config.get_after_comma():
#                     self.__i += 1
#                     self.__tokens.insert(self.__i, Formatter.__space_token)
#             elif token.get_value() == 'for':
#                 self.__add_spaces_in_for(self.__i, config.get_before_for_semicolon(), config.get_after_for_semicolon(),
#                                          config.get_before_colon_in_foreach())
#                 self.__i += 1
#             elif token.get_value() == 'enum' and self.__is_single_line_enum(self.__i):
#                 self.__add_spaces_in_enum(self.__i)
#                 self.__i += 1
#             elif token.get_value() == ')' and \
#                     (self.__tokens[self.__i + 1].get_value() == '('
#                      or self.__tokens[self.__i + 1].get_token_type() in
#                      (TokenType.KEYWORD, TokenType.IDENTIFIER, TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL)):
#                 self.__tokens.insert(self.__i + 1, Formatter.__space_token)
#                 self.__i += 1
#             self.__i += 1
#
#     def __is_single_line_enum(self, pos):
#         parenthesis_count = 0
#         parenthesis_found = False
#         while not (parenthesis_count == 0 and parenthesis_found):
#             if self.__tokens[pos].get_value() == '\n':
#                 return False
#             elif self.__tokens[pos].get_value() == '{':
#                 parenthesis_found = True
#                 parenthesis_count += 1
#             elif self.__tokens[pos].get_value() == '}':
#                 parenthesis_count -= 1
#                 if parenthesis_count == 0:
#                     return True
#             pos += 1
#         return True
#
#     def __add_spaces_in_for(self, pos, before_semicolon_rule, after_semicolon_rule, before_colon_rule):
#         if before_semicolon_rule or after_semicolon_rule or before_colon_rule:
#             brace_found = False
#             brace_count = 0
#             while not (brace_count == 0 and brace_found):
#                 if self.__tokens[pos].get_value() == '(':
#                     brace_found = True
#                     brace_count += 1
#                 elif self.__tokens[pos].get_value() == ')':
#                     brace_count -= 1
#                 elif self.__tokens[pos].get_value() == ';':
#                     if before_semicolon_rule:
#                         self.__tokens.insert(pos, Formatter.__space_token)
#                         pos += 1
#                     if after_semicolon_rule:
#                         self.__tokens.insert(pos + 1, Formatter.__space_token)
#                         pos += 1
#                 elif self.__tokens[pos].get_value() == ':':
#                     if before_colon_rule:
#                         self.__tokens.insert(pos + 1, Formatter.__space_token)
#                         self.__tokens.insert(pos, Formatter.__space_token)
#                         pos += 1
#                 pos += 1
#
#     def __add_spaces_in_enum(self, pos):
#         parentheses_found = False
#         parentheses_count = 0
#         while not (parentheses_count == 0 and parentheses_found):
#             if self.__tokens[pos].get_value() == '{':
#                 if parentheses_count == 0 and not parentheses_count:
#                     self.__tokens.insert(pos + 1, Formatter.__space_token)
#                     pos += 1
#                 parentheses_count += 1
#                 parentheses_found = True
#             elif self.__tokens[pos].get_value() == '}':
#                 parentheses_count -= 1
#                 if parentheses_count == 0 and parentheses_count:
#                     self.__tokens.insert(pos, Formatter.__space_token)
#                     pos += 1
#             pos += 1
#
#     def __add_blank_lines(self):
#         self.__keep_maximum_blank_lines()
#         self.___minimum_blank_lines()
#
#     # KeepMaximumBlankLines
#     def __keep_maximum_blank_lines(self):
#         self.__i = 0
#         config = self.__config.get_blank_lines().get_keep_maximum_blank_lines()
#         parentheses_count = 0
#         blank_lines_count = 0
#         while self.__i < len(self.__tokens):
#             token = self.__tokens[self.__i]
#             if token.get_value() == '\n':
#                 blank_lines_count += 1
#             elif blank_lines_count != 0:
#                 if token.get_value() == '}' and blank_lines_count >= config.get_before_right_parenthesis():
#                     self.__remove_new_lines_before_current_position(blank_lines_count - 1,
#                                                                     config.get_before_right_parenthesis())
#                     blank_lines_count = 0
#                 elif token.get_value() == 'package' and blank_lines_count >= config.get_between_header_and_package():
#                     self.__remove_new_lines_before_current_position(blank_lines_count,
#                                                                     config.get_between_header_and_package())
#                     blank_lines_count = 0
#                 elif parentheses_count == 1 and blank_lines_count >= config.get_in_declarations():
#                     self.__remove_new_lines_before_current_position(blank_lines_count - 1, config.get_in_declarations())
#                     blank_lines_count = 0
#                 elif parentheses_count > 1 and blank_lines_count >= config.get_in_code():
#                     self.__remove_new_lines_before_current_position(blank_lines_count - 1, config.get_in_code())
#                     blank_lines_count = 0
#
#             if token.get_value() == '{':
#                 parentheses_count += 1
#                 blank_lines_count = 0
#             elif token.get_value() == '}':
#                 parentheses_count -= 1
#                 blank_lines_count = 0
#             self.__i += 1
#
#     def __remove_new_lines_before_current_position(self, count, rule):
#         for i in range(count, rule, -1):
#             self.__i -= 1
#             self.__tokens.pop(self.__i)
#
#     def ___minimum_blank_lines(self):
#         self.__i = 0
#         config = self.__config.get_blank_lines().get_minimum_blank_lines()
#         parentheses_count = 0
#         blank_lines_count = 0
#
#         is_package = False
#         is_import = False
#
#         while self.__i < len(self.__tokens):
#             if self.__tokens[self.__i].get_value() == '\n':
#                 blank_lines_count += 1
#             if is_package and self.__tokens[self.__i - 1].get_value() == ';':
#                 is_package = False
#                 blank_lines_count = self.__count_empty_lines(self.__i + 1)
#                 if blank_lines_count <= config.get_after_package_statement():
#                     self.__add_new_lines_after_current_position(blank_lines_count,
#                                                                 config.get_after_package_statement())
#                 if blank_lines_count < config.get_after_package_statement():
#                     self.__i -= config.get_after_package_statement() - blank_lines_count
#                 blank_lines_count = 0
#             elif is_import and self.__tokens[self.__i + 1].get_value() != 'import' and self.__tokens[
#                 self.__i - 1].get_value() == ';':
#                 is_import = False
#                 blank_lines_count = self.__count_empty_lines(self.__i + 1)
#                 if blank_lines_count <= config.get_after_imports():
#                     self.__add_new_lines_after_current_position(blank_lines_count, config.get_after_imports())
#                 if blank_lines_count < config.get_after_imports():
#                     self.__i -= config.get_after_imports() - blank_lines_count
#                 blank_lines_count = 0
#             elif self.__tokens[self.__i].get_value() == 'package':
#                 if blank_lines_count <= config.get_before_package_statement():
#                     self.__add_new_lines_before_current_position(blank_lines_count,
#                                                                  config.get_before_package_statement())
#                 blank_lines_count = 0
#                 is_package = True
#                 self.__i = self.__find_token_by_value('\n', self.__i) - 1
#             elif self.__tokens[self.__i].get_value() == 'import' and not is_import:
#                 if not is_import:
#                     if blank_lines_count <= config.get_before_imports():
#                         self.__add_new_lines_before_current_position(blank_lines_count, config.get_before_imports())
#                     blank_lines_count = 0
#                 is_import = True
#                 self.__i = self.__find_token_by_value('\n', self.__i)
#                 while self.__tokens[self.__i + 1].get_value() == 'import':
#                     self.__i = self.__find_token_by_value('\n', self.__i + 1)
#                 self.__i -= 1
#             elif self.__tokens[self.__i].get_value() == 'class':
#                 pos = self.__i
#                 while self.__tokens[self.__i].get_value() != '\n':
#                     self.__i -= 1
#                 self.__add_new_lines_before_for_class(config.get_around_class(),
#                                                       config.get_after_class_header(),
#                                                       config.get_before_class_end(),
#                                                       config.get_around_field(),
#                                                       config.get_around_method())
#             elif self.__tokens[self.__i].get_value() == 'interface':
#                 while self.__tokens[self.__i].get_value() != '\n':
#                     self.__i -= 1
#                 self.__add_new_lines_before_for_class(config.get_around_class(),
#                                                       config.get_after_class_header(),
#                                                       config.get_before_class_end(),
#                                                       config.get_around_field_in_interface(),
#                                                       config.get_around_method_in_interface())
#             elif self.__tokens[self.__i].get_value() == '{':
#                 parentheses_count += 1
#             elif self.__tokens[self.__i].get_value() == '}':
#                 parentheses_count -= 1
#             self.__i += 1
#
#     def __count_empty_lines(self, pos):
#         count = 0
#         while self.__tokens[pos].get_value() == '\n':
#             count += 1
#             pos += 1
#         return count
#
#     def __add_new_lines_before_current_position(self, count, rule):
#         # while self.__tokens[self.__i].get_value() != '\n':
#         #     self.__i -= 1
#         if count < rule:
#             for i in range(count, rule, 1):
#                 self.__tokens.insert(self.__i, Formatter.__new_line_token)
#                 self.__i += 1
#         elif count > rule:
#             for i in range(count, rule, -1):
#                 self.__tokens.pop(self.__i)
#                 self.__i += 1
#
#     def __add_new_lines_after_current_position(self, count, rule):
#         # while self.__tokens[self.__i].get_value() != '\n':
#         #     self.__i += 1
#         if count < rule:
#             for i in range(count, rule, 1):
#                 self.__tokens.insert(self.__i + 1, Formatter.__new_line_token)
#                 self.__i += 1
#         if count > rule:
#             for i in range(count, rule, 1):
#                 self.__tokens.remove(self.__i + 1)
#                 self.__i += 1
#
#     def __add_new_lines_before_for_class(self, around_class, after_class_header, class_end_rule, around_field_rule,
#                                          around_method_rule):
#         brace_count = 0
#         brace_found = False
#
#         is_class_start = True
#
#         self.__i = self.__find_token_by_value('\n', self.__i) - 1
#
#         while not (brace_count == 0 and brace_found) and self.__i < len(self.__tokens):
#             if is_class_start:
#                 pos = self.__i
#                 self.__i = self.__find_token_by_value('\n', self.__i + 1)
#                 count = 0
#                 while self.__tokens[self.__i].get_value() == '\n':
#                     count += 1
#                     self.__i += 1
#                 self.__i -= 1
#                 if count <= after_class_header:
#                     self.__add_new_lines_after_current_position(count - 1, after_class_header)
#
#                 self.__i = pos + 1
#                 count = 0
#                 while self.__tokens[self.__i].get_value() != '\n':
#                     self.__i -= 1
#                 pos = self.__i
#                 while self.__tokens[pos].get_value() == '\n':
#                     count += 1
#                     pos -= 1
#                 if count <= around_class:
#                     self.__add_new_lines_before_current_position(count - 1, around_class)
#                 is_class_start = False
#                 while self.__tokens[self.__i].get_value() != '{':
#                     self.__i += 1
#
#             if self.__tokens[self.__i].get_value() == '{':
#                 brace_found = True
#                 brace_count += 1
#                 self.__i += 1
#             elif self.__tokens[self.__i].get_token_type() == TokenType.IDENTIFIER \
#                     and brace_count == 1:
#                 while self.__tokens[self.__i].get_value() != '\n':
#                     self.__i -= 1
#                 while self.__tokens[self.__i].get_token_type() == TokenType.WHITESPACE:
#                     self.__i += 1
#                 if brace_count == 1 and self.__is_method_declaration(self.__i):
#                     count = self.__count_empty_lines_before(self.__i)
#                     if count <= around_method_rule:
#                         self.__add_new_lines_before_current_position(count - 1, around_method_rule)
#
#                     method_brace_found = False
#                     method_brace_count = 0
#                     while not (
#                             (method_brace_found and method_brace_count == 0) or (
#                             not method_brace_found and self.__tokens[self.__i].get_value() == ';')):
#                         if self.__tokens[self.__i].get_value() == '{':
#                             method_brace_found = True
#                             method_brace_count += 1
#                         elif self.__tokens[self.__i].get_value() == '}':
#                             method_brace_count -= 1
#
#                         self.__i += 1
#                     self.__i = self.__find_token_by_value('\n', self.__i)
#                     pos = self.__i
#                     count = 0
#                     while self.__tokens[pos].get_value() == '\n':
#                         count += 1
#                         pos += 1
#                     if count <= around_method_rule:
#                         self.__add_new_lines_before_current_position(count - 1, around_method_rule)
#                 else:
#                     count = self.__count_empty_lines_before(self.__i)
#                     if count <= around_field_rule:
#                         self.__add_new_lines_before_current_position(count - 1, around_field_rule)
#
#                     self.__i = self.__find_token_by_value('\n', self.__i)
#                     pos = self.__i
#                     count = 0
#                     while self.__tokens[pos].get_value() == '\n':
#                         count += 1
#                         pos += 1
#                     if count <= around_field_rule:
#                         self.__add_new_lines_after_current_position(count - 1, around_field_rule)
#             elif self.__tokens[self.__i].get_value() == '}' and brace_found:
#                 brace_count -= 1
#                 if brace_count == 0:
#                     self.__i -= 1
#                     pos = self.__i
#                     count = 0
#                     while self.__tokens[pos].get_value() == '\n':
#                         count += 1
#                         pos -= 1
#                     if count <= class_end_rule:
#                         self.__add_new_lines_before_current_position(count - 1, class_end_rule)
#             self.__i += 1
#
#     def __count_empty_lines_before(self, pos):
#         count = 0
#         while self.__tokens[pos].get_value() != '\n':
#             pos -= 1
#         while self.__tokens[pos].get_value() == '\n':
#             count += 1
#             pos -= 1
#         return count
#
#