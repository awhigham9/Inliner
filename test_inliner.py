import unittest
from inline import *

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