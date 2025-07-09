from src import PARSER, GUI_PARSER
from src.PARSER import Parser

if __name__ == '__main__':
    
    excelfile = "Example excel path"
    bdffile = "Example bdf path"

    parser = Parser()
    parser.merge_files_into_ERG(bdffile=bdffile, excelfile=excelfile)