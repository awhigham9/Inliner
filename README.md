# Inliner

The following software performs pre-processing of Verilog files for automatic test generation by inlining module instantiations. This software can receive a file containing a series of Verilog modules referencing other modules present in the file, and then peform a program transformation generating each module with all instantiations of other modules replaced with the body of the instantiated module; this is the process of inlining. Each inlined portion is modified to contain the correct port and parameter assignments, so that the inlined version of the module is functionally equivalent to the original. Currently, this software adheres to [1364-2005 - IEEE Standard for Verilog Hardware Description Language](https://doi.org/10.1109/IEEESTD.2006.99495). This standard, however, has been superseded by [1800-2009 - IEEE Standard for SystemVerilog--Unified Hardware Design, Specification, and Verification Language](https://ieeexplore.ieee.org/servlet/opac?punumber=5985441). In the future, the software will transition to supporting the new standard.

***

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

The software requires python3.x.

This software also makes use of the the Icarus Verilog pre-processor to combine many Verilog files into a single file. While this is not necessary to use the python software, it is required to use the executable bash file and will automate the process of combining all relevant Verilog modules into one file. For instructions to install Icarus Verilog, go to [the Icarus Verilog website](http://iverilog.icarus.com/).

**NOTE: Currently, no part of the software uses the Icarus Verilog Pre-Processor. In the near future, however, a bash script will be added to streamline the execution process, and this will use it. For now, it is merely recommended.**

### Installing

Installation can be done directly by cloning the git repository (found [here](https://github.com/awhigham9/Inliner)) using the following command.

``` bash
git clone https://github.com/awhigham9/Inliner.git
```

### Testing

Automated installation tests coming soon. . .

***

## Design

### Inlining Algorithm

The core process of inlining Verilog modules is handled by the `Inliner` class found in inliner.py. The method `Inliner.inline()` encapsulates this algorithm, but in fact the algorithm is divided into a series of three distinct steps, each completed by a method call within `inline()`. Labeled by their method name, the three steps are as follows:

1. `Inliner._index`

   This function reads the tokens from the input file (lexed previously by a `Tokenizer` instance), and then processes these tokens into `Module` objects. This processing is off-loaded to the `_process_module` function, which is called by `_index`. After creation, each module object is stored into the Inliner object's `modules` member, which is a dictionary mapping module names (`str`) to module objects (`Module`).

2. `Inliner._generate_reference_tree`

   This function reads each module stored in `modules` and determines which other modules it references. From this information, a dictionary mapping module names (`str`) to the set composed of the names of the modules it references (`set` of `str`) is created. This dictionary is the `_reference_tree` of that Inliner object. In this context, the term reference is used to mean the instantiation of a module within another. For example, if module A contains instances of modules B and C, its entry in the `reference_tree` would be: `reference_tree['A'] = {'B', 'C'}`, and it would be said that A references C and B. The reference tree is used to determine a valid module inlining order.

3. `Inliner._inline`

   This function performs the task of creating the inlined versions of each module and storing them in the `_inlined_modules` dictionary (maps `str` to `Module` objects). This process is as follows:
   + Call `_get_inline_order` to receive the order in which the reference tree must be evaluated to properly inline all modules.
   + Iterate through this order, doing the following at each step:
     + If the module references other modules, call `_get_inlined_module` and store this new inlined version of the module in `_inlined_modules`. The process performed by `_get_inlined_module` is essentially the process of identifying module instantations within the module body and swapping each instantiation statement for that module's inlined body. This "swap" entails adding input and output assignments, as well as assiging values to parameters.
     + If not, store the original module in `inlined_modules` since the inlined version is identical to the original.

To execute the algorithm from the commandline, use the script `inline.py`. More about running this script can be found in **Using the Software**.

### File Manifest

In alphabetical order:

+ config.json
  + JSON file containing keywords, special characters, and special character sequences appearing in the Verilog syntax. This is primarily used during the lexing of the Verilog files. These keywords and operators are derived from the Verilog standard. The stored dictionary contains the following fields:
    + `keywords`: Verilog keywords to detect
    + `operators`: Verilog operators, as well as some other special characters that for the purpose of the naive lexing performed here can be treated as such
    + `binary_token_pairs`: Special tokes that are two characters long. This is stored as a dictionary, where the second character is mapped to the first; e.g., "&" -> "\~" is equivalent to "\~&". This is used in the detection of operator tokens.
    + Ternary token pairs: Special tokens that are three characters long. This is just like `binary_token_pairs`, except the value mapped to is two characters, not one; e.g. "=" -> "!=" is equivalent to "!==".
+ generator_helper.py
  + Contains a wrapper class for Python's `generator` construct. Accepts an iterable and yields elements through a method call. Primarily used to pass an input stream between scopes more succinctly.
+ inline.py
  + Contains the command line interface of the software. If you are running the software by hand on a Verilog file, and you only need to call the `inline` algorithm and dump the results to a file, you should be using inline.py.
+ inliner.py
  + Contains the `Inliner` class which performs the inlining algorithm discussed previously and stores inlined modules.
+ module.py
  + Contains the `Module` class which serves as a data wrapper for storing a Verilog module. Beyond just storing the text, it stores the name, the header, a list of ports, and a list of parameters.
+ regexes.py
  + Stores all the regexes which should be standardized throughout the project. The regexes which will be matched against, rather than composed into larger regexes, are compiled.
+ test_inliner.py
  + Contains unit tests for the `Inliner` class. Currently it **does not** adhere to Python unit testing standards. It should be updated to do so.
+ test_regexes.py
  + Contains unit tests for the regular expressions stored in regexes.py. Any time a new regex is added, it should receive a unit test in this file. This file currently **does** adhere to Python unit testing standards.
+ test_tokenizer.py
  + Contains unit tests for the `Tokenizer` class. Currently it **does not** adhere to Python unit testing standards; output must be manually verified as correct. It should be updated to do so.
+ tokens.py
  + Contains the `Token` class and the `TokenType` enum. These are used to store and classify text tokens after lexing, respectively.

### Library Reference

Coming soon . . .

***

## Using the Software

To use the inlining script, you first must have a Verilog file containing **all** the modules that are used in the design.

For example, if you have three files A.v, B.v, and C.v that are as follows:

A.v:

```verilog
module A;
    B instance_of_b;
    C instance_of_c;
    //Code1
endmodule;
```

B.v:

```verilog
module B;
    //Code2
endmodule;
```

C.v:

```verilog
module C;
    //Code3
endmodule;
```

To inline module `A` you need to have a file, let's call it A_prepared.v for this example, that is as follows:

A_prepared.v:

```verilog
module A;
    B instance_of_b;
    C instance_of_c;
    //Code1
endmodule;

module B;
    //Code2
endmodule;

module C;
    //Code3
endmodule;
```

The order of the modules in this file does not matter.

A file fitting this criteria could be made by hand, but on large designs this becomes tedious. The alternative solution is to use the Icarus Verilog pre-processor (ivlpp). This software executes pre-processor directives in Verilog files, including `include` statements. Using `include` statements, we can automate the addition of the modules we need in our top-level file. The only manual task is to add the `include` statements.

Back to the example, we can modify A.v to be:

```verilog
`include "B.v"
`include "C.v"

module A;
    B instance_of_b;
    C instance_of_c;
    //Code1
endmodule;
```

Now that we have `include` statements we can run the command

```bash
/path_to_ivlpp_executable/ivlpp -o A_prepared.v A.v
```

which will provide us with a file named A_prepared.v the that looks like this:

```verilog
module B;
    //Code2
endmodule;

module C;
    //Code3
endmodule;

module A;
    B instance_of_b;
    C instance_of_c;
    //Code1
endmodule;
```

**Note**: Be sure all compiler directive settings, such as defines, are in accordance with your final preferences for the design before running ivlpp, because it will execute them along with the `include` statements. Ivlpp can be found in Icarus Verilog's installation directory.

After doing this and obtaining a file with all the necessary modules, inlining them can be completed by running inline.py with your preferred commandline arguments. For guidance on using inline.py you can run:

```bash
python3 inline.py -h
```

For our example, let's say we want our output file of the inlining process to be named inlined_modules.v, and we only want module A to be present in this file. Then we would run:

```bash
python3 inline.py -o inlined_modules.v -t A A_prepared.v
```

After executing this command, you should find the file inlined_modules.v in the directory with the following contents:

```verilog
module A;
    //Code2
    //Code3
    //Code1
endmodule;
```

***

## Remaining Issues

The inlining software is not yet perfect, and there are still some issues that exist, and features in the Verilog standard that aren't yet supported. While a more complete list can be found on the GitHub repo, I will list some of the most notable and critical issues here.

### Bugs in Inlined Module Output

+ Missing semicolons
  + Currently, some lines will be missing semi-colons. This is due to a bug in `Inliner._instantation_to_inlined_body` which I have yet to fix. I will be working on finding its source and correcting it ASAP.
+ Redundant Declaration
  + The function `Inliner._instantation_to_inlined_body` converts a module instantation to a piece of Verilog with the correct assignments corresponding to the port assignments of the original.
  + Currently, it converts `output` nets to `wire` and `output reg` registers to `reg` using a simple find and replace mechanism. This is the naive solution, and the one I could implement most quickly.
  + The issue with this is that often, Verilog modules declare an `output` and declare a `reg` of the same name. Using the find and replace method causes both declarations to remain, producing there to be two declarations of `reg` or a `wire` and a `reg` of the same name in the module. This cannot be compiled.
  + To fix this, always remove the first declaration.
  + This should be fixed soon.
  + An easier to follow diagram is below

Un-inlined Original:

```verilog
module A;
    B instance_of_B
    //Code
endmodule;

module B;
    output x;
    reg x;
    //Other code
endmodule;
```

Current, broken output:

```verilog
module A;
  wire x;
  reg x;
  //Other code
  //Code
endmodule;
```

Correct output:

```verilog
module A;
    reg x;
    //Other code
    //Code
endmodule;
```

+ Possible incorrect tokenization
  + It is also possible, though unlikely, a token will be parsed incorrectly. The tell-tale sign of this is a portion of code that appears to be unedited from its original source, which is usually indicated by the lack of a variable name being prefixed.
  + If this occurs, identify the incorrectly parsed token (it will likely be printed as a default token warning) and post it as an issue on the GitHub (provided it isn't there already), or let me know.
  + If the token is just a time statement (e.g. `100ns`), I know these are currently being classified default, and I am working on fixing it.

### Unsupported features

Some features haven't been added yet, but should be soon. These include:

+ `inout` ports
+ Attributes
+ Any elements in the 1800-2009 IEEE Standard for SystemVerilog not appearing in IEEE Standard 1364-2005.

***

## Authors

Andrew Whigham

To contact me about this software, email me at awhigham@ufl.edu
