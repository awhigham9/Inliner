import json
from tokens import *
from util import *
import re

class Tokenizer:

    def __init__(self, config_path):
        self.config_path = config_path
        with open(self.config_path) as f:
            config_data = json.load(f)
            self.operators = config_data["operators"]
            self.keywords = config_data["keywords"]
            # Dictionary storing special 2 character tokens in a mapping such that:
            # <key> = second character
            # <value> = list of all possbile first characters
            # Ex: "~^" is represented as '^' -> ['~']
            # while "~&" and "&&" are "&" -> ['~', '&']
            self.binary_token_pairs = config_data["binary_token_pairs"]
            self.ternary_token_pairs = config_data["ternary_token_pairs"]
            self.comment_symbols = config_data["comment_bounds"]
        
    def tokenize(self, line):
        ''' Takes a string and tokenizes it according to verilog syntax '''
        buffer = ""
        tokens = []
        in_string = False
        in_comment = False
        in_block_comment = False
        for c in line:
            # Comment processing
            if in_comment:
                if c == "\n":
                    in_comment = False
                    t = Token(buffer, TokenType.COMMENT)
                    tokens.append(t)
                    tokens.append( Token(c, TokenType.WHTSPC) )
                    buffer = ""
                else:
                    buffer += c
            elif buffer == "//":
                in_comment = True
                buffer += c
            elif in_block_comment:
                if buffer[-2:] == "*/":
                    in_block_comment = False
                    t = Token(buffer, TokenType.COMMENT)
                    tokens.append(t)
                    buffer = c
                else:
                    buffer += c
            elif buffer == "/*":
                in_block_comment = True
                buffer += c
            elif c == "\"":
                if buffer and buffer[-1] == "\\" and in_string:
                    # The escape character '\"'
                    buffer += c
                else:
                    in_string = not in_string
                    if in_string:
                        t = Token(buffer, self.select_type(buffer))
                        tokens.append(t)
                        buffer = c
                    else:
                        buffer += c
                        t = Token(buffer,TokenType.STRING)
                        tokens.append(t)
                        buffer = ""
            elif in_string:
                buffer += c
            elif c.isspace():
                t = Token(buffer, self.select_type(buffer))
                tokens = self.append_non_empty(tokens,t)
                tokens.append( Token(c, TokenType.WHTSPC) )
                buffer = ""
            elif c in self.operators:
                # This catches operators as well as special comment characters like / and *
                if c in self.ternary_token_pairs:
                    # c is an operators which can appear in groups of 3
                    if buffer in self.ternary_token_pairs[c]:
                        # The token preceding c combines with it to make a new operator (ex: "<<<" =  "<" + "<<")
                        buffer += c
                    else:
                        # The token before c is not an operator we can combine with it 
                        t = Token(buffer, self.select_type(buffer))
                        tokens = self.append_non_empty(tokens,t)
                        buffer = c
                elif c in self.binary_token_pairs:
                    # c is an operator which can appear by itself or with others
                    if buffer in self.binary_token_pairs[c]:
                        # The token preceding c combines with it to make a new operator (ex: "!=" =  "!" + "=")
                        buffer += c
                    else:
                        # The token before c is not an operator we can combine with it 
                        t = Token(buffer, self.select_type(buffer))
                        tokens = self.append_non_empty(tokens,t)
                        buffer = c
                else:
                    t = Token(buffer, self.select_type(buffer))
                    tokens = self.append_non_empty(tokens,t)
                    buffer = c
            elif buffer in self.operators:
                t = Token(buffer, TokenType.OPERATOR)
                tokens = self.append_non_empty(tokens,t)
                buffer = c
            else:
                buffer += c
        t = Token(buffer, self.select_type(buffer))
        tokens = self.append_non_empty(tokens,t)
        return tokens

    def append_non_empty(self, tokens, token):
        ''' Appends the string token only if it is not empty 
        Params: tokens (List), token (Token)
        Returns: List 
        '''
        if(token.content):
            tokens.append(token)
        return tokens

    def select_type(self, content):
        ''' Accepts a token of content (str), and returns what type of token it is 
            Params: content (str)
            Returns: TokenType
        '''
        if self.is_keyword(content):
            return TokenType.KEYWORD
        elif self.is_operator(content):
            return TokenType.OPERATOR
        elif self.is_number(content):
            return TokenType.NUMBER
        elif self.is_comment(content):
            return TokenType.COMMENT
        elif self.is_compiler_directive(content):
            return TokenType.COMP_DIRECTIVE
        elif self.is_system_task(content):
            return TokenType.SYS_TASK
        elif self.is_string(content):
            return TokenType.STRING
        elif str.isspace(content):
            return TokenType.WHTSPC
        else:
            return TokenType.IDENTIFIER

    def is_string(self,token):
        str_re = "\".*\""
        return bool(re.fullmatch(str_re,token))

    def is_number(self,token):
        # Int check
        try:
            int(token)
            return True
        except:
            pass
        # Float check
        try:
            float(token)
            return True
        except:
            pass
        # bit/octal/hex string check
        binary_re = "[\d]+\'[bB][10_\?XZ]+"
        octal_re = "[\d]+\'[oO][(1-7)_\?XZ]+"
        hex_re = "[\d]+\'[hH][\d(A-F)(a-f)_\?XZ]+"
        decimal_re = "[\d]+\'[dD][\d_XZ\?]+"
        unknown_re = "X|x"
        high_imped_re = "Z|z|\\?"
        return bool(re.fullmatch(binary_re,token)) or bool(re.fullmatch(octal_re,token)) or bool(re.fullmatch(hex_re,token)) \
            or bool(re.fullmatch(decimal_re,token)) or bool(re.fullmatch(unknown_re,token)) or bool(re.fullmatch(high_imped_re,token))

    def is_comment(self,s):
        comment_re = "\/\/.*"
        block_comment_re = "\/\*[\S\s]*\*\/" #TODO: test this
        return bool(re.fullmatch(comment_re,s)) or bool(re.fullmatch(block_comment_re,s))

    def is_keyword(self,s):
        return s in self.keywords

    def is_system_task(self,s):
        sys_task_re = "\$.*"
        return bool(re.fullmatch(sys_task_re,s))

    def is_compiler_directive(self,s):
        comp_dir_re = "`.*"
        return bool(re.fullmatch(comp_dir_re,s))

    def is_operator(self,s):
        return s in self.operators