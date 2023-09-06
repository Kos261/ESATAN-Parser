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

class Primitive:
    def __init__(self,name,id):
        self.id = id
        self.name = name

    def __str__(self):
        return f"{self.name}_{self.id}"

    def get_id(self):
        return self.id


class Parser:
    def __init__(self,bdffile,excelfile):
        print("\n#############################################\n")
        self.points = []
        self.ctria3 = []
        self.cquad4 = []
        self.any_primitive = []
        self.bdffile = bdffile
        self.excelfile = excelfile
        self.load_excel_data()
        self.load_bdf_data()
        self.get_file_name()
        self.nowy_plikERG()
        print("\n#############################################\n")

    def get_file_name(self):
        self.filename = self.bdffile.split("\\")[-1]
        self.filename = self.filename.split(".")[-2]
        self.modelname = self.filename[2:]
        print(f"\tNazwa pliku: {self.filename}\n")

    def load_excel_data(self):
        Filter = True #Nan filter

        self.primitives = pd.read_excel(self.excelfile,sheet_name="PRIMITIVES",na_filter = Filter)
        self.primitives = self.primitives.iloc[:,list(range(8)) + [9]]
        
        self.cuts = pd.read_excel(self.excelfile,sheet_name="CUTS",na_filter = Filter)
        self.cuts = self.cuts.loc[:,["CUT Name","SHELL 1","SHELL 2"]]

        self.hierarchy = pd.read_excel(self.excelfile,sheet_name="HIERARCHY",na_filter = Filter)
        self.pid_index = self.hierarchy.columns.get_loc("PID")
        self.hier_pierwsze = self.hierarchy.iloc[:,0:self.pid_index] #Jeśli nazwa modelu jest źle to tutaj                   
        self.hierarchy = self.hierarchy.loc[:,["nodenumbers of side 1","End Ids","offset","act1","act2","coat1","coat2","bulk1","bulk2","thick1","thick2","unity1","unity2","throughCond","conductance","emittance","mass1","mass2","crit1","crit2","color1","color2"]]

        new_column_names = [f'Col{i+1}' for i in range(len(self.hier_pierwsze.columns))] 
        self.hier_pierwsze.columns = new_column_names                                   
        self.hierarchy = pd.concat([self.hier_pierwsze,self.hierarchy], axis = 1)       
                                                                            
        self.bulk = pd.read_excel(self.excelfile,sheet_name="BULK",na_filter = Filter)
        self.bulk = self.bulk.loc[:,["Bulk Name","Density [Kg/m3]","Specific heat [J/KgK]","Thermal conductivity [w/mK]"]]

        self.optical = pd.read_excel(self.excelfile,sheet_name="OPTICAL",na_filter = Filter)
        self.optical = self.optical.loc[:,["OPTICAL Name","ir_emiss","ir_refl","ir_trans","solar_abs","solar_ref","solar_trans","ir_spect_refl","solar_spect_refl","Control IR","Control Solar","Alp/Eps"]]

        self.settings = pd.read_excel(self.excelfile,sheet_name="Settings",na_filter = Filter)

        print("\n\tExcel data loaded succesfully")

    def load_bdf_data(self):
                #   -.123          -3.123-3 tu dwie cyfry w inżynieru       ''0.''         -5.-3
        regex = r'([+-]?\.\d+)|(([+-]?\d\.\d+)-(\d))|(\s0\.\s)|(([+-]?\d\.)-(\d))'
        
        with open(self.bdffile, 'r') as plik:
            linie = plik.readlines()
            i = 25
            for linia in linie:
                if linia.startswith('GRID'):
                    floats = []
                    id_num = re.findall(r'\b\d+\b', linia)[0]    
                    found = re.findall(regex, linia)
                    for Duple in found:
                        for num in Duple:
                            if num == '':
                                continue
                            elif re.match(r'(\s0\.\s)|([+-]?\.\d+)',num):
                                #           ''0.''         -.123
                                floats.append(num)

                            elif re.match(r'([+-]?\d\.\d+)-(\d)', num): 
                                #               -3.123-3
                                floats.append(self.convert_engi(Duple[2],Duple[3]))
                            
                            elif re.match(r'([+-]?\d\.)-(\d)', num):
                                 #          -5.-3
                                floats.append(self.convert_engi(Duple[6],Duple[7]))

                    floats = [format(float(i),'.8f') for i in floats]
                    punkt = Point(id_num,floats[0],floats[1],floats[2])
                    self.points.append(punkt)

