import warnings
warnings.filterwarnings(
    "ignore",
    message="Data Validation extension is not supported and will be removed",
    category=UserWarning,
    module=r"openpyxl\.worksheet\._reader",
)
import pandas as pd
import re
from pathlib import Path
from src.geometry import Point, Primitive, Triangle, Rectangle


class ERG_Parser:

    def __init__(self, outputdir='output'):
        self.primitives = None
        self.cuts = None
        self.hierarchy = None
        self.optical = None 
        self.settings = None
        self.bulk = None
        self.all_geometry = []
        # self.any_primitive = []
        self.cquad4 = []
        self.ctria3 = []
        self.points = []
        self.shell1 = []
        self.shell2 = []
        self.outputdir = outputdir
        
        
    def merge_files_into_ERG(self, bdffile, excelfile):
        self.load_excel_data(excelfile)
        self.load_bdf_data(bdffile)
        filename, modelname = self.get_file_name(bdffile)

        creator = ERG_Creator(filename=filename,
                              modelname = modelname,
                              points=self.points,
                              geometry=self.all_geometry,
                              primitives=self.primitives,
                              cuts=self.cuts,
                              hierarchy=self.hierarchy,
                              hier_first_cols=self.hier_first_cols,
                              optical=self.optical,
                              settings=self.settings,
                              bulk=self.bulk,
                              outputdir=self.outputdir)
        creator.nowy_plikERG()
        print("DONE!")

    def get_file_name(self, file):
        if "/" in file:
            filename = file.split(r'/')[-1]
            filename = filename.split(".")[-2]
            modelname = filename[2:]
            print(f"File name: {filename}\n")
            
        elif "\\" in file:
            filename = file.split("\\")[-1]
            filename = filename.split(".")[-2]
            modelname = filename[2:]
            print(f"Filename: {filename}\n")
        
        return filename, modelname

    def load_excel_data(self, excelfile):
        Filter = True #Nan filter

        self.primitives = pd.read_excel(excelfile,sheet_name="PRIMITIVES",na_filter = Filter)
        self.primitives = self.primitives.iloc[:,list(range(8)) + [9]]
        new_column_names = ["Primitives","node number","Config","Cutting","nodes 1","nodes 2","ratio1","ratio2","CAUTION"]
        self.primitives.columns = new_column_names

        if not (self.primitives.loc[:,["Primitives","node number"]].isna().all().all() or (self.primitives.loc[:,["Primitives","node number"]] == 0).all().all()):
            self.primitives['node number'] = self.primitives['node number'].apply(lambda x: str(x) if pd.notna(x) else x)
            # Deleting semicolons and dots
            self.primitives['node number'] = self.primitives['node number'].str.replace(r'\.0', '', regex=True)
            # Adding them back (optional)
            self.primitives['node number'] = self.primitives['node number'].apply(lambda x: int(x) if pd.notna(x) else x)
        
        self.cuts = pd.read_excel(excelfile,sheet_name="CUTS",na_filter = Filter)
        self.cuts = self.cuts.loc[:,["CUT Name","SHELL 1","SHELL 2"]]

        self.hierarchy = pd.read_excel(excelfile,sheet_name="HIERARCHY",na_filter = Filter)
        self.pid_index = self.hierarchy.columns.get_loc("PID")
        self.hier_first_cols = self.hierarchy.iloc[:,0:self.pid_index]
        self.hierarchy = self.hierarchy.loc[:,["nodenumbers of side 1","End Ids","offset","act1","act2","coat1","coat2","bulk1","bulk2","thick1","thick2","unity1","unity2","throughCond","conductance","emittance","mass1","mass2","crit1","crit2","color1","color2"]]

        new_column_names = [f'Col{i+1}' for i in range(len(self.hier_first_cols.columns))] 
        self.hier_first_cols.columns = new_column_names                                   
        self.hierarchy = pd.concat([self.hier_first_cols,self.hierarchy], axis = 1)       
                                                                            
        self.bulk = pd.read_excel(excelfile,sheet_name="BULK",na_filter = Filter)
        self.bulk = self.bulk.loc[:,["Bulk Name","Density [Kg/m3]","Specific heat [J/KgK]","Thermal conductivity [w/mK]"]]

        self.optical = pd.read_excel(excelfile,sheet_name="OPTICAL",na_filter = Filter)
        self.optical = self.optical.loc[:,["OPTICAL Name","ir_emiss","ir_refl","ir_trans","solar_abs","solar_ref","solar_trans","ir_spect_refl","solar_spect_refl","Control IR","Control Solar","Alp/Eps"]]

        self.settings = pd.read_excel(excelfile,sheet_name="Settings",na_filter = Filter)

        print("\nExcel data loaded succesfully")

    def load_bdf_data(self, bdffile, debug=False):       
                                        # .123-3
                        #   -.123          -3.123-3 engineer       ''0.''         -5.-3
        # self.regex_ptrn = r'([+-]?\.\d+)|(([+-]?\d\.\d+)-(\d))|(\s0\.\s)|(([+-]?\d\.)-(\d))'

        with open(bdffile, 'r') as file:
            lines = file.readlines()
            for line in lines:
                
                if line.startswith("GRID"):
                    self.line_to_point(line)

                elif line.startswith("CTRIA3"):
                    self.line_to_triang(line)
                
                elif line.startswith('CQUAD4'):
                    self.line_to_rect(line)

        self.all_geometry = self.ctria3+self.cquad4
        print("\nBDF data loaded succesfully\n")
    
    def split_f8(self, line: str) -> list[str]:
        """List of 8-char fields"""
        return [line[i:i+8].strip() for i in range(0, len(line), 8)]

    def f8_to_float(self, field: str) -> float:
        if not field:
            return 0.0 # UWAGA!
        if 'e' not in field.lower():
            m = re.search(r'([+-])(?!.*[+-])', field[1:])   # ostatni +/- po indeksie 0
        if m:
            i = m.start() + 1       
            field = field[:i] + 'e' + field[i:]
        return float(field)
    
    def line_to_point(self, line: str):
        fields = self.split_f8(line)
        id = int(fields[1])
        x = self.f8_to_float(fields[3])
        y = self.f8_to_float(fields[4])
        z = self.f8_to_float(fields[5])

        node = Point(id=id, x=x, y=y, z=z)
        self.points.append(node)
        return node

    def line_to_rect(self, line: str):
        fields = self.split_f8(line)
        id = int(fields[1])
        p1 = int(fields[3])
        p2 = int(fields[4])
        p3 = int(fields[5])
        p4 = int(fields[6])
        figura = Rectangle(id=id, p1=p1, p2=p2, p3=p3, p4=p4)
        self.cquad4.append(figura)

    def line_to_triang(self, line: str):
        fields = self.split_f8(line)
        id = int(fields[1])
        p1 = int(fields[3])
        p2 = int(fields[4])
        p3 = int(fields[5])
        figura = Triangle(id=id, p1=p1, p2=p2, p3=p3)
        self.ctria3.append(figura)

