# Inliner

The following software performs pre-processing of Verilog files for automatic test generation by inlining module instantiations. This software can receive a file containing a series of Verilog modules referencing other modules present in the file, and then peform a program transformation generating each module with all instantiations of other modules replaced with the body of the instantiated module; this is the process of inlining. Each inlined portion is modified to contain the correct port and parameter assignments, so that the inlined version of the module is functionally equivalent to the original. Currently, this software adheres to [1364-2005 - IEEE Standard for Verilog Hardware Description Language](https://doi.org/10.1109/IEEESTD.2006.99495). This standard however has been superseded by [1800-2009 - IEEE Standard for SystemVerilog--Unified Hardware Design, Specification, and Verification Language](https://ieeexplore.ieee.org/servlet/opac?punumber=5985441). In the future, the software will transition to supporting the new standard.

***

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

This software makes use of the the Icarus Verilog pre-processor to combine many Verilog files into a single file. While this is not necessary to use the python software, it is required to use the executable bash file and will automate the process of combining all relevant Verilog modules into one file. For instructions to install Icarus Verilog, go to [the Icarus Verilog website](http://iverilog.icarus.com/).

The software also requires python3.x.

### Installing

Installation can be done directly by cloning the git repository (found [here](https://github.com/awhigham9/Inliner)) using the following command.

``` bash
git clone https://github.com/awhigham9/Inliner.git
```

After installation, you can test the software on a provided sample by running the test.sh script.

***

## Design

### Inlining Algorithm

The core process of inlining Verilog modules is handled by the `Inliner` class found in inliner.py. This process was divided into a series of methods, each completing a step in the process. Labeled by their method name, the three steps are as follows:

1. `Inliner._index`

   This function reads the tokens from the input file (lexed previously by a `Tokenizer` instance), and then processes these tokens into `Module` objects. This processing is off-loaded to the `_process_module` function, which is called by `_index`. After creation, each module object is stored into the Inliner object's `modules` member, which is a dictionary mapping module names (`str`) to module objects (`Module`).

2. `Inliner._generate_reference_tree`

   This function reads each module stored in `modules` and determines which other modules it references. From this information, a dictionary mapping module names (`str`) to the set composed of the names of the modules it references (`set` of `str`) is created. This dictionary is the `reference_tree` of that Inliner object. In this context, the term reference is used to mean the instantiation of a module within another. For example, if module A contains instances of modules B and C, its entry in the `reference_tree` would be: `reference_tree['A'] = {'B', 'C'}`, and it would be said that A references C and B. The reference tree is used to determine a valid module inlining order.

3. `Inliner._inline`

   This function performs the task of creating the inlined versions of each module and storing them in the `_inlined_modules` dictionary (maps `str` to `Module` objects). This process is as follows:
   + Call `_get_inline_order` to receive the order in which the reference tree must be evaluated to properly inline all modules.
   + Iterate through this order, doing the following at each step:
     + If the module references other modules, call `_get_inlined_module` and store this new inlined version of the module in `_inlined_modules`. The process performed by `_get_inline_module` is commented within the code, but is essentially the process of identifying module instantations within the module body and swapping each instantiation statement for that modules inlined body. This "swap" entails adding input and output assignments, as well as assiging values to parameters.
     + If not, store the original module in `inlined_modules` since the inlined version is identical to the original.

These methods must be called in a particular order, and so have been encapsulated within a single method which is designed to be called externally, `Inliner.inline`.

## File Manifest

In alphabetical order:

+ config.json
  + JSON file containing keywords, special characters, and special character sequences appearing in the Verilog syntax. This is primarily used during the lexing of the Verilog files. These keywords and operators are derived from the Verilog standard. The stored dictionary contains the following fields:
    + `keywords`: Verilog keywords to detect
    + `operators`: Verilog operators, as well as some other special characters that for the purpose of the naive lexing performed here can be treated as such
    + `binary_token_pairs`: Special tokes that are two characters long. This is stored as a dictionary, where the second character is mapped to the first; e.g., "&" -> "~" is equivalent to "~&". This is used in the detection of operator tokens.
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

## API Reference