#TUTAJ CHYBA ZROBIĘ OD RAZU APPLY CZY PASUJE FIGURA DO SHELL1 LUB SHELL2 LUB PRIMITIVE JEŚLI TAK TO DODAJĘ DO KTÓREJŚ Z LIST. NADAM IM NAZWY Z PRIMITIVES np. BOX_123 A POTEM JESZCZE PRZYDZIELĘ DO CUTS
                elif linia.startswith('CTRIA3'):
                    dane = re.findall(r'[-+]?\d*\.\d+|\d+', linia)
                    figura = Triangle(int(dane[1]), int(dane[3]), int(dane[4]), int(dane[5]))
                    self.ctria3.append(figura)
                
                elif linia.startswith('CQUAD4'):
                    dane = re.findall(r'[-+]?\d*\.\d+|\d+', linia)
                    
                    figura = Rectangle(int(dane[1]),int(dane[3]), int(dane[4]), int(dane[5]),int(dane[6]))
                    self.cquad4.append(figura)

        print("\n\tBDF data loaded succesfully\n")
        return
    
    def convert_engi(self,base_number,exp):
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

            self.tekst("START GROUP BLOCKS")
            if not self.cuts.empty:
                self.add_cuts()

            self.tekst("GROUPS")
            self.add_groups()

            self.tekst("HIERARCHY")
            self.add_hier()

            self.tekst("ASSEMBLY")
            self.assembly()

            self.tekst("END")

            print("\tErg file created succesfully")

    def add_shells(self): 
        #TUTAJ TRZEBA POŁĄCZYĆ TRÓJKĄTY,PROSTOKĄTY I PRYMITYWY I DLA WSZYSTKIEGO SPRAWDZAĆ CZY JEST W HIERARCHII I PRYMITYWACH. PRYMITYWY MAJĄ NIEKTÓRE CECHY Z HIERARCHII A NIEKTÓRE Z PRYMITIVES
        #PROSTOKĄTY                 
        for rec in self.cquad4:
            p1,p2,p3,p4 = rec.get_points() 
            wiersz_hier = self.hierarchy[self.hierarchy.apply(self.check_id_hier, args=(rec.get_id(),), axis=1)]
            wiersz_prim = self.primitives[self.primitives.apply(self.check_id_prim, args=(rec.get_id(),),axis=1)]
            
            if not wiersz_hier.empty:
                self.file.write(f"\n\nGEOMETRY {rec};\n{rec} = SHELL_QUADRILATERAL(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\npoint4 = point_{p4},\n")
                self.add_one_figure_hier(rec.get_id(),wiersz_hier)


            #TUTAJ ZAMIENIĘ TO NA OBIEKT PRYMITYW O TYCH CECHACH
            elif not wiersz_prim.empty:
                print("W PRIM")
                Id = wiersz_prim.loc["node number"]
                prymityw = wiersz_prim.loc["Primitives"]
                Prymityw = prymityw.upper()
                self.file.write(f"\n\nGEOMETRY {prymityw}_{Id};\n{prymityw}_{Id} = SHELL_{Prymityw}(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\npoint4 = point_{p4},\n")
                self.add_one_figure_prim(rec.get_id(),wiersz_prim,wiersz_hier)

            else:
                print("ID nie ma na żadnej tabeli")

        #TRÓJKĄTY
        for tria in self.ctria3:
            p1,p2,p3 = tria.get_points()
            wiersz_hier = self.hierarchy[self.hierarchy.apply(self.check_id_hier, args=(tria.get_id(),), axis=1)]
            wiersz_prim = self.primitives[self.primitives.apply(self.check_id_prim, args=(tria.get_id(),),axis=1)]

            if not wiersz_hier.empty:
                self.file.write(f"\n\nGEOMETRY {tria};\n{tria} = SHELL_TRIANGLE(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\n")
                self.add_one_figure_hier(tria.get_id(),wiersz_hier)

            #Tu trzeba dokończyć
            elif not wiersz_prim.empty:     
                print("W PRIM")
                Id = wiersz_prim.loc["node number"]
                prymityw = wiersz_prim.loc["Primitives"]
                Prymityw = prymityw.upper()
                self.file.write(f"\n\nGEOMETRY {prymityw}_{Id};\n{prymityw}_{Id} = SHELL_{Prymityw}(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\n")
                self.add_one_figure_prim(rec.get_id(),wiersz_prim,wiersz_hier)

            else:
                print("ID nie ma na żadnej tabeli")

    def check_id_hier(self,row,moje_id):
        if pd.notnull(row['nodenumbers of side 1']) and pd.notnull(row['End Ids']):
            return row['nodenumbers of side 1'] <= moje_id <= row['End Ids']
        else:
            return False
        
    def check_id_prim(self,row,moje_id):
        if pd.notnull(row["node number"]):
            return row["node number"] == moje_id
        else:
            return False

    def add_one_figure_hier(self,moj_id,wiersz_hier):
        self.file.write(f'sense = 1,\nmeshType1 = "regular",\nnodes1 = 1,\nratio1 = 1.00000000,\nmeshType2 = "regular",\nnodes2 = 1,\nratio2 = 1.00000000,\nanalysis_type = "Lumped Parameter",\nlabel1 = "",\n')
        side1 = wiersz_hier["act1"].to_string(index=False)
        self.file.write(f'side1 = "{side1[0].upper()+side1[1:].lower()}",\n')
        self.file.write(f'criticality1 = "{wiersz_hier["crit1"].to_string(index=False)}",\n')
        self.file.write(f'nbase1 = {moj_id},\n')
        self.file.write('ndelta1 = 0,\n')
        self.file.write(f'opt1 = {wiersz_hier["coat1"].to_string(index=False)},\n')
        self.file.write(f'colour1 = "{wiersz_hier["color1"].to_string(index=False)}",\n')

        self.file.write('label2 = "",\n')
        side2 = wiersz_hier["act2"].to_string(index=False)
        self.file.write(f'side2 = "{side2[0].upper()+side2[1:].lower()}",\n')
        self.file.write(f'criticality2 = "{wiersz_hier["crit2"].to_string(index=False)}",\n')
        self.file.write(f'nbase2 = {moj_id},\n')
        self.file.write('ndelta2 = 0,\n')
        self.file.write(f'opt2 = {wiersz_hier["coat2"].to_string(index=False)},\n')
        self.file.write(f'colour2 = "{wiersz_hier["color2"].to_string(index=False)}",\n')
        self.file.write(f'composition = "SINGLE",\n')
        self.file.write(f'bulk = {wiersz_hier["bulk1"].to_string(index=False)},\n')
        liczba = format(float(wiersz_hier["thick1"].to_string(index=False)) ,'.8f')
        self.file.write(f'thick = {liczba},\n')

        self.file.write('bulk1 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick1 = 0.00000000,\nbulk2 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick2 = 0.00000000,\n')
        self.file.write(f'through_cond = "{wiersz_hier["throughCond"].to_string(index=False)}",\n')
        self.file.write('conductance = 0.00000000,\nemittance = 0.00000000);')
        
    def add_one_figure_prim(self,moj_id,wiersz_prim,wiersz_hier):
        if wiersz_prim.loc["CUTTING SENSE Inside: sense = -1, Outside: sense = 1"] == "OUTSIDE":
            self.file.write(f'sense = 1,\n')
        elif wiersz_prim.loc["CUTTING SENSE Inside: sense = -1, Outside: sense = 1"] == "INSIDE":
            self.file.write(f'sense = -1,\n')

        if wiersz_prim.loc[ "CONFIG          O:Original S:Section C:Cropped CS: Cropped/Section"] == "O":
            self.file.write(f'\n')
        elif wiersz_prim.loc["CONFIG          O:Original S:Section C:Cropped CS: Cropped/Section"] == "S":
            self.file.write(f'\n')
        elif wiersz_prim.loc["CONFIG          O:Original S:Section C:Cropped CS: Cropped/Section"] == "C":
            self.file.write(f'\n')
        elif wiersz_prim.loc["CONFIG          O:Original S:Section C:Cropped CS: Cropped/Section"] == "CS":
            self.file.write(f'\n')                          
                            
        self.file.write('meshType1 = "regular",\n')
        self.file.write(f"nodes1 = {wiersz_prim.loc['nodes 1: Elements circumreference']},\n")
        self.file.write("meshType2 = 'regular',\n")
        self.file.write(f"ratio1 = {wiersz_prim.loc['ratio1']},\n")
        self.file.write(f"nodes2 = {wiersz_prim.loc['nodes 2: Elements length']},\n")
        self.file.write(f"ratio2 = {wiersz_prim.loc['ratio2']},\n")
        #W sumie mam jeszcze pytanie czy jak tworzę figurę z primitives to czy ona potem ma te wszystkie parametry co figury w hierarchii? Bo ID znajduje się chyba albo w hierarchii albo primitives. Czy może być i tu i tu?

        #wiersz_hier
        self.file.write('analysis_type = "Lumped Parameter",\nlabel1 = "",\n')
        side1 = wiersz_hier["act1"].to_string(index=False)
        self.file.write(f'side1 = "{side1[0].upper()+side1[1:].lower()}",\n')
        self.file.write(f'criticality1 = "{wiersz_hier["crit1"].to_string(index=False)}",\n')
        self.file.write(f'nbase1 = {moj_id},\n')
        self.file.write('ndelta1 = 0,\n')
        self.file.write(f'opt1 = {wiersz_hier["coat1"].to_string(index=False)},\n')
        self.file.write(f'colour1 = "{wiersz_hier["color1"].to_string(index=False)}",\n')
        self.file.write('label2 = "",\n')
        side2 = wiersz_hier["act2"].to_string(index=False)
        self.file.write(f'side2 = "{side2[0].upper()+side2[1:].lower()}",\n')
        self.file.write(f'criticality2 = "{wiersz_hier["crit2"].to_string(index=False)}",\n')
        self.file.write(f'nbase2 = {moj_id},\n')
        self.file.write('ndelta2 = 0,\n')
        self.file.write(f'opt2 = {wiersz_hier["coat2"].to_string(index=False)},\n')
        self.file.write(f'colour2 = "{wiersz_hier["color2"].to_string(index=False)}",\n')
        self.file.write(f'composition = "SINGLE",\n')
        self.file.write(f'bulk = {wiersz_hier["bulk1"].to_string(index=False)},\n')
        liczba = format(float(wiersz_hier["thick1"].to_string(index=False)) ,'.8f')
        self.file.write(f'thick = {liczba},\n')

        self.file.write('bulk1 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick1 = 0.00000000,\nbulk2 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick2 = 0.00000000,\n')
        self.file.write(f'through_cond = "{wiersz_prim["throughCond"].to_string(index=False)}",\n')
        self.file.write('conductance = 0.00000000,\nemittance = 0.00000000);')

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

    def make_material_dict(self):
        self.wszystkie_geometrie = [item for item in self.ctria3+self.cquad4]
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

        for item in self.wszystkie_geometrie:                #Tutaj sprawdzam czy prymityw geometryczny jest 
            for key,ids in dictionary.items():          #w przedziale id-endid. Jeśli tak to dodaję do materiału
                if ids[0] <= item.get_id() <= ids[1]:
                    materiały[key].append(str(item))
                else:
                    continue
        return materiały
    
    def add_cuts(self):
        for index,row in self.cuts.iterrows():
            if not row.isnull().all():
                print(row[0],row[1],row[2])
                shell1 = re.findall(r'\b\d+\b',row[1])
                shell2 = re.findall(r'\b\d+\b',row[2])
                print(shell1,shell2)

            # for item in self.wszystkie_geometrie:
            #     if self.fig_in_cuts()

            #self.file.write(f"\nGEOMETRY cut_{row.loc['CUT Name']};\ncut_{row.loc['CUT Name']} = ")

        else:
            return

    def fig_in_cuts(self,id_fig,id_in_cuts):
        return  id_fig == id_in_cuts

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

        elif tekst == "START GROUP BLOCKS":
            self.file.write("\n\n/****************************************/\n\n/****************************************/\n/*        Start of group block          */\n/****************************************/\n")

        elif tekst == "GROUPS":
            self.file.write("\n/*--------------------------------------*/\n/*                 GROUPS               */\n/*--------------------------------------*/")

        
        elif tekst == "HIERARCHY":
            self.file.write("\n\n/*--------------------------------------*/\n/*               HIERARCHY              */\n/*--------------------------------------*/")

        elif tekst == "ASSEMBLY":
            self.file.write("\n\n/*--------------------------------------*/\n/*               ASSEMBLY               */\n/*--------------------------------------*/")

        elif tekst == "END":
            self.file.write("\n/****************************************/\n\nPURGE_MODEL();\nEND_MODEL")



if __name__ == '__main__':
    

    #Primitives, Cuts, Grupa Prim-cuts, Cyfry w BDF max 2 cyfry, Raport
    #Po co, założenia, Idiotoodporne, Kod do pobrania i co trzeba pobrać, żeby dało się zmienić


    excel_path = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER\2_FGS_TA_Rv04\2_FGS_TA_Rv04.xlsx"
    bdf_path = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER\2_FGS_TA_Rv04\2_FGS_TA_Rv04.bdf"

    parser = Parser(bdf_path,excel_path)