class ERG_Creator:
   
    def __init__(self, filename, modelname, points, geometry, primitives,
                  cuts, hierarchy, hier_first_cols, optical, settings, bulk, outputdir="output"):
        print("Creating '.erg' file")

        self.modelname = modelname
        outputdir = Path(outputdir)
        outputdir.mkdir(parents=True, exist_ok=True)
        self.file_path = outputdir / f"{filename}.erg"

        self.points = points
        self.all_geometry = geometry
        self.primitives = primitives
        self.cuts = cuts
        self.hierarchy = hierarchy
        self.hier_first_cols = hier_first_cols
        self.optical = optical
        self.settings = settings
        self.bulk = bulk
        # self.any_primitive = []
       
        self.shell1 = []
        self.shell2 = []

    def nowy_plikERG(self):
        self.transform_to_primitives()

        with self.file_path.open("w") as self.file:
            self.file.write(f"BEGIN_MODEL {self.modelname}\n")
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
            # if not self.cuts.empty:
            #     self.add_cuts()

            self.tekst("GROUPS")
            self.add_groups()

            self.tekst("HIERARCHY")
            self.add_hier()

            self.tekst("ASSEMBLY")
            self.assembly()

            self.tekst("END")

            print("Erg file created succesfully")

    def add_shells(self): 
        for figure in self.all_geometry:
            
            Id = figure.get_id()
            row_hierarchy = self.hierarchy[self.hierarchy.apply(self.check_id_hier, args=(Id,), axis=1)]
            
            if isinstance(figure,Triangle):
                p1,p2,p3 = figure.get_points()
                self.file.write(f"\n\nGEOMETRY {figure};\n{figure} = SHELL_TRIANGLE(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\n")
                self.add_one_figure_hier(Id,row_hierarchy)

            elif isinstance(figure,Rectangle):
                p1,p2,p3,p4 = figure.get_points() 
                self.file.write(f"\n\nGEOMETRY {figure};\n{figure} = SHELL_QUADRILATERAL(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\npoint4 = point_{p4},\n")
                self.add_one_figure_hier(Id,row_hierarchy)

            elif isinstance(figure,Primitive):
                row_primitive = self.primitives[self.primitives.apply(self.check_id_prim, args=(Id,),axis=1)]
            
                if figure.node_num == 3:
                    p1,p2,p3 = figure.get_points()
                    self.file.write(f"\n\nGEOMETRY {figure};\n{figure} = {figure.BIG()}(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\n")
                    self.add_one_figure_prim(Id,row_primitive,row_hierarchy)
                    
                if figure.node_num == 4:
                    p1,p2,p3,p4 = figure.get_points()
                    self.file.write(f"\n\nGEOMETRY {figure};\n{figure} = {figure.BIG()}(\npoint1 = point_{p1},\npoint2 = point_{p2},\npoint3 = point_{p3},\npoint4 = point_{p4},\n")
                    self.add_one_figure_prim(Id,row_primitive,row_hierarchy)

            else:
                print("Wrong definition of primitive")

    def transform_to_primitives(self):
        for index, item in enumerate(self.all_geometry):
            Id = item.get_id()
            row_primitive = self.primitives[self.primitives.apply(self.check_id_prim, args=(Id,),axis=1)]
            
            if not row_primitive.empty:
                primitive_name = row_primitive["Primitives"].values[0]

                if isinstance(item,Triangle):
                    p1,p2,p3 = item.get_points()
                    primitive = Primitive(primitive_name,Id,p1,p2,p3)
                    # self.any_primitive.append(primitive)
                    self.all_geometry[index] = primitive

                elif isinstance(item,Rectangle):
                    p1,p2,p3,p4 = item.get_points()
                    primitive = Primitive(primitive_name,Id,p1,p2,p3,p4)
                    # self.any_primitive.append(primitive)
                    self.all_geometry[index] = primitive
            else:
                continue

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

    def add_one_figure_hier(self,moj_id,row_hierarchy):
        self.file.write(f'sense = 1,\nmeshType1 = "regular",\nnodes1 = 1,\nratio1 = 1.00000000,\nmeshType2 = "regular",\nnodes2 = 1,\nratio2 = 1.00000000,\nanalysis_type = "Lumped Parameter",\nlabel1 = "",\n')
        side1 = row_hierarchy["act1"].to_string(index=False)
        self.file.write(f'side1 = "{side1[0].upper()+side1[1:].lower()}",\n')
        self.file.write(f'criticality1 = "{row_hierarchy["crit1"].to_string(index=False)}",\n')
        self.file.write(f'nbase1 = {moj_id},\n')
        self.file.write('ndelta1 = 0,\n')
        self.file.write(f'opt1 = {row_hierarchy["coat1"].to_string(index=False)},\n')
        self.file.write(f'colour1 = "{row_hierarchy["color1"].to_string(index=False)}",\n')

        self.file.write('label2 = "",\n')
        side2 = row_hierarchy["act2"].to_string(index=False)
        self.file.write(f'side2 = "{side2[0].upper()+side2[1:].lower()}",\n')
        self.file.write(f'criticality2 = "{row_hierarchy["crit2"].to_string(index=False)}",\n')
        self.file.write(f'nbase2 = {moj_id},\n')
        self.file.write('ndelta2 = 0,\n')
        self.file.write(f'opt2 = {row_hierarchy["coat2"].to_string(index=False)},\n')
        self.file.write(f'colour2 = "{row_hierarchy["color2"].to_string(index=False)}",\n')
        self.file.write(f'composition = "SINGLE",\n')
        self.file.write(f'bulk = {row_hierarchy["bulk1"].to_string(index=False)},\n')
        liczba = format(float(row_hierarchy["thick1"].to_string(index=False)) ,'.8f')
        self.file.write(f'thick = {liczba},\n')

        self.file.write('bulk1 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick1 = 0.00000000,\nbulk2 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick2 = 0.00000000,\n')
        self.file.write(f'through_cond = "{row_hierarchy["throughCond"].to_string(index=False)}",\n')
        self.file.write('conductance = 0.00000000,\nemittance = 0.00000000);')
        
    def add_one_figure_prim(self,moj_id,row_primitive,row_hierarchy):
        
        if row_primitive["Cutting"].values[0] == "OUTSIDE":
            self.file.write(f'sense = 1,\n')
        elif row_primitive["Cutting"].values[0] == "INSIDE":
            self.file.write(f'sense = -1,\n')

        self.file.write('meshType1 = "regular",\n')
        nodes1 = int(row_primitive['nodes 1'].values[0])
        self.file.write(f"nodes1 = {nodes1},\n")
        self.file.write('meshType2 = "regular",\n')
        ratio1 = format(row_primitive['ratio1'].values[0],'8f')
        self.file.write(f"ratio1 = {ratio1},\n")
        nodes2 = int(row_primitive['nodes 2'].values[0])
        self.file.write(f"nodes2 = {nodes2},\n")
        ratio2 = format(row_primitive['ratio2'].values[0],'8f')
        self.file.write(f"ratio2 = {ratio2},\n")

        self.file.write('analysis_type = "Lumped Parameter",\nlabel1 = "",\n')
        side1 = row_hierarchy["act1"].to_string(index=False)
        self.file.write(f'side1 = "{side1[0].upper()+side1[1:].lower()}",\n')
        self.file.write(f'criticality1 = "{row_hierarchy["crit1"].to_string(index=False)}",\n')
        self.file.write(f'nbase1 = {moj_id},\n')
        self.file.write('ndelta1 = 0,\n')
        self.file.write(f'opt1 = {row_hierarchy["coat1"].to_string(index=False)},\n')
        self.file.write(f'colour1 = "{row_hierarchy["color1"].to_string(index=False)}",\n')
        self.file.write('label2 = "",\n')
        side2 = row_hierarchy["act2"].to_string(index=False)
        self.file.write(f'side2 = "{side2[0].upper()+side2[1:].lower()}",\n')
        self.file.write(f'criticality2 = "{row_hierarchy["crit2"].to_string(index=False)}",\n')
        self.file.write(f'nbase2 = {moj_id},\n')
        self.file.write('ndelta2 = 0,\n')
        self.file.write(f'opt2 = {row_hierarchy["coat2"].to_string(index=False)},\n')
        self.file.write(f'colour2 = "{row_hierarchy["color2"].to_string(index=False)}",\n')
        self.file.write(f'composition = "SINGLE",\n')
        self.file.write(f'bulk = {row_hierarchy["bulk1"].to_string(index=False)},\n')
        liczba = format(float(row_hierarchy["thick1"].to_string(index=False)) ,'.8f')
        self.file.write(f'thick = {liczba},\n')

        self.file.write('bulk1 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick1 = 0.00000000,\nbulk2 = [-10000.00000000, -10000.00000000, -10000.00000000],\nthick2 = 0.00000000,\n')
        self.file.write(f'through_cond = "{row_hierarchy["throughCond"].to_string(index=False)}",\n')
        self.file.write('conductance = 0.00000000,\nemittance = 0.00000000);')

    def add_bulks(self):
        materials = self.hierarchy[['bulk1','bulk2']].stack().dropna().unique()

        for material in materials:
            row = self.bulk.loc[self.bulk['Bulk Name'] == material]
            val1 = row["Density [Kg/m3]"].to_string(index=False)
            val2 = row["Specific heat [J/KgK]"].to_string(index=False)
            val3 = row["Thermal conductivity [w/mK]"].to_string(index=False)
            self.file.write(f"\nBULK {material} = [{format(float(val1),'.3f')}, {format(float(val2),'.3f')}, {format(float(val3),'.3f')}];")
        
    def add_optics(self):
        coats = self.hierarchy[['coat1','coat2']].stack().dropna().unique()

        for coat in coats:
            row = self.optical.loc[self.optical['OPTICAL Name'] == coat]
            val1 = row['ir_emiss'].to_string(index=False)
            val2 = row['ir_refl'].to_string(index=False)
            val3 = row['ir_trans'].to_string(index=False)
            val4 = row['solar_abs'].to_string(index=False)
            val5 = row['solar_ref'].to_string(index=False)
            val6 = row['solar_trans'].to_string(index=False)
            val7 = row['ir_spect_refl'].to_string(index=False)
            val8 = row['solar_spect_refl'].to_string(index=False)
            lista = [val1,val2,val3,val4,val5,val6,val7,val8]
            tekst = ', '.join([format(float(i),'.6f') for i in lista])
            self.file.write(f'\nOPTICAL {coat} = [{tekst}];')

    def make_material_dict(self):
        dictionary = {}
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

        for k,v in dictionary.items():
            materiały = {k:[] for k,v in dictionary.items()}

        for item in self.all_geometry:                
            for key,ids in dictionary.items():        
                if ids[0] <= item.get_id() <= ids[1]:
                    materiały[key].append(str(item))
                else:
                    continue
        return materiały
    
    # def add_cuts(self):
    #     for item in self.any_primitive:
    #         print(item.get_id())
    #     for index,row in self.cuts.iterrows():
    #         if not row.isnull().all():
    #             print(row[0],row[1],row[2])
    #             shell1 = re.findall(r'\b\d+\b',row[1])
    #             shell2 = re.findall(r'\b\d+\b',row[2])
    #             print(shell1,shell2)

    #     else:
    #         return

    def fig_in_cuts(self,id_fig,id_in_cuts):
        return  id_fig == id_in_cuts

    def add_groups(self):
        materiały = self.make_material_dict()
        for materiał,lista in materiały.items():
            tekst = ' + '.join(lista)
            self.file.write(f"\n\nGEOMETRY {materiał};\n{materiał} = {tekst};")
            
    def add_hier(self):
        if self.hier_first_cols['Col4'].isna().all(): #Jeśli czwarta kolumna pusta
            self.result1 = self.helper_child_parent(self.hier_first_cols.loc[:,["Col2","Col3"]])
            for parent in self.result1:
                if not self.result1[parent]:
                   continue
                else:
                   lista = ' + '.join(self.result1[parent])
                   self.file.write(f"\nGEOMETRY {parent};\n{parent} = {lista};\n")

        else: #Jeśli jest czwarta kolumna
            self.result1 = self.helper_child_parent(self.hier_first_cols.loc[:,["Col3","Col4"]])
            self.result2 = self.helper_child_parent(self.hier_first_cols.loc[:,["Col2","Col3"]])
            for parent in self.result1:
                if not self.result1[parent]:
                    continue
                else:
                    lista = ' + '.join(self.result1[parent])
                    self.file.write(f"\nGEOMETRY {parent};\n{parent} = {lista};\n")

            for parent in self.result2:

                # print(parent)
                # print(self.result2[parent])

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
                children = colY[start:end+1].dropna().tolist()
                parents[ojciec] = children
            except:
                continue

        return(parents)
        
    def assembly(self):
        if self.hier_first_cols['Col4'].isna().all(): #Jeśli czwarta kolumna pusta
            lista = ' + '.join(self.result1)
            self.file.write(f"\n\n{self.modelname} = {lista};\n")
        else:
            lista = ' + '.join(self.result2)
            self.file.write(f"\n\n{self.modelname} = {lista};\n")

    def tekst(self,tekst):
        if tekst == "PODPIS":
            self.file.write("\n/*KONSTANTY KLOSIEWICZ*/\n")

        if tekst == "POINTS":
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