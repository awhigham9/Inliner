import json
from tokenizer import Tokenizer
from module import Module
import re
from util import *
from tokens import TokenType, Token

class Inliner:

    def __init__(self, config_path, input_path):
        self.config_path = config_path
        self.tokenizer = Tokenizer(config_path)
        self._token_gen = self._token_generator(input_path)
        with open(self.config_path) as f:
            config_data = json.load(f)
            self.operators = config_data["operators"]
            self.keywords = config_data["keywords"]
        self.modules = {} # Dict mapping module names in file to module names
        self.input_path = input_path
        self.reference_tree = {}

    def _token_generator(self, path_in):
        with open(path_in,'r') as f:
            text = f.read()
            tokens = self.tokenizer.tokenize(text)
            token, *tokens = tokens
            while(tokens):
                yield token
                token, *tokens = tokens
            yield token # Yield the last element 

    def _get_token(self):
        return next(self._token_gen, None)

    def inline(self, path_out):
        ''' The inlining function exposed as part of the API '''
        pass #TODO
    
    def _index(self):
        token = self._get_token()
        while(token):
            if token.content == "module":
                self._process_module(token)
            token = self._get_token()

    def _process_module(self, token):
        balance = 1
        module_content = [token] # Store the first token in the list
        token = self._get_token()
        # Capture the whole module text
        while(balance != 0 and token):
            if token.content == "module":
                balance += 1
            elif token.content == "endmodule":
                balance -= 1
            module_content.append(token)
            token = self._get_token()
        if not token and balance != 0:
            raise ValueError(f"Incomplete module input into function Inliner._process_module\nCheck input file {self.input_path} for proper Verilog Syntax")
        # Process the module header
        module_header = []
        module_body = module_content
        for token in module_body:
            module_header.append(token)
            module_body = module_body[1:]
            if token.content == ";":
                break   
        # Get the module name
        i = 0
        while(module_header[i].token_type != TokenType.IDENTIFIER):
            i += 1
        name = module_header[i].content
        # Process the port list from the header
        ports = []
        raw_module_header = list(map(lambda x: x.to_string(), module_header)) # Make a string version to call balanced bounds
        open_paren_idx = raw_module_header.index("(")
        close_paren_idx = balanced_bounds(raw_module_header,"(",")",open_paren_idx)
        port_list = module_header[open_paren_idx:close_paren_idx+1]
        ports = []
        for token in port_list:
            if token.token_type == TokenType.IDENTIFIER:
                ports.append(token.content)
        #TODO: Identify the parameters in the body
        parameters = []
        hit_parameter = False
        for token in module_body:
            if token.token_type == TokenType.KEYWORD and token.content == "parameter":
                hit_parameter = True
            if hit_parameter:
                if token.token_type == TokenType.IDENTIFIER:
                    parameters.append(token.content)
                    hit_parameter = False
        # Make the module object
        mod = Module(name, module_body, module_header, ports, parameters)
        self.modules[name] = mod

    def _generate_reference_tree(self):
        ''' Algorithm to generate the reference tree which
            stores which modules reference which, in a tree data structure.
            This can then be used to efficiently inline the files without error.
            Pre-conditions: The modules have already been indexed with _index()
        '''
        for name in self.modules:
            self.reference_tree[name] = set()
        for name, mod in self.modules.items():
            for token in mod.body:
                if token.token_type == TokenType.IDENTIFIER and token.content in modules:
                    # This module contains a reference to another module 
                    self.reference_tree[name].add(token.content)

    def _inline(self):
        ''' Algorithm to inline all modules into one single module for output
            Pre-conditions: _index() and _generate_reference_tree() have already been called
        '''
        # Phase 1: Establish the inlining order based on the reference tree
        child_nodes = set()
        for name, children in self.reference_tree.items():
            for elem in children:
                child_nodes.add(elem)
        # STOPPED HERE
        
                    

    def _process_module_instantiation(self,token):
        # Get text of whole statement
        tokens = []
        while(token != ";"):
            instantiation_text.append(token)
            token = self._get_token()
        module_name = instantiation_text[0]
        parameter_values = []
        # Move to the instance name and record parameter instantiations along the way
        i = 0
        while(tokens[i].isspace() or tokens[i] == "#" or self.isNumber(token[i]) or
            tokens[i] == "(" or tokens[i] == ")"):
            if(self.isNumber(tokens[i])):
                parameter_values.append(number)
            i += 1
        # The current token should now be the name of the instance
        instance_name = token[i]
        # Now parse the port assignments
        port_list = []
        open_paren_idx = module_header.index("(",i)
        close_paren_idx = balanced_bounds(module_header,"(",")",open_paren_idx)
        port_list = module_header[open_paren_idx:close_paren_idx+1]
        port_list = remove_comments(port_list) # Remove comments
        port_list = [tok for tok in port_list if not tok.isspace()] # Remove spaces
        port_assignments_text = []
        pass
        #TODO     

    def append_non_empty(self, tokens, token):
        ''' Appends the string token only if it is not empty 
        Params: List (tokens), str (token)
        Returns: List 
        '''
        if(token):
            tokens.append(token)
        return tokens

    def _output_module(self,name,prefix):
        ''' Returns module body with all idenitifiers prefixed by prefix '''
        if name not in self.modules:
            raise ValueError(f"Module by name {name} has not been processed by this Inliner instance")
        else:
            mod = self.modules[name]
            comment = False
            block_comment = False
            new_body = []
            for token in mod.body:
                if comment:
                    if token == "\n":
                        comment = False
                    new_body.append(token)
                elif block_comment:
                    if token == "*/":
                        block_comment = False
                    new_body.append(token)
                elif token == "//":
                    comment = True
                    new_body.append(token)
                elif token == "/*":
                    block_comment = True
                    new_body.append(token)
                elif token == "input":
                    #Replace inputs with wires
                    new_body.append("wire")
                elif token.startswith("$"):
                    # These are system tasks, not identifiers
                    new_body.append(token)
                elif token.startswith("`"):
                    # These are special macros or preprocessor directives
                    new_body.append(token)
                elif self.isNumber(token) or token.isspace() or token in self.operators \
                or token in self.keywords or token in self.separators or self.is_string(token):
                    new_body.append(token) 
                else:
                    token = prefix + token
                    new_body.append(token)
            return "".join(new_body)


