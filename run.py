# Импорты
import os
import glob
import re
import sys
from at_krl.core.knowledge_base import KnowledgeBase
from at_solver.core.goals import Goal
from at_solver.core.solver import Solver
from at_solver.core.solver import SOLVER_MODE
from at_solver.core.trace import ForwardStep

# Константы (в будущем переделать под аргументы скрипта)
kbs_path = "./TestingSystem.kbs"
prepared_kbs_path = "./prepared_kbs.kbs"
base_logs_folder = "../example_logs/"
modules_folder = "./modules"
test_types = ["smoke","bench","stress","tail","hand"]

import kbs_filler
kbs_set_variables = set()

# Чтение списка модулей
try:
    with open("modules.txt") as f:
        modules = [line.split()[0] for line in f if not line.startswith("#")]
except Exception as e:
    print(f"ERROR: An error occured while reading file modules.txt: {e}")
    sys.exit()
print(f"Modules enabled: {modules}")

fillers = []
parsers = []

# Загрузка филлеров и парсеров из модулей
for module_name in modules:
    try:
        with open(os.path.join(modules_folder, f"{module_name}.py")) as f:
            exec(f.read(), globals())
            fillers.extend(globals().get(f"{module_name}_fillers"))
            parsers.extend(globals().get(f"{module_name}_parsers"))
    except Exception as e:
        print(f"ERROR: An error occured while processing module {module_name}: {e}")
        sys.exit()
        
print("Will be using parsers: ", parsers)
print("Will be using fillers: ", fillers)

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


def fill_all(original_kbs_path, log_info):
    kbs_text = ""
    try:
        with open(original_kbs_path, 'r') as file:
            kbs_text = file.read()
    except FileNotFoundError:
        print(f"ERROR: The file '{original_kbs_path}' not found.")
    except Exception as e:
        print(f"ERROR: An error occurred while reading {original_kbs_path}: {e}")
    
    for filler in fillers:
        func = globals().get(filler)
        if callable(func):
            kbs_text = func(kbs_text, log_info)
    # save new version of kbs
    try:
        with open(prepared_kbs_path, 'w') as file:
            file.write(kbs_text)
            print(f"INFO: Knowledge base successfully filled, see {prepared_kbs_path}")
    except IOError as e:
        print(f"ERROR: An error occurred while writing updates knowledge base to the file {prepared_kbs_path}: {e}")
    return prepared_kbs_path

def parse_all(solver, log_info):
    # Если нет логов этого типа (или они сломаны) - пропускаем
    if log_info["folder"] == None or log_info["machine"] == None:
        print(f"WARNING: Trying to process not existing log directory for {log_info['type']} tests")
        return solver
    for parser in parsers:
        func = globals().get(parser)
        if callable(func):
            solver = func(solver, log_info)
    return solver

def main():
    print("Search for logs...")
    logs = find_logs()
    print("Start analysing TAIL")
    log_info = logs[3]
    print("Filling knowledge base...")
    fill_all(kbs_path, log_info)
    print("Reading knowledge base and building solver...")
    knowledge_base = KnowledgeBase.from_krl(open(prepared_kbs_path).read())
    solver = Solver(knowledge_base, SOLVER_MODE.forwards, goals=[])
    print("Parsing facts to working memory...")
    solver = parse_all(solver, log_info)
    #print(solver.wm.get_value("тестовая_машина"))
    #print("parsed test broken_lib_path status: ", solver.wm.get_value("тест_broken_lib_path.статус").to_representation())
    #print("parsed kernel: ", solver.wm.get_value("тестовая_машина.ядро").to_representation())
    #print("parsed arch: ", solver.wm.get_value("тестовая_машина.архитектура").to_representation()) 
    return
    
main()
