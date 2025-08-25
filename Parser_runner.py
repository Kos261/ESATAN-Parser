
if __name__ == '__main__':

    from src.PARSER import ERG_Parser
    from src.GUI import Ui
    from PyQt5 import QtWidgets
    import sys    
    
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())
    
    


    '''
    uv run pyinstaller .\Parser_runner.py `
    -F --windowed --name ESATAN_Parser `
    --distpath .\build\out --workpath .\build\.work --specpath . `
    --noconfirm --clean `
    --hidden-import PyQt5.sip `
    --collect-all PyQt5 `
    --icon "$PWD\assets\PARSER.ico"
    '''