import numpy as np
import pandas as pd
import re
import sys
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon,QFont

class Point:
    def __init__(self,id,x,y,z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"ID: {self.id} [{self.x},{self.y},{self.z}]"

    def get_pos(self):
        return self.x, self.y, self.z
    
    def get_id(self):
        return self.id
    
class Rectangle:
    def __init__(self,id,p1,p2,p3,p4):
        self.id = id
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

    def __str__(self):
        return f"quad_{self.id}"

    def get_id(self):
        return self.id
    
    def get_points(self):
        return self.p1, self.p2, self.p3, self.p4

class Triangle:
    def __init__(self,id,p1,p2,p3):
        self.id = id
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        
    def __str__(self):
        return f"tria_{self.id}"
    
    def get_id(self):
        return self.id
    
    def get_points(self):
        return self.p1, self.p2, self.p3

class Parser:
    def __init__(self,bdffile,excelfile):
        print("\n#############################################\n")
        self.bdffile = bdffile
        self.excelfile = excelfile
        self.load_excel_data()
        self.load_bdf_data()
        self.get_file_name()
        self.nowy_plikERG()
        print("\n#############################################\n")

    def get_file_name(self):
        self.filename = self.bdffile.split("/")[-1]
        self.filename = self.filename.split(".")[-2]
        self.modelname = self.filename[2:]
        print(f"\tNazwa pliku: {self.filename}\n")

    def load_excel_data(self):
        Filter = True #Nan filter
        self.hierarchy = pd.read_excel(self.excelfile,sheet_name="HIERARCHY",na_filter = Filter)
        self.bulk = pd.read_excel(self.excelfile,sheet_name="BULK",na_filter = Filter)
        self.optical = pd.read_excel(self.excelfile,sheet_name="OPTICAL",na_filter = Filter)
        self.primitives = pd.read_excel(self.excelfile,sheet_name="PRIMITIVES",na_filter = Filter)
        self.cuts = pd.read_excel(self.excelfile,sheet_name="CUTS",na_filter = Filter)
        self.settings = pd.read_excel(self.excelfile,sheet_name="Settings",na_filter = Filter)

        self.pid_index = self.hierarchy.columns.get_loc("PID")
    
        self.hier_pierwsze = self.hierarchy.iloc[:,0:self.pid_index] #Jeśli nazwa modelu jest źle to tutaj         
                    
        self.hierarchy = self.hierarchy.loc[:,["nodenumbers of side 1","End Ids","offset","act1","act2","coat1","coat2","bulk1","bulk2","thick1","thick2","unity1","unity2","throughCond","conductance","emittance","mass1","mass2","crit1","crit2","color1","color2"]]

        new_column_names = [f'Col{i+1}' for i in range(len(self.hier_pierwsze.columns))]     #Tutaj zmieniam nazwy  
        self.hier_pierwsze.columns = new_column_names                                        #pierwszych kolumn na
        self.hierarchy = pd.concat([self.hier_pierwsze,self.hierarchy], axis = 1)            #wygodniejsze i łączę
                                                                                             #wszystko w hierarchię

        self.bulk = self.bulk.loc[:,["Bulk Name","Density [Kg/m3]","Specific heat [J/KgK]","Thermal conductivity [w/mK]"]]
        self.optical = self.optical.loc[:,["OPTICAL Name","ir_emiss","ir_refl","ir_trans","solar_abs","solar_ref","solar_trans","ir_spect_refl","solar_spect_refl","Control IR","Control Solar","Alp/Eps"]]


        print("\n\tExcel data loaded succesfully")
        return self.hierarchy,self.bulk,self.optical

    def load_bdf_data(self):
        self.points, self.ctria3, self.cquad4 = [],[],[]

        with open(self.bdffile, 'r') as plik:
            linie = plik.readlines()
            i = 0
            for linia in linie:
                if linia.startswith('GRID'):
                    floats = []
                    id_num = re.findall(r'\b\d+\b', linia)[0]    
                    #Tutaj jest źle. W 2 plikach wykrywa zero na początku a w jednym wykrywa na końcu
                                        #-.1231       #-4.895-3               #tylko 0.
                    found = re.findall(r'([+-]?\.\d+)|(([+-]?\d+\.\d+)-(\d+))|(?<!\d)0\.(?!\d)', linia)
                    print(found)
                    for Duple in found:     #Tutaj trzeba się dokopać do tych liczb
                        for num in Duple:
                            if num == '':
                                continue
                            elif re.match(r'(?<!\d)0\.(?!\d)',num):
                                floats.append(num)

                            elif re.match(r'([+-]?\d+\.\d+)-(\d+)', num): 
                                floats.append(self.convert_engi(Duple[2],Duple[3]))

                            elif re.match(r'([+-]?\.\d+)',num):
                                floats.append(num)

                            
                    
                    floats = [format(float(i),'.8f') for i in floats]
                    #print(floats) 
                    punkt = Point(id_num,floats[0],floats[1],floats[2])
                    
                    self.points.append(punkt)


                elif linia.startswith('CTRIA3'):
                    dane = re.findall(r'[-+]?\d*\.\d+|\d+', linia)
                    figura = Triangle(int(dane[1]), int(dane[3]), int(dane[4]), int(dane[5]))
                    self.ctria3.append(figura)
                
                elif linia.startswith('CQUAD4'):
                    dane = re.findall(r'[-+]?\d*\.\d+|\d+', linia)
                    
                    figura = Rectangle(int(dane[1]),int(dane[3]), int(dane[4]), int(dane[5]),int(dane[6]))
                    self.cquad4.append(figura)

        print("\n\tBDF data loaded succesfully\n")
        return self.points, self.ctria3, self.cquad4
    
    def convert_engi(self,base_number,exp):
            #Do zamiany notacji inżynierskiej na float
            wynik = (float(base_number)) * 10 ** (-int(exp))
            return wynik
    
    def nowy_plikERG(self): #TUTAJ JEST TWORZONY PLIK
        with open(f"{self.filename}.erg","w") as self.file:
            self.file.write(f"BEGIN_MODEL {self.filename[2:]}\n")
            self.tekst("PODPIS")

            self.tekst("BULKS")
            self.add_bulks()

            self.tekst("OPTICAL")
            self.add_optics()

            self.tekst("POINTS")
            for p in self.points:
                x,y,z = p.get_pos()
                self.file.write(f"POINT point_{p.get_id()} = [{x}, {y}, {z}];\n")
            
            self.tekst("SHELLS")
            self.add_shells()

            self.tekst("GROUPS")
            self.add_groups()

            self.tekst("HIERARCHY")
            self.add_hier()

            self.tekst("ASSEMBLY")
            self.assembly()

            self.tekst("END")

            print("\tErg file created succesfully")

    def check_id(self,row,moje_id):
        if pd.notnull(row['nodenumbers of side 1']) and pd.notnull(row['End Ids']):
            return row['nodenumbers of side 1'] <= moje_id <= row['End Ids']
        else:
            return False
    
    def write_row(self,moj_id):
        pasujacy_wiersz = self.hierarchy[self.hierarchy.apply(self.check_id, args=(moj_id,), axis=1)]
        #print(pasujacy_wiersz)

        self.file.write(f'sense = 1,\nmeshType1 = "regular",\nnodes1 = 1,\nratio1 = 1.00000000,\nmeshType2 = "regular",\nnodes2 = 1,\nratio2 = 1.00000000,\nanalysis_type = "Lumped Parameter",\nlabel1 = "",\n')
        #TUTAJ CONDUCTIVE -> Conductive
        side1 = pasujacy_wiersz["act1"].to_string(index=False)
        self.file.write(f'side1 = "{side1[0].upper()+side1[1:].lower()}",\n')
        self.file.write(f'criticality1 = "{pasujacy_wiersz["crit1"].to_string(index=False)}",\n')
        self.file.write(f'nbase1 = {moj_id},\n')
        self.file.write('ndelta1 = 0,\n')
        self.file.write(f'opt1 = {pasujacy_wiersz["coat1"].to_string(index=False)},\n')
        self.file.write(f'colour1 = "{pasujacy_wiersz["color1"].to_string(index=False)}",\n')

        self.file.write('label2 = "",\n')
        #TUTAJ CONDUCTIVE -> Conductive
        side2 = pasujacy_wiersz["act2"].to_string(index=False)
        self.file.write(f'side2 = "{side2[0].upper()+side2[1:].lower()}",\n')
        self.file.write(f'criticality2 = "{pasujacy_wiersz["crit2"].to_string(index=False)}",\n')
        self.file.write(f'nbase2 = {moj_id},\n')
        self.file.write('ndelta2 = 0,\n')
        self.file.write(f'opt2 = {pasujacy_wiersz["coat2"].to_string(index=False)},\n')
        self.file.write(f'colour2 = "{pasujacy_wiersz["color2"].to_string(index=False)}",\n')
        self.file.write(f'composition = "SINGLE",\n')
        self.file.write(f'bulk = {pasujacy_wiersz["bulk1"].to_string(index=False)},\n')
        liczba = format(float(pasujacy_wiersz["thick1"].to_string(index=False)) ,'.8f')
        self.file.write(f'thick = {liczba},\n')

        self.file.write('bulk1 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick1 = 0.00000000,\nbulk2 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick2 = 0.00000000,\n')
        self.file.write(f'through_cond = "{pasujacy_wiersz["throughCond"].to_string(index=False)}",\n')
        self.file.write('conductance = 0.00000000,\nemittance = 0.00000000);')
        

        #TUTAJ CHYBA DODAM SELF.FILE WRITE ITD

    def add_shells(self): 
        #Rozpoznawanie figur i dodawanie ich do osobnych list
        for rec in self.cquad4:
            #print(rec)
            p1,p2,p3,p4 = rec.get_points()      #Tutaj jak nie działa to musi być tak quad_{rec.get_id()}
            self.file.write(f"\n\nGEOMETRY {rec};\n{rec} = SHELL_QUADRILATERAL(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\npoint4 = point_{p4},\n")
            self.write_row(rec.get_id())

        for tria in self.ctria3:
            p1,p2,p3 = tria.get_points()
            #print(f"{tria} wierzcholki {p1.get_pos()} {p2.get_pos()} {p3.get_pos()}")
            self.file.write(f"\n\nGEOMETRY {tria};\n{tria} = SHELL_TRIANGLE(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\n")
            self.write_row(tria.get_id())

    def add_bulks(self):
        materials = self.hierarchy[['bulk1','bulk2']].stack().dropna().unique()

        for material in materials:
            wiersz = self.bulk.loc[self.bulk['Bulk Name'] == material]  #Wiersz pasujący
            val1 = wiersz["Density [Kg/m3]"].to_string(index=False)
            val2 = wiersz["Specific heat [J/KgK]"].to_string(index=False)
            val3 = wiersz["Thermal conductivity [w/mK]"].to_string(index=False)
            self.file.write(f"\nBULK {material} = [{format(float(val1),'.3f')}, {format(float(val2),'.3f')}, {format(float(val3),'.3f')}];")
        
    def add_optics(self):
        coats = self.hierarchy[['coat1','coat2']].stack().dropna().unique()

        for coat in coats:
            wiersz = self.optical.loc[self.optical['OPTICAL Name'] == coat] #Wiersz pasujący
            val1 = wiersz['ir_emiss'].to_string(index=False)
            val2 = wiersz['ir_refl'].to_string(index=False)
            val3 = wiersz['ir_trans'].to_string(index=False)
            val4 = wiersz['solar_abs'].to_string(index=False)
            val5 = wiersz['solar_ref'].to_string(index=False)
            val6 = wiersz['solar_trans'].to_string(index=False)
            val7 = wiersz['ir_spect_refl'].to_string(index=False)
            val8 = wiersz['solar_spect_refl'].to_string(index=False)
            lista = [val1,val2,val3,val4,val5,val6,val7,val8]
            tekst = ', '.join([format(float(i),'.6f') for i in lista])
            self.file.write(f'\nOPTICAL {coat} = [{tekst}];')

    def tekst(self,tekst):
        if tekst == "PODPIS":
            self.file.write("\n/*KONSTANTY KLOSIEWICZ*/\n")

        if tekst == "POINTS":
            #TEKST
            self.file.write("\n/*--------------------------------------*/\n/*                 POINTS               */\n/*--------------------------------------*/\n")

        elif tekst == "OPTICAL":
            self.file.write("\n\n/*--------------------------------------*/\n/*          OPTICAL PROPERTIES          */\n/*--------------------------------------*/")

        elif tekst == "BULKS":
            self.file.write("\n/*--------------------------------------*/\n/*                 BULKS                */\n/*--------------------------------------*/")

        elif tekst == "SHELLS":
            self.file.write("\n/****************************************/\n/*      Start of geometry block         */\n/****************************************/\n\n/*--------------------------------------*/\n/*                 SHELLS               */\n/*--------------------------------------*/")

        elif tekst == "GROUPS":
            self.file.write("\n\n/****************************************/\n\n/****************************************/\n/*        Start of group block          */\n/****************************************/\n\n/*--------------------------------------*/\n/*                 GROUPS               */\n/*--------------------------------------*/")
        
        elif tekst == "HIERARCHY":
            self.file.write("\n\n/*--------------------------------------*/\n/*               HIERARCHY              */\n/*--------------------------------------*/")

        elif tekst == "ASSEMBLY":
            self.file.write("\n\n/*--------------------------------------*/\n/*               ASSEMBLY               */\n/*--------------------------------------*/")

        elif tekst == "END":
            self.file.write("\n/****************************************/\n\nPURGE_MODEL();\nEND_MODEL")

    def make_material_dict(self):
        wszystkie_geometrie = [item for item in self.ctria3+self.cquad4]
        dictionary = {}
                                                        #Dictionary żeby dopasować figury do materiału
        for _ , row in self.hierarchy.iterrows():
            col1 = row["Col1"]
            col2 = row["Col2"]
            col3 = row["Col3"]
            col4 = row["Col4"]
            nodeNum = row["nodenumbers of side 1"]
            endNodeNum = row["End Ids"]
            
            if pd.notna(nodeNum):
                key = col1 if pd.notna(col1) else (col2 if pd.notna(col2) else (col3 if pd.notna(col3) else col4))
                dictionary[key] = (nodeNum,endNodeNum)

                                                        #Pusty dictionary na materiały
        for k,v in dictionary.items():
            materiały = {k:[] for k,v in dictionary.items()}

        for item in wszystkie_geometrie:                #Tutaj sprawdzam czy prymityw geometryczny jest 
            for key,ids in dictionary.items():          #w przedziale id-endid. Jeśli tak to dodaję do materiału
                if ids[0] <= item.get_id() <= ids[1]:
                    materiały[key].append(str(item))
                else:
                    continue
        return materiały
    
    def add_groups(self):
        materiały = self.make_material_dict()
        # print(materiały)
        for materiał,lista in materiały.items():
            tekst = ' + '.join(lista)
            self.file.write(f"\n\nGEOMETRY {materiał};\n{materiał} = {tekst};")
            
    def add_hier(self):
        if self.hier_pierwsze['Col4'].isna().all(): #Jeśli czwarta kolumna pusta
            self.result1 = self.helper_child_parent(self.hier_pierwsze.loc[:,["Col2","Col3"]])
            for parent in self.result1:
                if not self.result1[parent]:
                   continue
                else:
                   lista = ' + '.join(self.result1[parent])
                   self.file.write(f"\nGEOMETRY {parent};\n{parent} = {lista};\n")

        else: #Jeśli jest czwarta kolumna
            self.result1 = self.helper_child_parent(self.hier_pierwsze.loc[:,["Col3","Col4"]])
            self.result2 = self.helper_child_parent(self.hier_pierwsze.loc[:,["Col2","Col3"]])
            for parent in self.result1:
                if not self.result1[parent]:
                    continue
                else:
                    lista = ' + '.join(self.result1[parent])
                    self.file.write(f"\nGEOMETRY {parent};\n{parent} = {lista};\n")

            for parent in self.result2:
                if not self.result2[parent]:
                    continue
                else:
                    lista = ' + '.join(self.result2[parent])
                    self.file.write(f"\nGEOMETRY {parent};\n{parent} = {lista};\n") 

    def helper_child_parent(self,cols):
        colX = cols.iloc[:,0]
        last_index = colX.index[-1]
        colY = cols.iloc[:,1]
        parents = {}
        colX = colX.dropna()
        original_indexes = colX.index.tolist() + [last_index]

        for i in range(0,len(colX)):
            try:
                start = original_indexes[i]
                end = original_indexes[i+1]
                ojciec = colX.iloc[i]
                #print("Stary = ",ojciec)
                children = colY[start:end+1].dropna().tolist()
                #print("Dziecko = ",children)
                parents[ojciec] = children
            except:
                continue

        return(parents)
        
    def assembly(self):
        if self.hier_pierwsze['Col4'].isna().all(): #Jeśli czwarta kolumna pusta
            lista = ' + '.join(self.result1)
            self.file.write(f"\n\n{self.modelname} = {lista};\n")
        else:
            lista = ' + '.join(self.result2)
            self.file.write(f"\n\n{self.modelname} = {lista};\n")


if __name__ == '__main__':

    excel_path = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER\1_TCS_FPM_TVAC.xlsx"
    bdf_path = "1_TCS_FPM_TVAC.bdf"

    parser = Parser(bdf_path,excel_path)