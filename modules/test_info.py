import os

test_info_fillers = [
"fill_tests"
]

test_info_parsers = [
# folder/machine/data_about_machine/
"parse_test_status",
#"parse_test_version"
]

test_list = []

# Добавление объектов в БЗ для каждого теста в логах
def fill_tests(kbs_text, log_info):
    tests_status_folder_path = os.path.join(log_info["folder"], log_info["machine"], 
        "status")
    if not os.path.isdir(tests_status_folder_path):
        print(f"ERROR: No tests status folder {tests_status_path}")
        return kbs_text
    # for all files add to kbs text object
    for filename in os.listdir(tests_status_folder_path):
        test_name = filename.split('.')[0]
        kbs_text += f"""

ОБЪЕКТ тест_{test_name}
ГРУППА тест
АТРИБУТЫ
  АТРИБУТ статус
    ТИП тип_статус_теста
  АТРИБУТ причина
    ТИП тип_причина
  АТРИБУТ рекомендация
    ТИП тип_рекомендация
КОММЕНТАРИЙ тест добавлен исходя из наличия файла {os.path.join(
    tests_status_folder_path, filename)} в логах
        """
    return kbs_text
    
# Добавление в РП информации о статусе каждого теста
def parse_test_status(solver: Solver, log_info):
    tests_status_folder_path = os.path.join(log_info["folder"], log_info["machine"], 
        "status")
    if not os.path.isdir(tests_status_folder_path):
        print(f"ERROR: No tests status folder {tests_status_folder_path}")
        return solver
    # for all files add to kbs text object
    for filename in os.listdir(tests_status_folder_path):
        test_name = filename.split('.')[0]
        test_status = "UNKNOWN"
        with open(os.path.join(tests_status_folder_path, filename)) as f:
            test_status = list(f)[-1].split()[0]
            if test_status == "0":
                test_status = "PASS"
            elif test_status == "1":
                test_status = "FAIL"
            elif test_status == "2":
                test_status = "SKIP"
            else:
                test_status = "FAIL"
        # добавить в словарь добавленных значений, добавить в solver
        var_name = f'{test_name}_status'
        globals()[var_name] = f"тест_{test_name}.статус"
        solver.wm.set_value(globals()[var_name], test_status)
        print(f"INFO: found test {test_name} status: {test_status}")
    return solver
    
def get_test_names():
    pass
