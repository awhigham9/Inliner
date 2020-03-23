import unittest
import traceback
import sys
from tokenizer import *


class TestTokenizer(unittest.TestCase):

    def setUp(self):
        self.t = Tokenizer("config.json")

    def test_tokenize_classification(self,path="sample.vl"):
        with open(path,"r") as f:
            s = f.read()
            tokens = self.t.tokenize(s)
            for token in tokens:
                if token.token_type == TokenType.DEFAULT:
                    print(f"{token.info()}\t***ERROR***")
                print(token.info())

    def test_tokenize_preservation(self,path="sample.vl"):
        with open(path,"r") as f:
            s = f.read()
            tokens = self.t.tokenize(s)
            s2 = "".join([x.to_string() for x in tokens])
            self.assertEqual(s,s2)
                