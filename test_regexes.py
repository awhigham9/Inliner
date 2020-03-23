import unittest
import regexes

class TestRegexes(unittest.TestCase):
    
    def setUp(self):
        self.v = []
        self.v.append("12'b1000_0101_0001") # Bin 0
        self.v.append("12'B1000_0101_0001") # Bin 1
        self.v.append("36'o5767_4355_5432") # Octal 2
        self.v.append("24'O7777_XXZZ") # Octal 3
        self.v.append("4'd15") # Decimal 4
        self.v.append("10'd10_23") # Decimal 5
        self.v.append("3'h7") # Hex 6
        self.v.append("32'HA7F0_????") # Hex 7
        self.v.append("1234") # Real number 8
        self.v.append("765.543") # Real number 9
        self.v.append("Z") # Z digit 10
        self.v.append("z") # Z digit 11
        self.v.append("?") # Z digit 12
        self.v.append("X") # X digit 13
        self.v.append("x") # X digit 14
        self.v.append("a_variable") # identifier 15
        self.v.append("_another_variable_$") # identifier 16
        self.v.append("A") # identifier 17
        self.v.append("// comemjrng4rbghrb3gro") # comment 18
        self.v.append("///////////////////////") # comment 19
        self.v.append("/* frfnrn \n $finish * \n * \n */") # block comment 20
        self.v.append("\"a string\"") # string 21
        self.v.append("\" 1234 \"") # string 22
        self.v.append("$finish") # system task 23
        self.v.append("$display(opa)") # system task 24
        self.v.append("`include") # compiler directive 25
        self.v.append("`timescale") # compiler directive 26
        self.v.append(".clk(clk),.opa(opa),.opb(opb),.ine(ine_r[0]),.tkz(dre[0:10]),.ovf_flag()") # a named port list 27
        self.v.append("clk,opa,opb,ine_r[0],dre[0:10]") # a positional port list 28
        self.v.append("1e-06") # Real number 29
        self.v.append("1.54372e2") # Real number 30
        self.v.append("1.2E12") # Real number 31

    def run_test(self, true_entries, regex, name=""):
        for i in range(0, len(self.v)):
            output = bool( regex.fullmatch(self.v[i]) )
            expected = i in true_entries
            try:
                if expected:
                    self.assertTrue( output )
                else:
                    self.assertFalse( output ) 
            except:
                print(f"\nFailure testing {name if name else str(regex)} on {self.v[i]}")
                print(f"Expected {expected}, received {not expected}\n")
                raise

    def test_identifier(self):
        self.run_test([10,11,13,14,15,16,17], regexes.identifier)

    def test_string(self):
        self.run_test([21,22], regexes.string)

    def test_comment(self):
        self.run_test([18,19], regexes.comment)

    def test_block_comment(self):
        self.run_test([20], regexes.block_comment)

    def test_sys_task(self):
        self.run_test([23,24], regexes.sys_task)

    def test_comp_dir(self):
        self.run_test([25,26], regexes.comp_dir)

    def test_z_digit(self):
        self.run_test([10,11,12], regexes.z_digit)

    def test_x_digit(self):
        self.run_test([13,14], regexes.x_digit)

    def test_real_number(self):
        self.run_test([8,9,29,30,31], regexes.real_number, "regexes.real_number")

    def test_binary(self):
        self.run_test([0,1], regexes.binary)

    def test_octal(self):
        self.run_test([2,3], regexes.octal)

    def test_hexadecimal(self):
        self.run_test([6,7], regexes.hexadecimal)

    def test_decimal(self):
        self.run_test([4,5], regexes.decimal)

    def test_number(self):
        self.run_test([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,29,30,31], regexes.number, "regexes.number")

    def test_named_port_list(self):
        self.run_test([27], regexes.named_port_list, "regexes.named_port_list")

    def test_positional_port_list(self):
        self.run_test([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,28,29,30,31], regexes.positional_port_list, "regexes.positional_port_list")
