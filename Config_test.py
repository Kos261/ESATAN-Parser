from configparser import ConfigParser

import os
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QDir, Qt, QCoreApplication
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QTextEdit,QStyleFactory
from PyQt5.QtGui import QPalette, QColor
import re

class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui,self).__init__(*args,**kwargs)
        print("Czy chcesz wznowić ostatnią sesję?")
        # self.my_folder = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER" #Tutaj zmienić na home
        # self.two_files_selected = False
        # self.BDF_filename = None
        # self.excel_filename = None
        # self.esrdg_path = None
        # self.gmm_folder = None
        # self.submodels_folder = None
        # self.workbench_folder = None
        # self.new_file_created = False                                            
        # self.last_erg_file = None                               
        # self.last_erg_file_path = None
        self.config_load()
        self.button_size = 150
        

        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget) 
        self.setWindowTitle('Config test')
        self.ButtonContainer = QtWidgets.QGridLayout()
        self.ButtonContainer = QHBoxLayout(self.widget)

        self.EsatanButton = QtWidgets.QPushButton(self.widget)
        self.EsatanButton.setText("Wybierz folder z\nmodelami")
        self.EsatanButton.setFixedSize(self.button_size, self.button_size)
        self.EsatanButton.clicked.connect(self.select_models_folder)
        self.ButtonContainer.addWidget(self.EsatanButton)

        self.DefaultButton = QtWidgets.QPushButton(self.widget)
        self.DefaultButton.setText("Ustawienia domyślne")
        self.DefaultButton.setFixedSize(self.button_size, self.button_size)
        self.DefaultButton.clicked.connect(self.select_models_folder)
        self.ButtonContainer.addWidget(self.DefaultButton)

    def select_models_folder(self):
        self.models_folder = QFileDialog.getExistingDirectory(self, 'Wybierz folder')
        if self.models_folder:
            nazwa_folderu = re.findall(r'[^//]+',self.models_folder)
            self.EsatanButton.setText(f'Wybrany folder:\n{nazwa_folderu[-1]}')
            try:
                self.workbench_folder = os.path.join(self.models_folder, '00_WORKBENCH')
                self.workbench_folder = self.zamien_ukosniki(self.workbench_folder,'\\')

                self.gmm_folder = os.path.join(self.models_folder, '01_GMM')
                self.gmm_folder = self.zamien_ukosniki(self.gmm_folder,'\\')

                self.submodels_folder = self.gmm_folder + "\\02_SUBMODELS"


            except OSError as e:
                if e.errno == 32:
                    print("Plik jest obecnie używany. Proszę zamknąć wszystkie foldery i pliki.")

    def zamien_ukosniki(self, adres_pliku, znak_zamiany):
        # Zamienia wszystkie ukośniki na wybrany znak zamiany
        nowy_adres = adres_pliku.replace('/', znak_zamiany)
        return nowy_adres

    def config_load(self):
        file = 'configDefault.ini'
        self.config = ConfigParser()
        self.config.read(file)
        ustawienia = list(self.config['path settings'])
        
        for i in range(len(ustawienia)):
            print(f"{ustawienia[i]} = {self.config['path settings'][ustawienia[i]]}")

    def config_save(self):
        Lastconfig = self.config
        Lastconfig.set('path settings',)
        self.my_folder = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER"
        self.two_files_selected = False
        self.BDF_filename = None
        self.excel_filename = None
        self.esrdg_path = None
        self.gmm_folder = None
        self.submodels_folder = None
        self.workbench_folder = None
        self.new_file_created = False                                            
        self.last_erg_file = None                               
        self.last_erg_file_path = None


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())