import sys
import os
import time
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from example import test_example

class WaitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Ожидание")
        self.setModal(True)

        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.label = QLabel("Извлечение фактов…")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

class LoadWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, func, path, parent=None):
        super().__init__(parent)
        self.func = func
        self.path = path

    def run(self):
        try:
            result = self.func(self.path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class LogAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Прототип: Решатель проблем (демо)')
        self.setGeometry(100, 100, 800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Секция выбора папки
        folder_group = QGroupBox("Выбор папки")
        folder_layout = QVBoxLayout()
        
        # Панель выбора папки
        folder_panel = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText('Выберите папку или введите путь')
        
        browse_button = QPushButton('Выбрать папку')
        browse_button.clicked.connect(self.browse_directory)
        
        folder_panel.addWidget(QLabel('Папка:'))
        folder_panel.addWidget(self.folder_input)
        folder_panel.addWidget(browse_button)

        
        # Кнопки действий
        action_panel = QHBoxLayout()
        
        
        clear_button = QPushButton('Очистить')
        clear_button.clicked.connect(self.clear_all)
        
        action_panel.addWidget(clear_button)
        action_panel.addStretch()
        
        folder_layout.addLayout(folder_panel)
        folder_layout.addLayout(action_panel)
        folder_group.setLayout(folder_layout)
        
        # Список файлов
        files_group = QGroupBox("Найденные файлы")
        files_layout = QVBoxLayout()
        
        # Текстовое поле для отображения путей
        self.files_text = QTextEdit()
        self.files_text.setReadOnly(True)
        self.files_text.setPlaceholderText('Здесь появятся пути к найденным файлам...')
        
        # Панель информации
        info_panel = QHBoxLayout()
        self.file_count_label = QLabel('Файлов: 0')
        self.total_size_label = QLabel('Размер: 0 Б')
        self.next_step = QPushButton('Далее')
        self.next_step.clicked.connect(self.run_analysis)
        
        info_panel.addWidget(self.file_count_label)
        info_panel.addWidget(self.total_size_label)
        info_panel.addStretch()
        info_panel.addWidget(self.next_step)
        
        files_layout.addWidget(self.files_text)
        files_layout.addLayout(info_panel)
        files_group.setLayout(files_layout)
        
        # Добавляем все в основной layout
        main_layout.addWidget(folder_group)
        main_layout.addWidget(files_group)

        # Создать меню и титульный экран
        self.create_menu()
        
        # Список файлов для передачи в функцию
        self.found_files = []
        
    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            'Выберите папку для анализа',
            '',
            QFileDialog.ShowDirsOnly
        )
        if dir_path:
            self.folder_input.setText(dir_path)
            self.scan_directory()
            
    def scan_directory(self):
        dir_path = self.folder_input.text()
        if not dir_path or not os.path.isdir(dir_path):
            QMessageBox.warning(self, 'Ошибка', 'Укажите существующую папку')
            return
        try:
            # Очищаем предыдущие результаты
            self.found_files = []
            self.files_text.clear()
            
            # Рекурсивно собираем все файлы
            progress = QProgressDialog("Сканирование папки...", "Отмена", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            total_size = 0
            file_count = 0
            
            # Рекурсивный обход всех файлов
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.found_files.append(file_path)
                    
                    # Добавляем путь в текстовое поле
                    self.files_text.append(file_path)
                    
                    try:
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
                    
                    file_count += 1
                    
                    # Обновляем прогресс каждые 100 файлов
                    if file_count % 100 == 0:
                        progress.setLabelText(f"Найдено файлов: {file_count}")
                        QApplication.processEvents()
                
                # Проверяем отмену
                if progress.wasCanceled():
                    break
            
            progress.close()
            
            # Обновляем статистику
            self.update_stats(file_count, total_size)
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при сканировании: {str(e)}')
            
    def update_stats(self, file_count, total_size):
        self.file_count_label.setText(f'Файлов: {file_count}')
        
        # Форматируем размер
        if total_size < 1024:
            size_text = f'{total_size} Б'
        elif total_size < 1024 * 1024:
            size_text = f'{total_size / 1024:.1f} КБ'
        elif total_size < 1024 * 1024 * 1024:
            size_text = f'{total_size / (1024 * 1024):.1f} МБ'
        else:
            size_text = f'{total_size / (1024 * 1024 * 1024):.1f} ГБ'
            
        self.total_size_label.setText(f'Общий размер: {size_text}')
        
    def run_analysis(self):
        """Запустить анализ с найденными файлами"""
        if not self.folder_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите путь')
            return
            
        try:
            # Здесь вызываем функцию анализа
            # Передаем список путей к файлам
            # TODO
            # Показываем результат в диалоговом окне
            self.show_result()
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при анализе: {str(e)}')
            
    def load(self, path: str):
        """
        ИЗМЕНЯЕМАЯ ФУНКЦИЯ АНАЛИЗА
        
        Аргументы:
        file_paths - список полных путей ко всем найденным файлам
        
        Возвращает строку с результатами анализа
        """
        # TODO
        #result = f"{path}"
        result = test_example()

        return result
        
    def show_result(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Результаты анализа')
        dialog.setGeometry(200, 200, 700, 500)
        
        layout = QVBoxLayout()
        
        # Поле с результатами
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier", 10))

        text_edit.setPlaceholderText("Анализ логов...")
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        copy_button = button_box.addButton("Копировать", QDialogButtonBox.ActionRole)
        save_button = button_box.addButton("Сохранить", QDialogButtonBox.ActionRole)
        
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addWidget(text_edit)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        # Запустить загрузку в другом потоке с индикатором ожидания
        path = self.folder_input.text()

        copy_button.setEnabled(False)
        save_button.setEnabled(False)

        wait = WaitDialog(self)
        wait.label.setText("Загрузка результатов...")
        wait.show()

        thread = QThread(self)
        worker = LoadWorker(self.load, path)
        worker.moveToThread(thread)

        def on_finished(res_text):
            text_edit.setPlainText(res_text)
            copy_button.setEnabled(True)
            save_button.setEnabled(True)
            try:
                wait.accept()
            except:
                wait.close()

        def on_error(err):
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки: {err}')
            try:
                wait.accept()
            except:
                wait.close()

        thread.started.connect(worker.run)
        worker.finished.connect(on_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(on_error)
        thread.finished.connect(thread.deleteLater)

        copy_button.clicked.connect(lambda: self.copy_to_clipboard(text_edit.toPlainText()))
        save_button.clicked.connect(lambda: self.save_result(text_edit.toPlainText()))

        thread.start()

        dialog.exec_()
        
        
    def copy_to_clipboard(self, text):
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Скопировано", "Результаты скопированы")
        
    def save_result(self, text):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить результаты",
            "анализ_результат.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "Сохранено", f"Файл сохранен: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
        
    def clear_all(self):
        """Очистить все поля"""
        self.folder_input.clear()
        self.files_text.clear()
        self.found_files = []
        self.file_count_label.setText('Файлов: 0')
        self.total_size_label.setText('Размер: 0 Б')

    def create_menu(self):
        """Создать меню приложения, в т.ч. Консультация->Начать"""
        menubar = self.menuBar()
        consult_menu = menubar.addMenu('Консультация')

        start_action = QAction('Начать', self)
        start_action.setStatusTip('Начать режим консультации')
        start_action.triggered.connect(self.start_consultation)
        consult_menu.addAction(start_action)

    def start_consultation(self):
        """Запустить режим консультации: показать информацию и выбрать файл журналов"""
        info_text = (
            "Режим консультации позволяет получить рекомендации на основе прямого вывода "
            "(с использованием АТ-РЕШАТЕЛЯ).\n\n"
            "Далее Вам будет предложено выбрать файл журналов тестирования, на основе которого "
            "будет сформировано начальное состояние рабочей памяти."
        )

        QMessageBox.information(self, 'Режим консультации', info_text)

        # Показать главное окно и открыть диалог выбора папки для анализа
        self.show()
        try:
            self.raise_()
        except Exception:
            pass

        dir_path = QFileDialog.getExistingDirectory(
            self,
            'Выберите папку для анализа',
            '',
            QFileDialog.ShowDirsOnly
        )
        if dir_path:
            # Установить выбранную папку и запустить сканирование
            self.folder_input.setText(dir_path)
            self.files_text.clear()
            self.scan_directory()

            QMessageBox.information(self, 'Папка выбрана', 'Папка выбрана и просканирована. Вы можете нажать "Далее" для анализа.')

    def show_title_screen(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Прототип ИЭС "Диагностика состояния ОС для процессоров семейства Эльбрус на основе артефактов тестирования"')
        dialog.setModal(True)
        dialog.setFixedSize(560, 320)

        layout = QVBoxLayout()

        title = QLabel('<h1>Прототип ИЭС</h1>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        title = QLabel('<h1>"Диагностика состояния ОС </h1>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        title = QLabel('<h1>для процессоров семейства Эльбрус </h1>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        title = QLabel('<h1>на основе артефактов тестирования"</h1>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel('Демонстрационный интерфейс для режима консультации')
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        info = QLabel(
            'Режим консультации позволяет получать рекомендации на основе прямого вывода.\n'
            'Для начала нажмите "Начать консультацию" — вам предложат выбрать файл журналов тестирования.'
        )
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        start_btn = QPushButton('Начать консультацию')
        start_btn.clicked.connect(lambda: (dialog.accept(), self.start_consultation()))
        btn_layout.addWidget(start_btn)

        #close_btn = QPushButton('Закрыть')
        #close_btn.clicked.connect(dialog.reject)
        #btn_layout.addWidget(close_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = LogAnalyzerApp()
    # Показываем только титульный экран при старте; главное окно откроется при запросе консультации
    window.show_title_screen()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
