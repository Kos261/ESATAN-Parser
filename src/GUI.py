import io, traceback, contextlib, sys, re, os, shutil
from pathlib import Path


from src.PARSER import ERG_Parser
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication, QSettings
from PyQt5.QtWidgets import (
    QApplication, 
    QPushButton, 
    QFileDialog, 
    QHBoxLayout, 
    QMessageBox, 
    QTextEdit,
    QLineEdit,
    QStyleFactory
    )
from PyQt5.QtGui import QPalette, QColor
from configparser import ConfigParser




class Ui(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(Ui,self).__init__(*args,**kwargs)
        self.settings = QSettings("CBK", "Esatan-Parser")
        self.init_state() # Only attributes
        self.setup_ui()   # Only creating widgets
        self.connect_signals()
        # self.load_config()
        
    def init_state(self):
        self.two_files_selected = False
        self.BDF_filename = None
        self.excel_filename = None
        self.app_dir = getattr(self, "app_dir", str(Path.cwd()))
        self.outputdir = self.settings.value("output/dir", self.app_dir, type=str)

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

    def setup_ui(self):
        self.setFixedSize(800, 400) 
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.setWindowTitle("FEMAP - ESATAN PARSER")
        self.button_size = 150
         
        self.BDFButton = QtWidgets.QPushButton()
        self.BDFButton.setText("Plik BDF")
        self.BDFButton.setFixedSize(self.button_size, self.button_size)

        self.ExcelButton = QtWidgets.QPushButton()
        self.ExcelButton.setText("Plik Excel")
        self.ExcelButton.setFixedSize(self.button_size, self.button_size)

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

        self.ButtonContainer = QtWidgets.QGridLayout()
        self.ButtonContainer.addWidget(self.BDFButton, 0, 0)
        self.ButtonContainer.addWidget(self.ExcelButton, 0, 1)
       
        left_panel = QtWidgets.QVBoxLayout()
        left_panel.addLayout(self.ButtonContainer)

        row = QtWidgets.QHBoxLayout()
        self.out_lineedit = QLineEdit()
        self.out_lineedit.setPlaceholderText(self.outputdir)
        self.outButton = QtWidgets.QPushButton()
        self.outButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon))
        # self.outButton.setText("Output")
        self.outButton.setFixedWidth(50)
        row.addWidget(self.out_lineedit, 1)
        row.addWidget(self.outButton, 0)
        left_panel.addLayout(row)


        main_layout = QtWidgets.QHBoxLayout(self.widget)
        main_layout.addLayout(left_panel)
        main_layout.addWidget(self.console)
        self.widget.setLayout(main_layout)

        self.darkMode()

    def connect_signals(self):
        self.ExcelButton.clicked.connect(self.get_XLSXfile)
        self.BDFButton.clicked.connect(self.get_BDFfile)
        self.outButton.clicked.connect(self.choose_outputdir)
        self.out_lineedit.editingFinished.connect(self._persist_outdir)
        
    def _start_dir(self, key):
        return self.settings.value(key, self.app_dir)

    def _persist_outdir(self):
        self.outputdir = self.out_lineedit.text().strip()
        self.settings.setValue("output/dir", self.outputdir)

    def choose_outputdir(self):
        start = self.settings.value("output/dir", self.app_dir, type=str)
        d = QFileDialog.getExistingDirectory(self, "Wybierz folder wyjściowy", start)
        if d:
            self.outputdir = d
            self.out_lineedit.setText(d)  

    def get_BDFfile(self):   
        start_dir = self._start_dir("lastDir/bdf")
        fname, _ = QFileDialog.getOpenFileName(self, 'Choose BDF file', start_dir, "BDF files (*.bdf)")

        if not fname:
            return
        
        p = Path(fname)
        self.settings.setValue("lastDir/bdf", str(p.parent))
        self.BDF_filename = str(p)
        self.BDFButton.setText(f"Wybrano \n {p.name}")
        self.append_text(f"Wybrano {p.name} ")
        self.BDFButton.setStyleSheet("background-color: green;")
        QCoreApplication.processEvents()

        if self.are_files_selected():
            
            if self.check_filenames():
                self.create_parser()
            
            else:
                self.BDFButton.setStyleSheet("background-color: red;")
                QMessageBox.warning(self, "Warning!", "Different names!", QMessageBox.Ok)

    def get_XLSXfile(self):   
        start_dir = self._start_dir("lastDir/xlsx")
        fname, _ = QFileDialog.getOpenFileName(self, 'Choose Excel file', start_dir, "Xlsx files (*.xlsx)")

        if not fname:
            return
        
        p = Path(fname)
        self.settings.setValue("lastDir/xlsx", str(p.parent))
        self.excel_filename = str(p)
        self.ExcelButton.setText(f"{p.name}")
        self.append_text(f"Chosen {p.name} ")
        self.ExcelButton.setStyleSheet("background-color: green;")
        QCoreApplication.processEvents()

        if self.are_files_selected():
            
            if self.check_filenames():
                self.create_parser()
            
            else:
                self.ExcelButton.setStyleSheet("background-color: red;")
                QMessageBox.warning(self, "Warning!", "Different names!", QMessageBox.Ok)

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
        self.outputdir = self.out_lineedit.text().strip() or self.outputdir
        self.settings.setValue("output/dir", self.outputdir)
        Path(self.outputdir).mkdir(parents=True, exist_ok=True)

        if self.outputdir == '':
           self.parser = ERG_Parser()
           
        else:
            self.parser = ERG_Parser(self.outputdir)
        
        
        self.append_text('🔄 Starting conversion…')
        QCoreApplication.processEvents()

        buf = io.StringIO()                           # bufor for stdout/stderr
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                self.parser.merge_files_into_ERG(self.BDF_filename, self.excel_filename)

            self.append_text(buf.getvalue())          # co wypisał parser
            self.append_text(f'✅ Successfully created {self.parser.get_file_name(self.BDF_filename)}.erg')
        
        except Exception:
            self.append_text('❌ Error:\n' + traceback.format_exc())
            QMessageBox.critical(self, 'Parser error', 'Conversion aborted')

    def append_text(self, text):
        self.console.append(text)

    def closeEvent(self, event):
        result = self.confirmCloseDialog()
        if result:
            # self.config_save()
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



if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())

    # pyinstaller src/GUI.py  -F --windowed --name ESATAN_Parser --add-data "src;src" 