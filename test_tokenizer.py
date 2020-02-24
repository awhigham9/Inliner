import unittest
import traceback
import sys
from tokenizer import *


class TestTokenizer(unittest.TestCase):

    def setUp(self):
        self.t = Tokenizer("config.json")

    def test_tokenize_classification(self,path):
        with open(path,"r") as f:
            s = f.read()
            tokens = self.t.tokenize(s)
            for token in tokens:
                print(token.info())

    def test_tokenize_preservation(self,path,path2):
        with open(path,"r") as f:
            with open(path2, 'w') as out:
                s = f.read()
                tokens = self.t.tokenize(s)
                for token in tokens:
                    out.write(token.content)      


if __name__ == "__main__":
    t = TestTokenizer()
    t.setUp()
    t.test_tokenize_preservation('sample/sample_top.v', 'test.vl')