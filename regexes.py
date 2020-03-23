import re


##########################################################################################
# REGEX STRINGS

# Non-number lexical tokens
s_identifier = "[a-zA-Z_][\w\$]*"
s_string = "\".*\""
s_comment = "\/\/.*" # Inline comment
s_block_comment = "\/\*[\S\s]*\*\/" # Block comment
s_sys_task = "\$.*" # System Task
s_comp_dir= f"`{s_identifier}" # Compiler Directive 

# Numbers
s_unsigned_digit = "[0-9]"
s_z_digit = "Z|z|\\?" # Matches the high impedance (z) and ? digits
s_x_digit = "X|x" # Matches the unknown digit (x)
s_exp = "[eE]"
s_sign = "[+-]"
s_unsigned_num = f"{s_unsigned_digit}([{s_unsigned_digit}|_])*"
s_real_number = f"{s_unsigned_num}(\.{s_unsigned_num})?({s_exp}({s_sign})?{s_unsigned_num})?"
s_binary = f"[\d]+\'[bB][10_|{s_z_digit}|{s_x_digit}]+" # Matches binary numbers
s_octal = f"[\d]+\'[oO][(1-7)_|{s_z_digit}|{s_x_digit}]+" # Matches octal numbers
s_hexadecimal = f"[\d]+\'[hH][\d(A-F)(a-f)_|{s_z_digit}|{s_x_digit}]+" # Matches hexadecimal numbers
s_decimal = f"[\d]+\'[dD][\d_|{s_z_digit}|{s_x_digit}]+" # Matches decimal numbers
s_number = f"{s_real_number}|{s_binary}|{s_octal}|{s_hexadecimal}|{s_decimal}|{s_z_digit}|{s_x_digit}"

# Port list related regexes
s_indexing_statement = f"\[.+?\]" # Matches "[<anything>]"; edge cases not checked because signal[] is not compilable in verilog
s_named_port_assignment_re = f"\.{s_identifier}\((.*(?=\)))\)"
s_named_port_list = f"^(({s_named_port_assignment_re},))*({s_named_port_assignment_re}(?!,))$"
#s_named_port_list = f"^(?=\."
#s_positional_port_list = f"((({s_identifier}|{s_number})({s_indexing_statement})?),)*(({s_identifier}|{s_number})({s_indexing_statement})?)"
s_positional_port_list = f"^(((({s_identifier})|({s_number}))({s_indexing_statement})?),)*((({s_identifier})|({s_number}))({s_indexing_statement})?(?!,))$"

###############################################################################################################
# COMPILED REGEXES

# Lexical token regexes
identifier = re.compile(s_identifier)
string = re.compile(s_string)
comment = re.compile(s_comment)
block_comment = re.compile(s_block_comment)
sys_task = re.compile(s_sys_task)
comp_dir = re.compile(s_comp_dir)
# Number regexes
z_digit = re.compile(s_z_digit)
x_digit = re.compile(s_x_digit)
real_number = re.compile(s_real_number)
binary = re.compile(s_binary)
octal =  re.compile(s_octal)
hexadecimal = re.compile(s_hexadecimal)
decimal = re.compile(s_decimal)
number = re.compile(s_number)
# Port list related regexe
named_port_list = re.compile(s_named_port_list)
positional_port_list = re.compile(s_positional_port_list)
