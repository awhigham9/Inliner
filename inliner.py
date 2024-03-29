import json
from tokenizer import Tokenizer
from module import Module
import re
import regexes
from tokens import TokenType, Token
from generator_helper import GeneratorHelper
from copy import deepcopy

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
        self._inlined_modules = {} # Dict mapping module names to their inlined versions; will be empty until _inline() is called
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

    def inline(self,message=True):
        ''' The inlining function exposed as part of the API '''
        self._index()
        if(message):
            print("Indexing complete . . .")
        self._generate_reference_tree()
        if(message):
            print("Reference tree generation complete . . .")
        self._inline()
        if(message):
            print("Inlining complete . . .")
    
    def _index(self):
        ''' Reads the input file '''
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
        raw_module_header = list(map(lambda x: x.to_string(), module_header)) # Make a string version to call balanced bounds
        # Process the port list from the header
        ports = []
        open_paren_idx = raw_module_header.index("(")
        close_paren_idx = balanced_bounds(raw_module_header,"(",")",open_paren_idx)
        port_list = module_header[open_paren_idx:close_paren_idx+1]
        ports = []
        for token in port_list:
            if token.token_type == TokenType.IDENTIFIER:
                ports.append(token.content)
        # Process the parameter list in the module header
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
            stores which modules reference which other modules, in a tree implemented
            as a dicitonary mapping names (str) to sets of names (set, str).
            This can then be used to efficiently inline the files without error.
            Pre-conditions: The modules have already been indexed with _index()
        '''
        for name in self.modules:
            self.reference_tree[name] = set()
        for name, mod in self.modules.items():
            for token in mod.body:
                if token.token_type == TokenType.IDENTIFIER and token.content in self.modules:
                    # This module contains a reference to another module 
                    self.reference_tree[name].add(token.content)

    def _inline(self):
        ''' Algorithm to inline all modules into one single module for output
            Pre-conditions: _index() and _generate_reference_tree() have already been called
        '''
        # Phase 1: Establish the inlining order based on the reference tree
        order = self._get_inline_order(self.reference_tree)       
        for name in order:
            if not self.reference_tree[name]:
                # This module is a leaf; it references no other modules
                self._inlined_modules[name] = self.modules[name]
            else:
                # Inline this module
                self._inlined_modules[name] = self._get_inlined_module(name)

    def _get_inlined_module(self, name):
        ''' Function which given a name appearing in the modules dictionary creates an inlined version of it
        Params: name (str) which appears in self.modules
        Returns: Inlined module object (module)
        Pre-conditions:  _inline() is calling this function in the correct order, as the modules referenced by 
                        'name' must be inlined before 'name' 
        '''
        top_body = self.modules[name].body
        new_body = []
        gen = GeneratorHelper(top_body)
        token = gen.get_element()
        while(token):
            if token.token_type == TokenType.IDENTIFIER and token.content in self._inlined_modules:
                try:
                    inlined_portion = self._process_module_instantiation(gen,token)
                    new_body.extend(inlined_portion)
                except ValueError as e:
                    raise ValueError(f"Error encountered while attempting to inline module {name}:\n{str(e)}")
            else:
                new_body.append(token)
            token = gen.get_element()
        return Module(name, new_body, self.modules[name].header, self.modules[name].ports, self.modules[name].parameters)
                
    def _process_module_instantiation(self, gen, curr_token):
        ''' Method to extract a module instantiation from a generator input 
        stream gen (GeneratorHelper), process it, and then write it to the output (List of Token) 
        '''
        balance = 1
        instance_type = curr_token
        statement = [curr_token]
        token = gen.get_element()
        while(token and token.content != ";"):
            statement.append(token)
            token = gen.get_element()
        if not token:
            raise ValueError(f"Incomplete module instantiation detected in input to Inliner in function Inliner._process_module_instantiation\nCheck input file {self.input_path} for proper Verilog Syntax")
        statement.append(token) # Add on the ending semicolon
        try:
            inlined_portion = self._instantation_to_inlined_body(statement)
        except ValueError:
            raise # Just hand it up to the caller function
        else:
            return inlined_portion

    def _instantation_to_inlined_body(self, instantiation):
        ''' Accepts text of a  module instantiation (List of Tokens) 
            in verilog syntax. Returns the body of the module instantiated with
            the correct I/O assignments '''
            
        raw_text = list(map( lambda x : x.to_string(), instantiation))

        # Get the names
        module_name = instantiation[0].content
        i = 1

        # Get the parameter assignment list, if it exists
        param_list = []
        if "#" in raw_text:
            idx = raw_text.index("#")
            param_list_start = raw_text.index("(",idx)
            param_list_end = balanced_bounds(raw_text, "(", ")", param_list_start)
            param_list = instantiation[param_list_start + 1 : param_list_end]
            param_list = [tok for tok in param_list if tok.token_type != TokenType.COMMENT and tok.token_type != TokenType.WHTSPC]
            i = param_list_end + 1

        while(instantiation[i].token_type != TokenType.IDENTIFIER):
            i += 1
        instance_name = instantiation[i].content


        # Get the port assignment list
        if param_list:
            port_list_start = raw_text.index("(", i + 1)
        else:
            port_list_start = raw_text.index("(")
        port_list_end = balanced_bounds(raw_text, "(", ")", port_list_start)
        port_list = instantiation[port_list_start + 1 : port_list_end]
        port_list = [tok for tok in port_list if tok.token_type != TokenType.COMMENT and tok.token_type != TokenType.WHTSPC]

        # Identify the type of port list (positional or named) and param list (positional or named)
        port_list_text = "".join([x.to_string() for x in port_list])
        param_list_text = "".join([x.to_string() for x in param_list])
        # A regex for an identifier or an indexed identifier
        
        # Regexes to match the naming list and positional list convention of port/parameter assignment
        param_positional = regexes.positional_port_list.fullmatch(param_list_text)
        param_naming = regexes.named_port_list.fullmatch(param_list_text)
        port_positional = regexes.positional_port_list.fullmatch(port_list_text)
        port_naming = regexes.named_port_list.fullmatch(port_list_text)

        # Parse the param and port assignment lists now that we know their format
        param_assignments = {}
        if param_list:
            if param_naming:
                param_assignments = self._parse_named_param_list(param_list, module_name)
            elif param_positional:
                param_assignments = self._parse_positional_param_list(param_list, module_name)
            else:
                raise ValueError(f"Invalid parameter list syntax detected in Inliner._instantiation_to_inlined_body:" /
            "\n" + "".join(raw_text) + "\n" + f"Check file {self.input_path} for proper verilog syntax.")
        port_assignments = {}
        if port_naming:
            port_assignments = self._parse_named_port_list(port_list, module_name)
        elif port_positional:
            port_assignments = self._parse_positional_port_list(port_list, module_name)

        # Resolve naming collisions by prefixing variable names
        old_body = deepcopy(self._inlined_modules[module_name].body)
        for token in old_body:
            if token.token_type == TokenType.IDENTIFIER:
                token.content = self._prefix_name(instance_name,token.content)
        for key in param_assignments.copy():
            new_key = self._prefix_name(instance_name,key)
            param_assignments[new_key] = param_assignments[key]
            del param_assignments[key]
        for key in port_assignments.copy():
            new_key = self._prefix_name(instance_name,key)
            port_assignments[new_key] = port_assignments[key]
            del port_assignments[key]

        # Modify the body of the module by adding assignments, and renaming inputs and outputs to wires or regs.
        inlined_body = []
        gen = GeneratorHelper(old_body)
        token = gen.get_element()
        buffer = []
        output_regs = []
        output_wires = []
        tkzr = Tokenizer(self.config_path)
        # Change the input and output declarations
        while( token.content != 'endmodule'):
            buffer.append(token)
            # End of a statement, process it
            if buffer[-1].content == ";":
                # stmt is buffer without comments
                stmt = [x for x in buffer if x.token_type != TokenType.COMMENT]
                stmt = list(map(lambda x : x.to_string(), stmt))
                modified_stmt = deepcopy(stmt)
                if "input" in stmt:
                    i = stmt.index("input")
                    modified_stmt[i] = "wire"
                    ports = [key for key in port_assignments if key in stmt] # Input ports mentioned in the statement
                    for port in ports:
                        if port_assignments[port]:
                            # If the port wasn't left empty
                            modified_stmt.append("\n")
                            modified_stmt.append(f"assign {port} = {port_assignments[port]};")
                elif "output" in stmt:
                    start = 0
                    end = 0
                    if "[" in stmt:
                        # Remove the size field
                        size_field = True
                        start = stmt.index("[")
                        end = balanced_bounds(stmt,"[","]",start)
                    text = "".join(stmt)
                    output_reg_re = '[\\s\n]*output[\\s\n]+reg'
                    hasOutputReg = re.match(output_reg_re,text)
                    if hasOutputReg:
                        modified_stmt.remove("output")
                        for t in buffer[end:]:
                            if t.token_type == TokenType.IDENTIFIER:
                                output_regs.append(t)
                    else:
                        i = stmt.index("output")
                        modified_stmt[i] = "wire"
                        for t in buffer[end:]:
                            if t.token_type == TokenType.IDENTIFIER:
                                output_wires.append(t)
                elif "inout" in stmt:
                    # TODO implement functionality for inout ports
                    pass
                elif "parameter" in stmt:
                    # TODO: implement detection multiple assignments of multiple params in one line
                    # Example: 'parameter P1, P2, P3 = <value>'
                    param_assign_regex = ".*[\s\n]*parameter[\s\n]+([\w\$]+)[\s\n]*=[\s\n]*(.*?)[\s\n]*;"
                    m = re.match(param_assign_regex, "".join(stmt))
                    if m:
                        if m.group(1) in param_assignments:
                            val_idx = modified_stmt.index(m.group(2))
                            modified_stmt[val_idx] = param_assignments[m.group(1)]
                modified_stmt = tkzr.tokenize( "".join(modified_stmt) )
                i = 0
                j = 0
                # Merge the comments back into the output added to the inlined body
                while(i < len(modified_stmt) and j < len(buffer)): 
                    if buffer[j].token_type == TokenType.COMMENT:
                        inlined_body.append(buffer[j])
                        j += 1
                    else:
                        inlined_body.append(modified_stmt[i])
                        i += 1
                        j += 1
                if len(buffer) < len(modified_stmt):
                    while(i < len(modified_stmt)):
                        inlined_body.append(modified_stmt[i])
                        i += 1
                elif len(modified_stmt) < len(buffer):
                    while(j < len(buffer) - 1): # Minus 1 to avoid the final semicolon
                        inlined_body.append(buffer[j])
                        j += 1
                buffer = [] # Empty the buffer
            token = gen.get_element()
        inlined_body.extend(buffer)
        # Add on the output assignments at the end of the module body
        # TODO: There will be errors if the connection to the output is a reg because these are continuous assignments
        # How do we solve this problem?
        for port in output_regs:
            if port_assignments[port.content]: # Don't add if the port was left disconnected
                s = f"\nassign {port_assignments[port.content]} = {port.content};"
                inlined_body.extend( tkzr.tokenize(s) )
        for port in output_wires:
            if port_assignments[port.content]: # Don't add if the port was left disconnected
                s = f"\nassign {port_assignments[port.content]} = {port.content};"
                inlined_body.extend( tkzr.tokenize(s) )
        inlined_body.append( Token("\n", TokenType.WHTSPC) )
        return inlined_body
        

    def _prefix_name(self, prefix, name):
        ''' Helper function to standardize the way variables are prefixed 
            when they are being inlined into a module that references them
            to avoid naming collisions.
            Params: Prefix (str), name (str)
            Returns: new variable name (str)
        '''
        return f"_{prefix}_{name}"

    def _parse_positional_param_list(self, param_list, module_name):
        ''' Function to parse a positional parameter list (List of tokens) in 
            verilog syntax for a particular module, and return a dictionary
            mapping parameter names (str) to strings (str), whether they 
            represent a number, identifier, or otherwise.
        '''
        # TODO: Add error checking
        # Remove spaces and commas, leaving only the parameter list arguments
        param_list = [x for x in param_list if x.token_type != TokenType.WHTSPC]
        param_list = [x for x in param_list if x.content != ","]
        module_params = self.modules[module_name].ports
        assignments = {}
        min_size = min( len(module_params), len(param_list) )
        for i in range( min_size ):
            assignments[ module_params[i] ] = param_list[i].to_string()
        return assignments  

    def _parse_named_param_list(self, param_list, module_name):
        ''' Function to parse a named parameter list (List of tokens) in 
            verilog syntax for a particular module, and return a dictionary
            mapping parameter names (str) to strings (str), whether they 
            represent a number, identifier, or otherwise.
        '''
        # TODO: Add error checking
        assignments = {}
        regex = f"\.({regexes.identifier})\((({regexes.identifier})|({regexes.number}))\)" # Consider changing group 2 to any character
        text = "".join(list(map(lambda x : x.to_string(), param_list)))
        period = -1
        while("." in text[period+1:]):
            period = text.index(".",period+1)
            text = text[period:] # Test this
            m = re.match(regex, text)
            assignments[m.group(1)] = m.group(2)
        return assignments

    def _parse_named_port_list(self, port_list, module_name):
        ''' Function to parse a named port assignment list (List of tokens) in 
            verilog syntax for a particular module, and return a dictionary
            mapping port names (str) to the connected reg or wire names (str)
        '''
        # TODO: Add error checking
        assignments = {}
        regex = f"\.({regexes.s_identifier})\((.*?)\)" 
        text = "".join(list(map(lambda x : x.to_string(), port_list)))
        period = text.index(".")
        text = text[period:]
        while("." in text[1:]):
            m = re.match(regex, text)
            assignments[m.group(1)] = m.group(2)
            period = text.index(".",1)
            text = text[period:] # Test this
        m = re.match(regex, text)
        assignments[m.group(1)] = m.group(2) # Add the last one
        return assignments        

    def _parse_positional_port_list(self, port_list, module_name):
        port_list = [x for x in port_list if x.token_type != TokenType.WHTSPC]
        port_list = [x for x in port_list if x.content != ","]
        ports = self.modules[module_name].ports
        assignments = {}
        min_size = min( len(ports), len(port_list) )
        for i in range( min_size ):
            assignments[ ports[i] ] = port_list[i].to_string()
        return assignments  

    def _get_inline_order(self, ref_tree):
        rt = deepcopy(ref_tree)
        return self._get_inline_order_helper(rt,[])
    
    def _get_inline_order_helper(self, ref_tree, order):
        ''' Algorithm to identify the order in which modules will be inlined '''
        if not ref_tree:
            # Base case, the tree has been completely trimmed and we have the ordering
            return order
        else:
            # Identify leaf nodes
            leaves = set()
            for name, children in ref_tree.items():
                if not children:
                    leaves.add(name)
            if not leaves:
                # There are no leaf nodes, implying a cycle must exist
                # TODO: Throw an error when this occurs
                pass
            else:
                order.extend( list(leaves) ) # Put the current leaves on the back of the order
                # Trim the tree
                for name, children in ref_tree.items():
                    for child in children.copy():
                        if child in leaves:
                            children.remove(child)
                for name in leaves:
                    ref_tree.pop(name, None)
                # Now that the tree is trimmed, execute a recursive call on the trimmed tree
                return self._get_inline_order_helper(ref_tree, order)      


def balanced_bounds(strings, open_token, close_token, start=0):
    ''' An algorithm which given a list of strings = [s0, s1, ... , sn] 
    and an open and closing strings t0 and t1, will start at index 'start' 
    and return the index at which an equal number of t0 and t1 have occurred '''
    if not start < len(strings):
        raise ValueError("Starting index too high")
    if not strings:
        return 0
    i = start
    # Go to the first open token
    while(strings[i] != open_token):
        i += 1
        if not i < len(strings):
            raise ValueError("Open token does not appear at or after start index")
    count = 1
    i += 1
    while(count != 0 and i < len(strings)):
        if(strings[i] == open_token):
            count += 1
        elif(strings[i] == close_token):
            count -= 1
        i += 1
    if not i < len(strings) and count != 0:
        raise ValueError("Input strings do not contain balanced open_token and closing_token groupings")
    else:
        return i - 1



        
        