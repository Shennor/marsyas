
common_linux_fillers = [
"fill_SIGBUSS",
"fill_unknown_service",
"fill_no_file",
]

common_linux_parsers = [
"parse_SIGBUSS",
"parse_unknown_service",
"parse_no_file",
]

global_test_list = []

# -------------------------------- UTILS --------------------------------------

def get_test_list(log_info):
    if len(global_test_list) == 0:
        tests_status_folder_path = os.path.join(log_info["folder"], log_info["machine"], 
            "status")
        if not os.path.isdir(tests_status_folder_path):
            print(f"ERROR: No tests status folder {tests_status_path}")
            return test_list
        for filename in os.listdir(tests_status_folder_path):
            test_name = filename.split('.')[0]
            global_test_list.append(test_name)
    return global_test_list
        

def add_error_object(kbs_text, log_info, error_name):
    test_list = get_test_list(log_info)
    # for all files add to kbs text object
    for test in test_list:
        kbs_text += f"""
        
ОБЪЕКТ тест_{test}_содержит_ошибку_{error_name}
ГРУППА факт
АТРИБУТЫ
  АТРИБУТ присутствие
    ТИП тип_да_нет
        """
    print(f"INFO: Added {error_name} error object for {len(test_list)} tests")
    return kbs_text
   
   
# ------------------------------- TEMPLATES ----------------------------------
# Генерация объектов для каждого теста и ошибки
def fill_template(kbs_text, log_info):
    # Add your error name:
    error_name = ""
    return add_error_object(kbs_text, log_info, error_name)
   
# Определение наличия ошибки
def parse_template(solver, log_info):
    # Add your error name:
    error_name = ""
    test_list = get_test_list(log_info)
    for test in test_list:
        test_log_path = os.path.join(log_info["folder"], log_info["machine"], 
            f"{test}.log")
        try:
            with open(test_log_path, "r") as f:
                text = f.read()
                error_exists = False
                # add your error search
                # ...
                if False:
                    print(f"INFO: Found error тест_{test}_содержит_ошибку_{error_name}")
                var_name = f'{test}_{error_name}'
                globals()[var_name] = f"тест_{test}_содержит_ошибку_{error_name}.присутствие"
                solver.wm.set_value(globals()[var_name], "Да" if error_exists else "Нет")
        except Exception as e:
            print(f"ERROR: An error occured while opening log file {test_log_path}: {e}")
    return solver
   

# ------------------------------ ENTITIES ------------------------------------- 

# 1 
def fill_SIGBUSS(kbs_text, log_info):
    error_name = "SIGBUSS"
    return add_error_object(kbs_text, log_info, error_name)
    
def parse_SIGBUSS(solver, log_info):
    # Add your error name:
    error_name = "SIGBUSS"
    test_list = get_test_list(log_info)
    for test in test_list:
        test_log_path = os.path.join(log_info["folder"], log_info["machine"], 
            f"{test}.log")
        try:
            with open(test_log_path, "r") as f:
                text = f.read()
                error_exists = False
                # error search
                patterns = [
    r'SIGBUS',
    r'bus error',
    r'ошибка шины',
    r'сбой шины'
]
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        error_exists = True
                        print(f"INFO: Found error тест_{test}_содержит_ошибку_{error_name}")
                # adding fact to working memory
                var_name = f'{test}_{error_name}'
                globals()[var_name] = f"тест_{test}_содержит_ошибку_{error_name}"
                solver.wm.set_value(globals()[var_name], "Да" if error_exists else "Нет")
        except Exception as e:
            print(f"ERROR: An error occured while opening log file {test_log_path}: {e}")
    return solver

# 2
def fill_unknown_service(kbs_text, log_info):
    error_name = "unknown_service"
    return add_error_object(kbs_text, log_info, error_name)
    
def parse_unknown_service(solver, log_info):
    # Add your error name:
    error_name = "unknown_service"
    test_list = get_test_list(log_info)
    for test in test_list:
        test_log_path = os.path.join(log_info["folder"], log_info["machine"], 
            f"{test}.log")
        try:
            with open(test_log_path, "r") as f:
                text = f.read()
                error_exists = False
                # error search
                patterns = [
"service is not recognized by the system",
"unrecognized service"
                ]
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        error_exists = True
                        print(f"INFO: Found error тест_{test}_содержит_ошибку_{error_name}")
                # adding fact to working memory
                var_name = f'{test}_{error_name}'
                globals()[var_name] = f"тест_{test}_содержит_ошибку_{error_name}.присутствие"
                solver.wm.set_value(globals()[var_name], "Да" if error_exists else "Нет")
        except Exception as e:
            print(f"ERROR: An error occured while opening log file {test_log_path}: {e}")
    return solver

# 3
def fill_no_file(kbs_text, log_info):
    error_name = "no_file"
    return add_error_object(kbs_text, log_info, error_name)
    
def parse_no_file(solver, log_info):
    # Add your error name:
    error_name = "no_file"
    test_list = get_test_list(log_info)
    for test in test_list:
        test_log_path = os.path.join(log_info["folder"], log_info["machine"], 
            f"{test}.log")
        try:
            with open(test_log_path, "r") as f:
                text = f.read()
                error_exists = False
                # error search
                patterns = [
"Нет такого файла или каталога",
"No such file"
                ]
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        error_exists = True
                        print(f"INFO: Found error тест_{test}_содержит_ошибку_{error_name}")
                # adding fact to working memory
                var_name = f'{test}_{error_name}'
                globals()[var_name] = f"тест_{test}_содержит_ошибку_{error_name}.присутствие"
                solver.wm.set_value(globals()[var_name], "Да" if error_exists else "Нет")
        except Exception as e:
            print(f"ERROR: An error occured while opening log file {test_log_path}: {e}")
    return solver

# Генерация правила (генерация для каждого теста)

# TODO
