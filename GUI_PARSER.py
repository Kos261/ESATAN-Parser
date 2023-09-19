import sys
import re
import time
import os
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QTextEdit,QStyleFactory
from PyQt5.QtGui import QPalette, QColor
from PARSER import Parser,Point,Triangle,Rectangle



class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui,self).__init__(*args,**kwargs)
        self.my_folder = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER" #Tutaj zmienić na home
        self.two_files_selected = False
        self.BDF_filename = None
        self.excel_filename = None
        self.button_size = 150
        self.setFixedSize(900, 600)

        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget) 
        self.setWindowTitle('FEMAP - ESATAN PARSER')
        self.ButtonContainer = QtWidgets.QGridLayout()
        self.main_layout = QHBoxLayout(self.widget)

        self.darkMode()
        self.createButtons()
        
        self.main_layout.addLayout(self.ButtonContainer)
        self.main_layout.addWidget(self.text_edit)

    def darkMode(self):
        # Tworzenie ciemnego motywu
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Ustawianie ciemnego motywu
        self.setPalette(dark_palette)

        # Ustawianie ciemnego stylu
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def createButtons(self):
        ###TWORZYMY WIDGETY I USTAWIAMY JE###
        
        self.EsatanButton = QtWidgets.QPushButton(self.widget)
        self.EsatanButton.setText("Wybierz folder\nEsatana")
        self.EsatanButton.setFixedSize(self.button_size, self.button_size)
        self.EsatanButton.clicked.connect(self.select_folder)
        self.ButtonContainer.addWidget(self.EsatanButton, 0, 2)
         
        self.BDFButton = QtWidgets.QPushButton(self.widget)
        self.BDFButton.setText("Plik BDF")
        self.BDFButton.setFixedSize(self.button_size, self.button_size)
        self.BDFButton.clicked.connect(self.get_BDFfile)
        self.ButtonContainer.addWidget(self.BDFButton, 0, 0)

        self.ExcelButton = QtWidgets.QPushButton(self.widget)
        self.ExcelButton.setText("Plik Excel")
        self.ExcelButton.setFixedSize(self.button_size, self.button_size)
        self.ExcelButton.clicked.connect(self.get_XLSXfile)
        self.ButtonContainer.addWidget(self.ExcelButton, 0, 1)

        self.copyButton = QtWidgets.QPushButton(self.widget)
        self.copyButton.setText("Skopiuj pliki")
        self.copyButton.clicked.connect(self.copy_files)
        self.copyButton.setFixedSize(self.button_size, self.button_size)
        self.ButtonContainer.addWidget(self.copyButton, 1, 0)

        self.deleteButton = QtWidgets.QPushButton(self.widget)
        self.deleteButton.setText("Usuń stare pliki")
        self.deleteButton.clicked.connect(self.confirm_remove_workbench)
        self.deleteButton.setFixedSize(self.button_size, self.button_size)
        self.ButtonContainer.addWidget(self.deleteButton, 1, 1)

        self.testButton = QtWidgets.QPushButton(self.widget)
        self.testButton.setText("Test BAT")
        self.testButton.clicked.connect(self.get_ERGfile)
        self.testButton.setFixedSize(self.button_size, self.button_size)
        self.ButtonContainer.addWidget(self.testButton, 1, 2)

        self.clear_button = QPushButton("Clear\nconsole")
        self.clear_button.clicked.connect(self.clear_console)
        self.clear_button.setFixedSize(self.button_size, self.button_size)
        self.ButtonContainer.addWidget(self.clear_button,2,0)



        self.text_edit = QTextEdit()
        font = self.text_edit.currentFont()
        font.setPointSize(13)
        self.text_edit.setFont(font)
        self.text_edit.setReadOnly(True)  # Ustaw tryb tylko do odczytu

    def get_BDFfile(self):   
        try:
            self.BDF_filename, _ = QFileDialog.getOpenFileName(self, 'Choose BDF file', self.my_folder, "BDF files (*.bdf)")
            result = re.findall(r'[^//]+', self.BDF_filename)
            self.BDFButton.setText(f"Wybrano \n {result[-1]}")
            self.append_text(f"Wybrano {result[-1]} ")

            # Sprawdź, czy nazwy plików BDF i Excel są takie same przed aktywowaniem create_parser
            if self.are_files_selected():
                if self.check_filenames():
                    self.create_parser()
                else:
                    QMessageBox.warning(self,'Ostrzeżenie','Nazwy plików BDF i Excel są różne. Wybierz pliki o takich samych nazwach.',QMessageBox.Ok)
        except:
            pass

    def get_XLSXfile(self):   
        try:
            self.excel_filename, _ = QFileDialog.getOpenFileName(self, 'Choose Excel file', self.my_folder, "Excel files (*.xlsx)")
            result = re.findall(r'[^//]+', self.excel_filename)
            self.ExcelButton.setText(f"Wybrano \n {result[-1]}")
            self.append_text(f"Wybrano {result[-1]} ")

            # Sprawdź, czy nazwy plików BDF i Excel są takie same przed aktywowaniem create_parser
            if self.are_files_selected():
                if self.check_filenames(): 
                    self.create_parser()
                else:
                    QMessageBox.warning(self,'Ostrzeżenie','Nazwy plików BDF i Excel są różne. Wybierz pliki o takich samych nazwach.',QMessageBox.Ok)
        except:
            pass

    def check_filenames(self):
        # Sprawdź, czy nazwy plików BDF i Excel są takie same
        if self.BDF_filename and self.excel_filename:
            bdf_name = os.path.splitext(self.BDF_filename)[0]
            excel_name = os.path.splitext(self.excel_filename)[0]
            print(bdf_name,excel_name)
            return bdf_name == excel_name
        return False

    def are_files_selected(self):
        return self.BDF_filename is not None and self.excel_filename is not None
 
    def create_parser(self):
        self.append_text('Rozpoczynam konwersję')
        self.EsatanParser = Parser(self.BDF_filename, self.excel_filename)
        self.append_text(f'Pomyślnie stworzono plik "{self.EsatanParser.get_file_name()}.erg"')
        self.BDF_filename = None
        self.excel_filename = None

    def copy_files(self):
        pass

    def test_ERG(self):
        pass

    def select_folder(self):
        self.esatan_folder = QFileDialog.getExistingDirectory(self, 'Wybierz folder')
        if self.esatan_folder:
            nazwa_folderu = re.findall(r'[^//]+',self.esatan_folder)
            self.EsatanButton.setText(f'Wybrany folder:\n{nazwa_folderu[-1]}')
            self.append_text(f"Wybrano folder {self.esatan_folder}")

    def confirm_remove_workbench(self):
        if hasattr(self, 'esatan_folder'):
            try:
                workbench_folder = os.path.join(self.esatan_folder, '00_WORKBENCH')
                gmm_folder = os.path.join(self.esatan_folder, '01_GMM')

                if os.path.exists(workbench_folder):
                    result = QMessageBox.question(
                        self,
                        'Potwierdzenie',
                        'Czy na pewno chcesz usunąć wszystko z folderu Workbench?',
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if result == QMessageBox.Yes:
                        self.deleteButton.setText('Usunięto pliki')
                        self.delete_workbench_contents(workbench_folder)
                        self.delete_out_files_in_01_GMM(gmm_folder)
            except OSError as e:
                if e.errno == 32:
                    self.append_text("Plik jest obecnie używany. Proszę zamknąć wszystkie foldery  pliki.")

    def delete_workbench_contents(self, folder):
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except OSError as e:
                    if e.errno == 32:
                        self.append_text("Plik jest obecnie używany. Proszę zamknąć wszystkie foldery  pliki.")

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    os.rmdir(dir_path)
                except OSError as e:
                    if e.errno == 32:
                        self.append_text("Plik jest obecnie używany. Proszę zamknąć wszystkie foldery  pliki.")

    def delete_out_files_in_01_GMM(self,folder):
        if hasattr(self, 'esatan_folder'):
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if file.endswith(".out"):
                            file_path = os.path.join(root, file)
                            try:
                                os.remove(file_path)
                            except OSError as e:
                                if e.errno == 32:
                                   self.append_text("Plik jest obecnie używany. Proszę zamknąć wszystkie foldery  pliki.")

    def clear_console(self):
        self.text_edit.clear()

    def append_text(self, text):
        self.text_edit.append(text)

    def get_ERGfile(self):
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Wybierz plik", self.my_folder, "Pliki (*.erg)")
            if file_path:
                self.create_batch_file(file_path)

    def create_batch_file(self, file_path):
        batch_content = '''@echo off
                            echo Hello, World!
                            pause'''
        # Nazwa pliku batch
        batch_file_name = 'hello_world.bat'

        with open(batch_file_name, "w") as batch_file:
            batch_file.write(batch_content)

        self.append_text(f"Utworzono plik batch: {batch_file_name}")


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    ui.append_text("**FEMAP-ESATAN PARSER 2023**\nOprogramowane konwertujące")
    sys.exit(app.exec_())