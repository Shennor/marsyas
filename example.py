# Импорты
import os
import glob
import re
import sys
import json
from at_krl.core.knowledge_base import KnowledgeBase
from at_solver.core.goals import Goal
from at_solver.core.solver import Solver
from at_solver.core.solver import SOLVER_MODE
from at_solver.core.trace import ForwardStep

def test_example():
    # Read example knowledge base
    knowledge_base = KnowledgeBase.from_krl(open("./example.kbs").read())
    solver = Solver(knowledge_base, SOLVER_MODE.forwards, goals=[])
    
    # Filling work memory
    solver.wm.set_value("тест_ViennaCL.статус","FAIL")
    solver.wm.set_value("тест_ViennaCL.зависит_от_графики","Да")
    solver.wm.set_value("тест_ViennaCL_содержит_ошибку_SIGBUSS.присутствие","Да")
    solver.wm.set_value("тестирование.количество_упавших_тестов_на_графику","7")
    solver.wm.set_value("машина.установлена_модель_видеокарты","Radeon3000")
    solver.wm.set_value("тест_dacapo_java11_9.статус","FAIL")
    solver.wm.set_value("тест_dacapo_java11_9_содержит_ошибку_OOM.присутствие", "Да")
    solver.wm.set_value("конфигурация_JVM.используется_GC","Нет")
    solver.wm.set_value("конфигурация_JVM.использование_оптимизации","Нет")
    solver.wm.set_value("тест_dacapo_java11_9.среднее_использование_памяти_при_запуске","90.0")  
    solver.wm.set_value("тест_dacapo_java11_9.зависит_от_JVM","Да")
    solver.wm.set_value("тестирование.количество_упавших_тестов_JVM","1")
    solver.wm.set_value("тест_peak_test.статус","FAIL")
    solver.wm.set_value("тест_peak_test_содержит_ошибку_OOM.присутствие", "Да")
    solver.wm.set_value("тест_peak_test.среднее_использование_памяти_при_запуске", "91.6")
    solver.wm.set_value("тест_peak_test.монопольный_запуск", "Нет")
    solver.wm.set_value("тестирование.тип","smoke")
    solver.wm.set_value("тестирование.количество_упавших_тестов_JVM","2")
    
    # Get initial values as text 
    values_before = solver.wm.all_values_dict
    values_before_report = "Состояние РП:\n\n"
    for k, v in values_before.items():
        values_before_report += f"{k} = {v['content']}\n" 
    values_before_report += "\n\n"
    
    # Run forward
    solver.run_forward()
    
    # Get trace as text report
    report = "Трассировка вывода:\n"
    for i, step in enumerate(solver.trace.steps):
        if isinstance(step, ForwardStep):
            report += f"\nSTEP {i}\n"
            report += f"{step.selected_rule.id}\n"
            report += f"Rule condition value {step.rule_condition_value.to_representation()}\n"
            report += "firing instrictions:\n"
            if step.rule_condition_value.content:
                for instr in step.selected_rule.instructions:
                    report += f"\t {instr.krl}\n"
            else:
                for instr in step.selected_rule.else_instructions:
                    report += f"\t {instr.krl}\n"
    
    
    
    return values_before_report + report
