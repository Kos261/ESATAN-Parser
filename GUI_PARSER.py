import sys
import re
import time
import os
import shutil

from PARSER import Parser,Point,Triangle,Rectangle
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QDir, Qt, QCoreApplication
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QTextEdit,QStyleFactory
from PyQt5.QtGui import QPalette, QColor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler





class Ui(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui,self).__init__(*args,**kwargs)
        self.my_folder = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER" #Tutaj zmienić na home
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
        self.button_size = 150
        self.setFixedSize(1300, 800)

        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget) 
        self.setWindowTitle('FEMAP - ESATAN PARSER')
        self.ButtonContainer = QtWidgets.QGridLayout()
        self.main_layout = QHBoxLayout(self.widget)

        
        self.darkMode()
        self.createButtons()
        self.esrdg_finder()

        self.main_layout.addLayout(self.ButtonContainer)
        self.main_layout.addWidget(self.text_edit)

    def darkMode(self):
        # Tworzenie ciemnego motywu
        self.dark_palette = QPalette()
        self.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.WindowText, Qt.white)
        self.dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ButtonText, Qt.white)
        self.dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        self.dark_palette.setColor(QPalette.Text, Qt.white)
        self.dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        self.dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Ustawianie ciemnego motywu
        self.setPalette(self.dark_palette)

        # Ustawianie ciemnego stylu
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def createButtons(self):
        ###TWORZYMY WIDGETY I USTAWIAMY JE###
        
        self.EsatanButton = QtWidgets.QPushButton(self.widget)
        self.EsatanButton.setText("Wybierz folder z\nmodelami")
        self.EsatanButton.setFixedSize(self.button_size, self.button_size)
        self.EsatanButton.clicked.connect(self.select_models_folder)
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
        self.copyButton.setText("Wybierz folder z\nplikiem esrdg.bat")
        self.copyButton.clicked.connect(self.esrdg_finder_manual)
        self.copyButton.setFixedSize(self.button_size, self.button_size)
        self.ButtonContainer.addWidget(self.copyButton, 1, 0)

        self.deleteButton = QtWidgets.QPushButton(self.widget)
        self.deleteButton.setText("Usuń stare pliki")
        self.deleteButton.clicked.connect(self.confirm_remove_workbench)
        self.deleteButton.setFixedSize(self.button_size, self.button_size)
        self.ButtonContainer.addWidget(self.deleteButton, 1, 1)

        self.testButton = QtWidgets.QPushButton(self.widget)
        self.testButton.setText("Test BAT")
        self.testButton.clicked.connect(self.test_ERG)
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
            self.BDFButton.setStyleSheet("background-color: green;")
            QCoreApplication.processEvents()
            # Sprawdź, czy nazwy plików BDF i Excel są takie same przed aktywowaniem create_parser
            if self.are_files_selected():
                if self.check_filenames():
                    self.create_parser()
                else:
                    self.BDFButton.setStyleSheet("background-color: red;")
                    QMessageBox.warning(self,'Ostrzeżenie','Nazwy plików BDF i Excel są różne. Wybierz pliki o takich samych nazwach.',QMessageBox.Ok)
        except:
            pass

    def get_XLSXfile(self):   
        try:
            self.excel_filename, _ = QFileDialog.getOpenFileName(self, 'Choose Excel file', self.my_folder, "Excel files (*.xlsx)")
            result = re.findall(r'[^//]+', self.excel_filename)
            self.ExcelButton.setText(f"Wybrano \n {result[-1]}")
            self.append_text(f"Wybrano {result[-1]} ")
            self.ExcelButton.setStyleSheet("background-color: green;")
            QCoreApplication.processEvents()
            # Sprawdź, czy nazwy plików BDF i Excel są takie same przed aktywowaniem create_parser
            if self.are_files_selected():
                if self.check_filenames(): 
                    self.create_parser()
                else:
                    self.ExcelButton.setStyleSheet("background-color: red;")
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
        QCoreApplication.processEvents()
        self.EsatanParser = Parser(self.BDF_filename, self.excel_filename)
        self.append_text(f'Pomyślnie stworzono plik "{self.EsatanParser.get_file_name()}.erg"')
        self.znajdz_ostatni_erg(self.my_folder)
        self.BDFButton.setStyleSheet(self.dark_palette)
        self.ExcelButton.setStyleSheet(self.dark_palette)   #Tu chcę z powrotem szary

        # self.last_erg_file = self.EsatanParser.get_file_name()
        # self.last_erg_file_path = os.path.join(self.my_folder, self.last_erg_file)
        self.new_file_created = True
        self.BDF_filename = None
        self.excel_filename = None

    def select_models_folder(self):
        self.models_folder = QFileDialog.getExistingDirectory(self, 'Wybierz folder')
        if self.models_folder:
            nazwa_folderu = re.findall(r'[^//]+',self.models_folder)
            self.EsatanButton.setText(f'Wybrany folder:\n{nazwa_folderu[-1]}')
            self.append_text(f"Wybrano folder {self.models_folder}")
            try:
                self.workbench_folder = os.path.join(self.models_folder, '00_WORKBENCH')
                self.workbench_folder = self.zamien_ukosniki(self.workbench_folder,'\\')
                self.append_text("\nFolder WORKBENCH\n" + self.workbench_folder)

                self.gmm_folder = os.path.join(self.models_folder, '01_GMM')
                self.gmm_folder = self.zamien_ukosniki(self.gmm_folder,'\\')
                self.append_text("\nFolder GMM\n" + self.gmm_folder)

                self.submodels_folder = self.gmm_folder + "\\02_SUBMODELS"
                self.append_text("\nFolder SUBMODELS\n" + self.submodels_folder)


            except OSError as e:
                if e.errno == 32:
                    self.append_text("Plik jest obecnie używany. Proszę zamknąć wszystkie foldery i pliki.")

    def confirm_remove_workbench(self):
        if hasattr(self, 'models_folder'):
            try:
                if os.path.exists(self.workbench_folder):
                    result = QMessageBox.question(
                        self,
                        'Potwierdzenie',
                        'Czy na pewno chcesz usunąć wszystko z folderu Workbench?',
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if result == QMessageBox.Yes:
                        self.deleteButton.setText('Usunięto pliki')
                        self.delete_workbench_contents(self.workbench_folder)
                        self.delete_out_files_in_01_GMM(self.gmm_folder)
            except OSError as e:
                if e.errno == 32:
                    self.append_text("Plik jest obecnie używany. Proszę zamknąć wszystkie foldery i pliki.")

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
        if hasattr(self, 'models_folder'):
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

    def zamien_ukosniki(self, adres_pliku, znak_zamiany):
        # Zamienia wszystkie ukośniki na wybrany znak zamiany
        nowy_adres = adres_pliku.replace('/', znak_zamiany)
        return nowy_adres

    #FUNKCJE DO TESTOWANIA ERGA
    
    def esrdg_finder(self):
        nazwa_pliku = "esrdg.bat"
        esrdg_folder = r'C:\ESATAN-TMS\2018sp1\Radiative\bin'
        for root, dirs, files in os.walk(esrdg_folder):
            try:
                if nazwa_pliku in files:
                    self.esrdg_path = os.path.join(root, nazwa_pliku)
                    self.append_text(f"\nZnaleziono {nazwa_pliku} " + self.esrdg_path + "\n")
                    return self.esrdg_path
            except:
                self.append_text(f"\nNie można znaleźć pliku {nazwa_pliku}\nProszę wyszukać ręcznie")
        return None
    
    def esrdg_finder_manual(self):
        nazwa_pliku = "esrdg.bat"
        esrdg_folder = QFileDialog.getExistingDirectory(self, 'Wybierz folder')
        for root, dirs, files in os.walk(esrdg_folder):
            try:
                if nazwa_pliku in files:
                    self.esrdg_path = os.path.join(root, nazwa_pliku)
                    self.append_text(f"\nZnaleziono {nazwa_pliku} " + self.esrdg_path + "\n")
                    return self.esrdg_path
            except:
                self.append_text("\nNie ma takiego pliku\n")
        return None
    
    def test_ERG(self):
        if not self.last_erg_file:
            #Nie ma nowego pliku - biorę ostatni
            self.znajdz_ostatni_erg(self.my_folder)
            self.append_text(f"\nOstatni plik .erg {self.last_erg_file}\n")

        if self.gmm_folder and self.last_erg_file:
            #Wybrano folder z modelami i utworzono ostatnio plik
            self.przenies_ostatni_erg()
            #self.create_batch_file()
        else:
            #Nie wybrano folderu z modelammi lub nie ma ostatnio żadnego pliku
            self.append_text(f"\nFolder GMM:{self.gmm_folder}\nOstatni plik: {self.last_erg_file}\n")
            self.append_text("\nNie utworzono pliku albo nie znaleziono folderu z modelami\n")

    def znajdz_ostatni_erg(self, folder_programu):
            self.append_text("\nSzukam ostatniego pliku .erg\n")
            lista_plikow = [f for f in os.listdir(folder_programu) if f.endswith(".erg")]
            if lista_plikow:
                self.last_erg_file = max(lista_plikow, key=lambda x: os.path.getctime(os.path.join(folder_programu, x)))
                self.append_text(self.last_erg_file)
                self.last_erg_file_path = os.path.join(folder_programu, self.last_erg_file)

    def przenies_ostatni_erg(self):
        if self.last_erg_file_path:
            if os.path.exists(self.submodels_folder+'\\'+self.last_erg_file):
                self.append_text(self.submodels_folder+'\\'+self.last_erg_file)
                result = QMessageBox.question(self,'Potwierdzenie','Czy na pewno chcesz zastąpić stary model nowym?',QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
                if result == QMessageBox.Yes:
                    os.remove(self.submodels_folder + '\\' + self.last_erg_file)
                    shutil.move(self.last_erg_file_path,self.submodels_folder)
            else:
                self.append_text("Nie ma starego pliku")
                shutil.move(self.last_erg_file_path,self.submodels_folder)
                self.append_text(f"\nPlik {self.last_erg_file} przeniesiony do: {self.submodels_folder}\n")
                self.testButton.setEnabled(False)
        else:
            self.append_text("Nie znaleziono plików .erg do przeniesienia.")
            
    def create_batch_file(self):

        batch_content = f'''
set\tPFAD_GMM={self.gmm_folder}\\

rem call submodels
call {self.esrdg_path} < %PFAD_GMM%02_SUBMODELS\{self.last_erg_file} >      %PFAD% {self.last_erg_file.split('.')[0]+'.out'}
rem assemble model from module *.erg files
call {self.esrdg_path} < %PFAD_GMM%Test_subj_1.erg >       %PFAD%99_Test_all.out

pause
'''
        # Nazwa pliku batch
        batch_file_name = os.path.join(self.gmm_folder, 'Test_subj_1.bat')

        with open(batch_file_name, "w") as batch_file:
            batch_file.write(batch_content)

        self.append_text(f"\n***Utworzono plik batch: {batch_file_name}***\n")


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    ui.append_text("**FEMAP-ESATAN PARSER 2023**\nOprogramowane konwertujące")
    sys.exit(app.exec_())