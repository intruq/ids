import sys
import os
import subprocess
from time import sleep
from dotenv import dotenv_values
import warnings

warnings.filterwarnings('ignore', message='.*cryptography', )

def fix_filepaths(dict):
    for i in dict:
        split = dict[i].split("||")
        if len(split) > 1:
            dict[i] = os.path.abspath(os.path.join(*split))
    return dict

def init():
    

    warnings.filterwarnings('ignore', message='.*cryptography', )

    env = fix_filepaths(dotenv_values("development_configs/c2_template.env"))
    subprocess.Popen(["python", "./../implementation/c2_server.py"],
                     env={
                         **os.environ,
                         **env,
                     })

    env = fix_filepaths(dotenv_values("development_configs/lm_1_template.env"))
    subprocess.Popen(["python", "../implementation/local_monitor.py"],
                     env={
                         **os.environ,
                         **env,
                     })

    env = fix_filepaths(dotenv_values("development_configs/lm_2_template.env"))
    subprocess.Popen(["python", "../implementation/local_monitor.py"],
                     env={
                         **os.environ,
                         **env,
                     })

    env = fix_filepaths(dotenv_values("development_configs/nm_1_template.env"))
    subprocess.Popen(["python", "../implementation/neighborhood_monitor.py"],
                     env={
                         **os.environ,
                         **env,
                     })

    env = fix_filepaths(dotenv_values("development_configs/nm_2_template.env"))
    subprocess.Popen(["python", "../implementation/neighborhood_monitor.py"],
                     env={
                         **os.environ,
                         **env,
                     })

    subprocess.Popen(["python", "webserver.py"], cwd="../visualization")
    
    while True:
        sleep(1)


if __name__ == '__main__':
    init()
