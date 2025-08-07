from src.PARSER import ERG_Parser
from src.GUI import Ui
from PyQt5 import QtWidgets


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())
    
    '''
    pyinstaller Parser_runner.py `
    -F --windowed --name ESATAN_Parser `
    --distpath build\out `
    --workpath build\.work `
    --specpath build `
    --noconfirm --clean `
    --icon=logo.ico
    '''