def balanced_bounds(tokens, open_token, close_token, start=0):
    ''' An algorithm which given a list of strings = [s0, s1, ... , sn] 
    and an open and closing tokens t0 and t1, will start at index 'start' 
    and return the index at which an equal number of t0 and t1 have occurred '''
    if not start < len(tokens):
        raise ValueError("Starting index too high")
    if not tokens:
        return 0
    i = start
    # Go to the first open token
    while(tokens[i] != open_token):
        i += 1
        if not i < len(tokens):
            raise ValueError("Open token does not appear at or after start index")
    count = 1
    i += 1
    while(count != 0 and i < len(tokens)):
        if(tokens[i] == open_token):
            count += 1
        elif(tokens[i] == close_token):
            count -= 1
        i += 1
    if not i < len(tokens) and count != 0:
        raise ValueError("Input tokens do not contain balanced open_token and closing_token groupings")
    else:
        return i - 1

def remove_comments(tokens, start=0, end=None):
    ''' Given a list of parsed tokens, remove all comments from this list
    in the range [start,end). If end is not specified, go to the end of the list.
    Params: tokens (List of str), start=0 (int), end=-1 (int)
    Returns: List of str, with comments removed '''
    comment = False
    block_comment = False
    out = []
    for t in tokens:
        if comment:
            if t == "\n":
                out.append(t)
                comment = False
        elif block_comment:
            if t == "*/":
                comment = False
        elif t == "//":
            comment = True
        elif t == "/*":
            block_comment = True
        else:
            out.append(t)
    return out



        
        