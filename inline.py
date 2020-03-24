import json
from inliner import *
import argparse

def run(config_path, input_path, output_path, top_modules=None):
    print("Running. . .")
    i = Inliner(config_path,input_path)
    i.inline()
    with open(output_path,'w') as f:
        if top_modules:
            for name in top_modules:
                f.write("".join(list(map(lambda x : x.to_string(), i._inlined_modules[name].header))))
                f.write("".join(list(map(lambda x : x.to_string(), i._inlined_modules[name].body))))
                f.write("\n\n\n")
        else:
            for name in i._inlined_modules:
                f.write("".join(list(map(lambda x : x.to_string(), i._inlined_modules[name].header))))
                f.write("".join(list(map(lambda x : x.to_string(), i._inlined_modules[name].body))))
                f.write("\n\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Performs the inlining process on file using the settings specified in config")
    parser.add_argument("file", help="the input file whose modules will be inlined")
    parser.add_argument("-c", "--config", nargs=1, help="the configuration file that speficies the verilog keywords and special characters (default: %(default)s)", default=["config.json"])
    parser.add_argument("-t", "--top", nargs="?", action="append", const="", help="the top level modules that should appear in the output path; if not specified, all modules are dumped to the output path")
    parser.add_argument("-o", "--out", nargs=1, default=["out.v"], help="the output file path to which the inlined files will be dumped(default: %(default)s)")
    args = parser.parse_args()
    run(args.config[0], args.file, args.out[0], args.top)