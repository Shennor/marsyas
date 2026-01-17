import os

test_meta_folder = "../example_tests_meta"

test_info_fillers = [
"fill_tests",
"fill_test_graph_depend"
]

test_info_parsers = [
# folder/machine/data_about_machine/
"parse_test_status",
"parse_test_graph_depend"
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
  АТРИБУТ зависит_от_графики
    ТИП тип_да_нет
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
        with open(os.path.join(tests_status_folder_path, filename), "r") as f:
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
    
def parse_test_graph_depend(solver: Solver, log_info):
    tests_status_folder_path = os.path.join(log_info["folder"], log_info["machine"], 
        "status")
    if not os.path.isdir(tests_status_folder_path):
        print(f"ERROR: No tests status folder {tests_status_folder_path}")
        return solver
    if not os.path.isdir(test_meta_folder):
        print(f"ERROR: No tests meta folder {test_meta_folder}")
        return solver
    for filename in os.listdir(tests_status_folder_path):
        test_name = filename.split('.')[0]
        test_meta_path = os.path.join(test_meta_folder, test_name, "meta.yaml")
        try:
            with open(test_meta_path, "r") as f:
                lines = list(f)
                for line in lines:
                    if "- graph" in line:
                        var_name = f'{test_name}_graph'
                        globals()[var_name] = f"тест_{test_name}.зависит_от_графики"
                        solver.wm.set_value(globals()[var_name], "Да")
                        print(f"INFO: found from meta.yaml that test {test_name} depends on graphic")
                        return solver
        except Exception as e:
            print(f"ERROR: An error occured while reading test meta file {test_meta_path}: {e}")
    return solver
