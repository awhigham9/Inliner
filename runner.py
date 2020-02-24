import json
from inline import *

def run(config_path,input_path):
    with open(input_path,'r') as f:
        jobs = json.load(f)
        print("Running. . .")
        for job in jobs:
            try:
                inl = Inliner(config_path,job["input_path"])
                inl._index()
                s = inl._output_module(job["module"],job["prefix"])
                out = open(job["output_path"],'w')
                out.write(s)
            except Exception as e:
                print(e)
                


#if __name__ == "__main__":
    run("./config.json","./jobs/mem_ctrl/jobs.json")