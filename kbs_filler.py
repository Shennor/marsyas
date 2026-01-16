import os

prepared_kbs_filepath = "./prepared_kbs.kbs"

fillers = [
"fill_tests"
]

# fill tests from logs
def fill_tests(kbs_text, log_info):
    tests_status_path = os.path.join(log_info["folder"], log_info["machine"], 
        "status")
    if not os.path.isdir(tests_status_path):
        print("ERROR: No tests status folder {tests_status_path}")
        return kbs_text
    # for all files add to kbs text object
    for filename in os.listdir(tests_status_path):
        test_name = filename.split('.')[0]
        kbs_text += f"""

ОБЪЕКТ тест_{test_name}
ГРУППА тест
АТРИБУТЫ
  АТРИБУТ имя
    ТИП тип_имя_теста
  АТРИБУТ версия
    ТИП тип_версия_теста
  АТРИБУТ причина
    ТИП тип_причина
  АТРИБУТ рекомендация
    ТИП тип_рекомендация
КОММЕНТАРИЙ тест добавлен исходя из наличия файла {os.path.join(
    tests_status_path, filename)} в логах
         """
    return kbs_text
    
def update_kbs(original_kbs_path, log_info):
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
        with open(prepared_kbs_filepath, 'w') as file:
            file.write(kbs_text)
            print(f"INFO: Knowledge base successfully filled, see {prepared_kbs_filepath}")
    except IOError as e:
        print(f"ERROR: An error occurred while writing updates knowledge base to the file {prepared_kbs_filepath}: {e}")
    
    return prepared_kbs_filepath
    
    
