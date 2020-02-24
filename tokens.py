import enum

class TokenType(enum.Enum):
    WHTSPC = 0
    OPERATOR = 1
    KEYWORD = 2
    IDENTIFIER = 3
    COMMENT = 4
    NUMBER = 5
    SYS_TASK = 6
    COMP_DIRECTIVE = 7
    STRING = 8

class Token:
    ''' The wrapper class for raw verilog tokens '''

    def __init__(self,content,token_type):
        ''' The constructor
            Params:
                content (str) : the character content of the token
                token_type (TokenType) : one of the values on the enum token_type 
        '''
        self.content = content
        self.token_type = token_type

    def info(self):
        return f"type: <{self.token_type}>, content: <{self.content}>"

    def to_string(self):
        return self.content
