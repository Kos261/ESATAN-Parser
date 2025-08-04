import io, traceback, contextlib, sys, re, os, shutil
from pathlib import Path


from src.PARSER import ERG_Parser
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import (
    QApplication, 
    QPushButton, 
    QFileDialog, 
    QHBoxLayout, 
    QMessageBox, 
    QTextEdit,
    QStyleFactory
    )
from PyQt5.QtGui import QPalette, QColor
from configparser import ConfigParser




class Ui(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(Ui,self).__init__(*args,**kwargs)
        
        self.my_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        # self.my_folder = Path(__file__).parent.resolve()
        self.createButtons()
        self.load_config()
        self.two_files_selected = False
        self.BDF_filename = None
        self.excel_filename = None
        self.setFixedSize(800, 400) 
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.setWindowTitle("FEMAP - ESATAN PARSER")

        # main_layout = QHBoxLayout(self.widget)

        
        self.ButtonContainer = QtWidgets.QGridLayout()
        self.ButtonContainer.addWidget(self.BDFButton, 0, 0)
        self.ButtonContainer.addWidget(self.ExcelButton, 0, 1)
       

        left_panel = QtWidgets.QVBoxLayout()
        left_panel.addLayout(self.ButtonContainer)
        left_panel.addWidget(self.out_type)
    
        main_layout = QtWidgets.QHBoxLayout(self.widget)
        main_layout.addLayout(left_panel)
        main_layout.addWidget(self.console)
        self.widget.setLayout(main_layout)

        self.darkMode()

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
        self.button_size = 150
         
        self.BDFButton = QtWidgets.QPushButton()
        self.BDFButton.setText("Plik BDF")
        self.BDFButton.setFixedSize(self.button_size, self.button_size)
        self.BDFButton.clicked.connect(self.get_BDFfile)

        self.ExcelButton = QtWidgets.QPushButton()
        self.ExcelButton.setText("Plik Excel")
        self.ExcelButton.setFixedSize(self.button_size, self.button_size)
        self.ExcelButton.clicked.connect(self.get_XLSXfile)

        self.console = QTextEdit()
        font = self.console.currentFont()
        font.setPointSize(13)
        self.console.setFont(font)
        self.console.setReadOnly(True)
        self.append_text(
            '<span style="color:#03a9f4; font-weight:bold;">🌡️ FEMAP Nastran – ESATAN Parser 2025</span><br>'
            '<span style="color:#8bc34a;">📐 BDF file → ERG Converter</span><br>'
            '<span style="color:#9e9e9e; font-size:10pt;">© 2025 Konstanty Kłosiewicz CBK • MIT License</span>'
        )

        self.out_type = QTextEdit()
        self.out_type.setPlaceholderText("Type output directory")
        font = self.out_type.currentFont()
        font.setPointSize(13)
        self.out_type.setFont(font)
        self.out_type.setFixedHeight(40)

        # self.clear_button = QPushButton("Clear\nconsole")
        # self.clear_button.clicked.connect(self.clear_console)
        # self.clear_button.setFixedSize(self.button_size, self.button_size)
        # self.ButtonContainer.addWidget(self.clear_button,2,0)


    def get_BDFfile(self):   
        try:
            self.BDF_filename, _ = QFileDialog.getOpenFileName(self, 'Choose BDF file', self.my_folder, "BDF files (*.bdf)")
            
            if self.BDF_filename != None and self.BDF_filename !='':
                result = re.findall(r'[^//]+', self.BDF_filename)
                self.BDFButton.setText(f"Wybrano \n {result[-1]}")
                self.append_text(f"Wybrano {result[-1]} ")
                self.BDFButton.setStyleSheet("background-color: green;")
                QCoreApplication.processEvents()
                
                if self.are_files_selected():
                    if self.check_filenames():
                        self.create_parser()
                    else:
                        self.BDFButton.setStyleSheet("background-color: red;")
                        QMessageBox.warning(self,'Warning!','Different names!',QMessageBox.Ok)

        except (FileNotFoundError, IOError):
            self.append_text("Wrong file or file path")

    def get_XLSXfile(self):   
        try:
            self.excel_filename, _ = QFileDialog.getOpenFileName(self, 'Choose Excel file', self.my_folder, "Excel files (*.xlsx)")

            if self.excel_filename != None and self.excel_filename !='':
                result = re.findall(r'[^//]+', self.excel_filename)
                self.ExcelButton.setText(f"Wybrano \n {result[-1]}")
                self.append_text(f"Wybrano {result[-1]} ")
                self.ExcelButton.setStyleSheet("background-color: green;")
                QCoreApplication.processEvents()
                
                if self.are_files_selected():
                    if self.check_filenames(): 
                        self.create_parser()
                    else:
                        self.ExcelButton.setStyleSheet("background-color: red;")
                        QMessageBox.warning(self,'Warning!','Different names!',QMessageBox.Ok)

        except:
            pass

    def check_filenames(self):
        #Czy w ogóle
        # Sprawdź, czy nazwy plików BDF i Excel są takie same
        if self.BDF_filename and self.excel_filename:
            bdf_name = os.path.splitext(self.BDF_filename)[0]
            excel_name = os.path.splitext(self.excel_filename)[0]
            return bdf_name == excel_name
        else:
            return False

    def are_files_selected(self):
        return self.BDF_filename is not None and self.excel_filename is not None
 
    def create_parser(self):
        self.outputdir = self.out_type.toPlainText()
        if self.outputdir == '':
           self. parser = ERG_Parser()
        else:
            parser = ERG_Parser(self.outputdir)
        
        
        self.append_text('🔄 Start konwersji…')
        QCoreApplication.processEvents()

        buf = io.StringIO()                           # bufor na stdout/stderr
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                parser.merge_files_into_ERG(self.BDF_filename, self.excel_filename)

            self.append_text(buf.getvalue())          # co wypisał parser
            self.append_text(f'✅ Utworzono {parser.get_file_name(self.BDF_filename)}.erg')
        except Exception:
            self.append_text('❌ Błąd:\n' + traceback.format_exc())
            QMessageBox.critical(self, 'Błąd parsera', 'Konwersja nie powiodła się')

    def clear_console(self):
        self.console.clear()

    def append_text(self, text):
        self.console.append(text)

    def replace_slash(self, adres_pliku, znak_zamiany):
        # Zamienia wszystkie ukośniki na wybrany znak zamiany
        nowy_adres = adres_pliku.replace('/', znak_zamiany)
        return nowy_adres

    #ZAMYKANIE I ZAPISYWANIE USTAWIEŃ

    def closeEvent(self, event):
        result = self.confirmCloseDialog()
        if result:
            self.config_save()
            event.accept()  
        else:
            event.ignore()

    def confirmCloseDialog(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Potwierdzenie zamknięcia")
        msg_box.setText("Czy na pewno chcesz zamknąć program?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        result = msg_box.exec_()

        return result == QMessageBox.Yes

    def load_config(self):
        files = [f for f in os.listdir(self.my_folder) if f.endswith(".ini")]
        if 'configLast.ini' in files:
            self.config_load_file('configLast.ini') 
        else:
            self.default_settings()

    def config_save(self):
        file = 'configLast.ini'
        configLast = ConfigParser()
        configLast.add_section('path settings')                                    
        configLast.set('path settings','self.outputdir', 'None')                               

        with open(file,'w') as configfile:
            configLast.write(configfile)

    def config_load_file(self,file):
        self.config = ConfigParser()
        self.config.read(file)
        self.outputdir = self.config['path settings']['self.outputdir']
        if not self.outputdir:
            self.znajdz_ostatni_erg(self.my_folder)

        if file != 'configDefault.ini':
            self.append_text(f"OUTPUTDIR: {self.outputdir}")
            self.append_text("\n***POPRZEDNIA SESJA***\n")
        
    def default_settings(self):
        text = '''[path settings]                              
self.outputdir = None
'''
        with open('configDefault.ini','w') as file:
            file.write(text)
        self.config_load_file('configDefault.ini')

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())

    # pyinstaller GUI.py  -F --windowed --name ESATAN_Parser --add-data "src;src" 