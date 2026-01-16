import os
import glob
import re

from at_krl.core.knowledge_base import KnowledgeBase
from at_solver.core.goals import Goal
from at_solver.core.solver import Solver
from at_solver.core.solver import SOLVER_MODE
from at_solver.core.trace import ForwardStep

kbs_path="./TestingSystem.kbs"
base_logs_folder="../example_logs/"
test_types=["smoke","bench","stress","tail","hand"]

import kbs_filler

kbs_set_variables = set()

# Соберем парсеры из модулей
parsers = []

modules = [
"common_linux_parsers",
"machine_info_parsers"
]

for module_name in modules:
    with open(f"{module_name}.py") as f:
        exec(f.read(), globals())
        parsers.extend(globals().get(module_name))
print("Will be using parsers: ", parsers)

def find_logs():
    logs=[]
    for testtype in test_types:
        log = dict()
        log["type"] = testtype
        folders = glob.glob(os.path.join(base_logs_folder, f"*{testtype}*"))
        if len(folders) != 0:
            log["folder"] = folders[0]
            dirs = [entry.name for entry in os.scandir(log["folder"]) if entry.is_dir()]
            if len(dirs) == 1:
                log["machine"] = dirs[0]
            elif len(dirs) == 0:
                log["machine"] = None
                print(f'ERROR: no machine folder found in {log["folder"]}')
            else:
                log["machine"] = dirs[0]
                print(f'WARNING: more than one folder found in {log["folder"]}; {log["machine"]} selected as machine name')
        else:
            log["folder"] = None
            log["machine"] = None
            print(f"WARNING: folder for {testtype} tests not found")
        logs.append(log)
    return logs


def parse_all(solver, log_info):
    # Если нет логов этого типа (или они сломаны) - пропускаем
    if log_info["folder"] == None or log_info["machine"] == None:
        print(f"WARNING: trying to process not existing log directory for {log_info['type']} tests")
        return solver
    for parser in parsers:
        func = globals().get(parser)
        if callable(func):
            solver = func(solver, log_info)
    return solver

def main():
    print("Search for logs...")
    logs = find_logs()
    print("Start analysing SMOKE")
    log_info = logs[0]
    print("Filling knowledge base...")
    prepared_kbs_path = kbs_filler.update_kbs(kbs_path, log_info)
    print("Reading knowledge base and building solver...")
    knowledge_base = KnowledgeBase.from_krl(open(prepared_kbs_path).read())
    solver = Solver(knowledge_base, SOLVER_MODE.forwards, goals=[])
    print("Parsing facts to working memory...")
    solver = parse_all(solver, log_info)
    print(solver.wm.get_value("тестовая_машина"))
    print("parsed name: ", solver.wm.get_value("тестовая_машина.имя").to_representation())
    print("parsed kernel: ", solver.wm.get_value("тестовая_машина.ядро").to_representation())
    print("parsed arch: ",
 solver.wm.get_value("тестовая_машина.архитектура").to_representation()) 
    return
    
main()
