import os

from at_solver.core.solver import Solver

machine_info_parsers = [
# folder/machine/data_about_machine/
"parse_machine_kernel",
"parse_machine_arch",
"parse_machine_name"
]

def parse_machine_kernel(solver: Solver, log_info):
    kernel_log_path = os.path.join(log_info["folder"], log_info["machine"],
        "data_about_machine/kernel.data")
    if not os.path.exists(kernel_log_path):
        print(f"ERROR: no info about machine kernel found (file {kernel_log_path} not exists)")
        return solver
    with open(kernel_log_path, 'r') as f:
        for line in f:
            if line.startswith('kernel-number:'):
                kernel_version = line.split(':', 1)[1].strip()
                print(f"INFO: found kernel version on {log_info['machine']}: {kernel_version}")
                m_kernel = "тестовая_машина.ядро"
                solver.wm.set_value(m_kernel, kernel_version)
                kbs_set_variables.add("m_kernel")
    return solver
    
def parse_machine_arch(solver: Solver, log_info):
    arch_log_path = os.path.join(log_info["folder"], log_info["machine"],
        "data_about_machine/proc_model.data")
    if not os.path.exists(arch_log_path):
        print(f"ERROR: no info about machine arch found (file {arch_log_path} not exists)")
        return solver
    with open(arch_log_path, 'r') as f:
        for line in f:
            m_arch = "тестовая_машина.архитектура"
            solver.wm.set_value(m_arch, line.split()[0])
            kbs_set_variables.add("m_arch")
            break
    return solver

def parse_machine_name(solver: Solver, log_info):
    m_name = "тестовая_машина.имя"
    solver.wm.set_value(m_name, log_info["machine"])
    kbs_set_variables.add("m_name")
    return solver

