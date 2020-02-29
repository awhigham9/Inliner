import unittest
from inline import *
import tokenizer

class TestInliner(unittest.TestCase):

    def setUp(self,config_path,input_path):
        self.input = input_path
        self.config = config_path
        self.inliner = Inliner(config_path,input_path)

    def test_preservation_after_indexing(self, outpath):
        self.inliner._index()
        with open(f"unit_testing_output/{outpath}", 'w') as f:
            f.write(f"Preservation After Indexing Test of Inliner Class\n\
                    Input path: \"{self.input}\" \n \
                    Config path: \"{self.config}\" \n")
        for k in self.inliner.modules:
            h = "".join( list( map(lambda x : x.to_string(), self.inliner.modules[k].header)))
            b = "".join( list( map(lambda x : x.to_string(), self.inliner.modules[k].body)))
            with open(f"unit_testing_output/{outpath}", 'a') as f:
                f.write(h)
                f.write(b)
                f.write('\n')

    def test_ports(self, outpath):
        self.inliner._index()
        with open(f"unit_testing_output/{outpath}", 'w') as f:
            f.write(f"Port Recording Test of Inliner Class Method _index() \nInput path: \"{self.input}\" \nConfig path: \"{self.config}\" \n")
        for k in self.inliner.modules:
            with open(f"unit_testing_output/{outpath}", 'a') as f:
                f.write(f"Module \"{k}\" Ports:\n")
                for p in self.inliner.modules[k].ports:
                    f.write(p)
                    f.write('\n')

    def test_named_param_list_parser(self, named_param_list_str, module_name):
        self.inliner._index()
        t = Tokenizer(self.config)
        params = t.tokenize(named_param_list_str)
        try:
            out = self.inliner._parse_named_param_list(params,module_name)
            print("No exceptions thrown")
            print( "Parameter : Value")
            for k, v in out.items():
                print(f"{k} : {v}")
        except ValueError as e:
            print("Test of function Inliner._parse_named_param_list failed due to the following error, possibly expected")
            raise
        except Exception as e:
            print("Test of function Inliner._parse_named_param_list failed due to unexpected error.")
            raise

    def test_positional_param_list_parser(self, pos_param_list_str, module_name):
        self.inliner._index()
        t = Tokenizer(self.config)
        params = t.tokenize(pos_param_list_str)   
        try:
            out = self.inliner._parse_positional_param_list(params,module_name)
            print("No exceptions thrown")
            print( "Parameter : Value")
            for k, v in out.items():
                print(f"{k} : {v}")
        except ValueError as e:
            print("Test of function Inliner._parse_named_param_list failed due to the following error, possibly expected")
            raise
        except Exception as e:
            print("Test of function Inliner._parse_named_param_list failed due to unexpected error.")
            raise

    def test_named_port_list_parser(self, named_port_list_str, module_name):
        self.inliner._index()
        t = Tokenizer(self.config)
        ports = t.tokenize(named_port_list_str)
        try:
            out = self.inliner._parse_named_port_list(ports,module_name)
            print("No exceptions thrown")
            print( "Parameter : Value")
            for k, v in out.items():
                print(f"{k} : {v}")
        except ValueError as e:
            print("Test of function Inliner._parse_named_port_list failed due to the following error, possibly expected")
            raise
        except Exception as e:
            print("Test of function Inliner._parse_named_port_list failed due to unexpected error.")
            raise

    def test_positional_port_list_parser(self, pos_port_list_str, module_name):
        self.inliner._index()
        t = Tokenizer(self.config)
        ports = t.tokenize(pos_port_list_str)   
        try:
            out = self.inliner._parse_positional_port_list(ports,module_name)
            print("No exceptions thrown")
            print( "Parameter : Value")
            for k, v in out.items():
                print(f"{k} : {v}")
        except ValueError as e:
            print("Test of function Inliner._parse_named_port_list failed due to the following error, possibly expected")
            raise
        except Exception as e:
            print("Test of function Inliner._parse_named_port_list failed due to unexpected error.")
            raise

    def test_instantiation_to_inlined_body(self, instantiation_stmt):
        ''' Params: instantiation_stmt (str), a string in verilog syntax instantiating a module found
            in input file
        '''
        t = Tokenizer(self.config)
        self.inliner._index()
        toks = t.tokenize(instantiation_stmt)
        try:
            out = self.inliner._instantation_to_inlined_body(toks)
            print("No exceptions thrown")
            print("Output")
            strings = [x.to_string() for x in out]
            print("".join(strings))
        except Exception as e:
            print("Test of function Inliner._parse_named_port_list failed due to the following error:")
            raise

    def test_generate_reference_tree(self):
        ''' Test of the Inline._generate_reference_tree function '''
        self.inliner._index()
        self.inliner._generate_reference_tree()
        print(self.inliner.reference_tree)
        # STOPPED HERE

    def test_inline_function(self):
        ''' Test of the Inline._inline() function which creates the class's 
            inlined_modules dictionary
        '''
        self.inliner._index()
        self.inliner._generate_reference_tree()
        print("Testing Inline._inline():\n")
        try:
            self.inliner._inline()
            for name, mod in self.inliner._inlined_modules.items():
                print(f"Module: {name}")
                print("Inlined Version")
                h = "".join( list( map(lambda x : x.to_string(), mod.header)))
                b = "".join( list( map(lambda x : x.to_string(), mod.body)))
                print(h)
                print(b)
                print("\n")
        except:
            print("Error encountered or unexpected exception raised:")
            raise