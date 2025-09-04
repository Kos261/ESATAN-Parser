import argparse
import sys
from src.PARSER import ERG_Parser

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Esatan-Parser',
                    description='This is converter combining geometry made in BDF format and hierarchy of elements from excel file. The result is .erg file compatibile with ESATAN for thermal analysis',
                    epilog='')
    
    parser.add_argument('-bdf', '--bdf')   
    parser.add_argument('-xlsx', '--excel')
    parser.add_argument('-out', '--outdir')    
