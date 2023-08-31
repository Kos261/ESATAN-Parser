import sys
import re
import time
import os
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PARSER import Parser,Point,Triangle,Rectangle



class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui,self).__init__(*args,**kwargs)
        self.two_files_selected = False
        self.BDF_filename = None
        self.excel_filename = None

        button_size = 150
        self.setWindowTitle('PARSER')
        self.setFixedSize(900, 600)
        gridLayout = QtWidgets.QGridLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(gridLayout)         
        self.setCentralWidget(widget)    

        ###TWORZYMY WIDGETY I USTAWIAMY JE###
        
        self.EsatanButton = QtWidgets.QPushButton(widget)
        self.EsatanButton.setText("Wybierz folder\nEsatana")
        self.EsatanButton.setFixedSize(button_size, button_size)
        self.EsatanButton.clicked.connect(self.select_folder)
        gridLayout.addWidget(self.EsatanButton, 0, 2)
         
        self.BDFButton = QtWidgets.QPushButton(widget)
        self.BDFButton.setText("Plik BDF")
        self.BDFButton.setFixedSize(button_size, button_size)
        self.BDFButton.clicked.connect(self.get_BDFfile)
        gridLayout.addWidget(self.BDFButton, 0, 0)

        self.ExcelButton = QtWidgets.QPushButton(widget)
        self.ExcelButton.setText("Plik Excel")
        self.ExcelButton.setFixedSize(button_size, button_size)
        self.ExcelButton.clicked.connect(self.get_XLSXfile)
        gridLayout.addWidget(self.ExcelButton, 0, 1)

        self.copyButton = QtWidgets.QPushButton(widget)
        self.copyButton.setText("Skopiuj pliki")
        self.copyButton.clicked.connect(self.copy_files)
        self.copyButton.setFixedSize(button_size, button_size)
        gridLayout.addWidget(self.copyButton, 1, 0)

        self.deleteButton = QtWidgets.QPushButton(widget)
        self.deleteButton.setText("Usuń stare pliki")
        self.deleteButton.clicked.connect(self.confirm_remove_files)
        self.deleteButton.setFixedSize(button_size, button_size)
        gridLayout.addWidget(self.deleteButton, 1, 1)

        self.testButton = QtWidgets.QPushButton(widget)
        self.testButton.setText("Test BAT")
        #self.testButton.clicked.connect(self.Test)
        self.testButton.setFixedSize(button_size, button_size)
        gridLayout.addWidget(self.testButton, 1, 2)

    def get_BDFfile(self):   
        try:       
            self.BDF_filename, _ = QFileDialog.getOpenFileName(self, 'Choose BDF file', r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER", "BDF files (*.bdf)")
        except:
            pass
        result = re.findall(r'[^//]+',self.BDF_filename)
        self.BDFButton.setText(f"Wybrano \n {result[-1]}")

        if self.are_files_selected():
            self.create_parser()

    def get_XLSXfile(self):   
        try:       
            self.excel_filename, _ = QFileDialog.getOpenFileName(self, 'Choose Excel file', r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER", "Excel files (*.xlsx)")
        except:
            pass
        result = re.findall(r'[^//]+',self.excel_filename)
        self.ExcelButton.setText(f"Wybrano \n {result[-1]}")

        if self.are_files_selected():
            self.create_parser()

    def create_parser(self):
        time.sleep(5)
        self.EsatanParser = Parser(self.BDF_filename, self.excel_filename)
        self.BDF_filename = None
        self.excel_filename = None

    def are_files_selected(self):
        return self.BDF_filename is not None and self.excel_filename is not None
    
    def copy_files(self):
        pass

    def test_ERG(self):
        pass

    def select_folder(self):
        self.esatan_folder = QFileDialog.getExistingDirectory(self, 'Wybierz folder')
        if self.esatan_folder:
            nazwa_folderu = re.findall(r'[^//]+',self.esatan_folder)
            self.EsatanButton.setText(f'Wybrany folder:\n{nazwa_folderu[-1]}')
    
    def confirm_remove_files(self):
        if hasattr(self, 'esatan_folder'):
            result = QMessageBox.question(
                self,
                'Potwierdzenie',
                'Czy na pewno chcesz usunąć pliki z 00_WORKBENCH?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if result == QMessageBox.Yes:
                self.remove_files()

    def remove_files(self):
        if hasattr(self, 'esatan_folder'):
            workbench_folder = os.path.join(self.esatan_folder, '00_WORKBENCH')
            if os.path.exists(workbench_folder):
                self.delete_files_in_folder(workbench_folder)
                self.deleteButton.setText('Usunięto pliki z\n"00_WORKBENCH"')
            else:
                self.deleteButton.setText('Folder "00_WORKBENCH"\nnie istnieje')

    def delete_files_in_folder(self, folder):
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file) 
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Nie udało się usunąć pliku {file_path}: {e}")


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())