import warnings
warnings.filterwarnings(
    "ignore",
    message="Data Validation extension is not supported and will be removed",
    category=UserWarning,
    module=r"openpyxl\.worksheet\._reader",
)
import pandas as pd
import re
from textwrap import dedent
from pathlib import Path
from src.geometry import Point, Primitive, Triangle, Rectangle


class ERG_Parser:

    def __init__(self, outputdir='output'):
        self.DFs = {"primitives":  None,
                    "cuts"      :  None,
                    "hierarchy" :  None,
                    "optical"   :  None,
                    "settings"  :  None,
                    "bulk"      :  None,
                    "mass"      :  None}
        self.all_geometry = []
        
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
                              DFs=self.DFs,
                              points=self.points,
                              geometry=self.all_geometry,
                              hier_first_cols=self.hier_first_cols,
                              outputdir=self.outputdir)
        
        creator.wrtie_ERG_file()
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
        na = True #Nan filter

        self.DFs["primitives"] = self.load_primitives(excelfile)
        self.DFs["hierarchy"], self.hier_first_cols, self.pid_index = self.load_hierarchy(excelfile)

        self.DFs["cuts"] = pd.read_excel(
            excelfile, sheet_name="CUTS", na_filter=na,
            usecols=["CUT Name", "SHELL 1", "SHELL 2"]
        )
                                                          
        self.DFs["bulk"] = pd.read_excel(
            excelfile, sheet_name="BULK", na_filter=na,
            usecols=["Bulk Name", "Density [Kg/m3]", "Specific heat [J/KgK]", "Thermal conductivity [w/mK]"]
        )

        self.DFs["optical"] = pd.read_excel(
            excelfile, sheet_name="OPTICAL", na_filter=na,
            usecols=["OPTICAL Name","ir_emiss","ir_refl","ir_trans","solar_abs","solar_ref",
                    "solar_trans","ir_spect_refl","solar_spect_refl","Control IR","Control Solar","Alp/Eps"]
        )

        self.DFs["settings"] = pd.read_excel(excelfile, sheet_name="Settings", na_filter = na)

        print("\nExcel data loaded succesfully")

    def load_primitives(self, excelfile, Filter = True):
        new_column_names = ["Primitives","node number","Config","Cutting","nodes 1","nodes 2","ratio1","ratio2","CAUTION"]
        primitives = pd.read_excel(excelfile, sheet_name="PRIMITIVES", na_filter = Filter)
        primitives = primitives.iloc[:,list(range(8)) + [9]]
        primitives.columns = new_column_names

        if not (primitives.loc[:,["Primitives","node number"]].isna().all().all() or 
               (primitives.loc[:,["Primitives","node number"]] == 0).all().all()):
            primitives['node number'] = primitives['node number'].apply(lambda x: str(x) if pd.notna(x) else x)
            # Deleting semicolons and dots
            primitives['node number'] = primitives['node number'].str.replace(r'\.0', '', regex=True)
            # Adding them back (optional)
            primitives['node number'] = primitives['node number'].apply(lambda x: int(x) if pd.notna(x) else x)
        
        return primitives

    def load_hierarchy(self, excelfile, Filter = True):
        hierarchy = pd.read_excel(excelfile,sheet_name="HIERARCHY",na_filter = Filter)
        pid_index = hierarchy.columns.get_loc("PID")
        hier_first_cols = hierarchy.iloc[:, 0:pid_index]
        hierarchy = hierarchy.loc[:,["nodenumbers of side 1","End Ids","offset","act1","act2","coat1","coat2","bulk1","bulk2","thick1","thick2","unity1","unity2","throughCond","conductance","emittance","mass1","mass2","crit1","crit2","color1","color2"]]

        new_column_names = [f'Col{i+1}' for i in range(len(hier_first_cols.columns))] 
        hier_first_cols.columns = new_column_names                                   
        hierarchy = pd.concat([hier_first_cols, hierarchy], axis = 1)       

        return hierarchy, hier_first_cols, pid_index

    def load_bdf_data(self, bdffile, debug=False):       

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
   
    def __init__(self, filename, modelname, DFs, points, geometry, hier_first_cols, outputdir="output"):
        print("Creating '.erg' file")

        self.modelname = modelname
        outputdir = Path(outputdir)
        outputdir.mkdir(parents=True, exist_ok=True)
        self.file_path = outputdir / f"{filename}.erg"

        self.points = points
        self.all_geometry = geometry
        self.hier_first_cols = hier_first_cols
        self.DFs = DFs
       
        self.shell1 = []
        self.shell2 = []

    def wrtie_ERG_file(self):
        self.transform_to_primitives()

        with self.file_path.open("w") as self.file:
            self.file.write(f"BEGIN_MODEL {self.modelname}\n")
            self.text_block("PODPIS")

            self.text_block("BULKS")
            self.add_bulks()

            self.text_block("OPTICAL")
            self.add_optics()

            self.text_block("POINTS")
            for p in self.points:
                x,y,z = p.get_pos()
                self.file.write(f"POINT point_{p.get_id()} = [{x}, {y}, {z}];\n")
            
            self.text_block("SHELLS")
            self.add_shells()

            self.text_block("START GROUP BLOCKS")
            # if not self.DFs["cuts"].empty:
            #     self.add_cuts()

            self.text_block("GROUPS")
            self.add_groups()

            self.text_block("HIERARCHY")
            self.add_hier()

            self.text_block("ASSEMBLY")
            self.assembly()

            self.text_block("END")

            print("Erg file created succesfully")

    def add_shells(self): 
        for figure in self.all_geometry:
            
            Id = figure.get_id()
            row_hierarchy = self.DFs["hierarchy"][self.DFs["hierarchy"].apply(self.check_id_hier, args=(Id,), axis=1)]
            
            if isinstance(figure,Triangle):
                block = f'''
                    GEOMETRY {figure};
                    {figure} = SHELL_TRIANGLE(
                    point1 = point_{figure.p1},
                    point2 = point_{figure.p2},
                    point3 = point_{figure.p3},
                    )
                    '''
                self.add_one_figure_hier(Id, row_hierarchy)

            elif isinstance(figure, Rectangle):
                block = f'''
                GEOMETRY {figure};
                {figure} = SHELL_QUADRILATERAL(
                point1 = point_{figure.p1},
                point2 = point_{figure.p2},
                point3 = point_{figure.p3},
                point4 = point_{figure.p4},
                )
                '''
                self.add_one_figure_hier(Id,row_hierarchy)

            elif isinstance(figure,Primitive):
                row_primitive = self.DFs["primitives"][self.DFs["primitives"].apply(self.check_id_prim, args=(Id,),axis=1)]
            
                if figure.node_num == 3:
                    block = f'''
                    GEOMETRY {figure};
                    {figure} = {figure.BIG()}(
                    point1 = point_{figure.p1},
                    point2 = point_{figure.p2},
                    point3 = point_{figure.p3},
                    )
                    '''
                
                elif figure.node_num == 4:
                    block = f'''
                    GEOMETRY {figure};
                    {figure} = {figure.BIG()}(
                    point1 = point_{figure.p1},
                    point2 = point_{figure.p2},
                    point3 = point_{figure.p3},
                    point4 = point_{figure.p4},
                    )
                    '''
                self.add_one_figure_prim(Id,row_primitive,row_hierarchy)
            
            else:
                raise ValueError("Unsupported node_num")
                    
            self.file.write(dedent(block))

    def transform_to_primitives(self):
        for index, item in enumerate(self.all_geometry):
            Id = item.get_id()
            row_primitive = self.DFs["primitives"][self.DFs["primitives"].apply(self.check_id_prim, args=(Id,),axis=1)]
            
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

    def add_one_figure_hier(self, moj_id, row_hierarchy):
        side1, side2 =   str(row_hierarchy["act1"]).strip(),   str(row_hierarchy["act2"]).strip()
        crit1, crit2 =   str(row_hierarchy["crit1"]).strip(),  str(row_hierarchy["crit2"]).strip()
        opt1, opt2 =     str(row_hierarchy["coat1"]).strip(),  str(row_hierarchy["coat2"]).strip()
        color1, color2 = str(row_hierarchy["color1"]).strip(), str(row_hierarchy["color2"]).strip()
        side1_cap, side2_cap = side1[:1].upper() + side1[1:].lower(),  side2[0].upper() + side2[1:].lower()

        bulk = str(row_hierarchy["bulk1"]).strip()
        cond = str(row_hierarchy["throughCond"]).strip()
        thick = f"{row_hierarchy['thick1'].iloc[0]:.8f}"

        block = f'''
            sense = 1,
            meshType1 = "regular",
            nodes1 = 1,
            ratio1 = 1.00000000,
            meshType2 = "regular",
            nodes2 = 1,
            ratio2 = 1.00000000,
            analysis_type = "Lumped Parameter",

            label1 = "",
            side1_cap = {side1_cap},
            criticality1 = {crit1},
            nbase1 = {moj_id},
            ndelta1 = 0,
            opt1 = {opt1},
            colour1 = {color1},

            label2 = "",
            side2 = {side2_cap},
            criticality2 = {crit2},
            nbase2 = {moj_id},
            ndelta2 = 0,
            opt2 = {opt2},
            colour2 = {color2},
            
            composition = "SINGLE",
            bulk = {bulk},
            thick = {thick},
            bulk1 = [-10000.00000000, -10000.00000000, -10000.00000000],
            thick1 = 0.00000000,
            bulk2 = [-10000.00000000, -10000.00000000, -10000.00000000],
            thick2 = 0.00000000,
            through_cond = {cond},
            conductance = 0.00000000,
            emittance = 0.00000000);
        '''
        self.file.write(dedent(block))
        
    def add_one_figure_prim(self, moj_id, row_primitive, row_hierarchy):
        
        rp = row_primitive.iloc[0]  if isinstance(row_primitive,  pd.DataFrame)  else row_primitive
        rh = row_hierarchy.iloc[0]  if isinstance(row_hierarchy,  pd.DataFrame)  else row_hierarchy

        cut = str(rp["Cutting"]).strip().upper()
        sense = 1 if cut == "OUTSIDE" else -1 if cut == "INSIDE" else 1

        nodes1, nodes2 = int(rp["nodes 1"]), int(rp["nodes 2"])
        ratio1, ratio2 = f'{float(rp["ratio1"]):.8f}', f'{float(rp["ratio2"]):.8f}'
        
        side1, side2 =   str(rh["act1"]).strip(),   str(rh["act2"]).strip()
        crit1, crit2 =   str(rh["crit1"]).strip(),  str(rh["crit2"]).strip()
        opt1, opt2 =     str(rh["coat1"]).strip(),  str(rh["coat2"]).strip()
        color1, color2 = str(rh["color1"]).strip(), str(rh["color2"]).strip()
        side1_cap, side2_cap = side1[:1].upper() + side1[1:].lower(),  side2[0].upper() + side2[1:].lower()

        bulk = str(rh["bulk1"]).strip()
        cond = str(rh["throughCond"]).strip()
        thick = f"{rh['thick1'].iloc[0]:.8f}"

        block = f"""
            sense = {sense},
            meshType1 = "regular",
            nodes1 = {nodes1},
            ratio1 = {ratio1},
            meshType2 = "regular",
            nodes2 = {nodes2},
            ratio2 = {ratio2},
            analysis_type = "Lumped Parameter",

            label1 = "",
            side1 = "{side1_cap}",
            criticality1 = "{crit1}",
            nbase1 = {moj_id},
            ndelta1 = 0,
            opt1 = {opt1},
            colour1 = "{color1}",

            label2 = "",
            side2 = "{side2_cap}",
            criticality2 = "{crit2}",
            nbase2 = {moj_id},
            ndelta2 = 0,
            opt2 = {opt2},
            colour2 = "{color2}",

            composition = "SINGLE",
            bulk = {bulk},
            thick = {thick},
            bulk1 = [-10000.00000000, -10000.00000000, -10000.00000000],
            thick1 = 0.00000000,
            bulk2 = [-10000.00000000, -10000.00000000, -10000.00000000],
            thick2 = 0.00000000,
            through_cond = {cond},
            conductance = 0.00000000,
            emittance = 0.00000000);
        """
        self.file.write(dedent(block))

    def add_bulks(self):
        materials = self.DFs["hierarchy"][['bulk1','bulk2']].stack().dropna().unique()

        for material in materials:
            row = self.DFs["bulk"].loc[self.DFs["bulk"]['Bulk Name'] == material]
            val1 = row["Density [Kg/m3]"].to_string(index=False)
            val2 = row["Specific heat [J/KgK]"].to_string(index=False)
            val3 = row["Thermal conductivity [w/mK]"].to_string(index=False)
            self.file.write(f"\nBULK {material} = [{format(float(val1),'.3f')}, {format(float(val2),'.3f')}, {format(float(val3),'.3f')}];")
        
    def add_optics(self):
        coats = self.DFs["hierarchy"][['coat1','coat2']].stack().dropna().unique()

        for coat in coats:
            row = self.DFs["optical"].loc[self.DFs["optical"]['OPTICAL Name'] == coat]
            val1 = row['ir_emiss'].to_string(index=False)
            val2 = row['ir_refl'].to_string(index=False)
            val3 = row['ir_trans'].to_string(index=False)
            val4 = row['solar_abs'].to_string(index=False)
            val5 = row['solar_ref'].to_string(index=False)
            val6 = row['solar_trans'].to_string(index=False)
            val7 = row['ir_spect_refl'].to_string(index=False)
            val8 = row['solar_spect_refl'].to_string(index=False)
            values = [val1,val2,val3,val4,val5,val6,val7,val8]
            text = ', '.join([format(float(i),'.6f') for i in values])
            self.file.write(f'\nOPTICAL {coat} = [{text}];')

    def make_material_dict(self):
        dictionary = {}
        for _ , row in self.DFs["hierarchy"].iterrows():
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
            materials = {k:[] for k,v in dictionary.items()}

        for item in self.all_geometry:                
            for key,ids in dictionary.items():        
                if ids[0] <= item.get_id() <= ids[1]:
                    materials[key].append(str(item))
                else:
                    continue
        return materials
    
    # def add_cuts(self):
    #     for item in self.any_primitive:
    #         print(item.get_id())
    #     for index,row in self.DFs["cuts"].iterrows():
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
        materials = self.make_material_dict()
        for material, lista in materials.items():
            text = ' + '.join(lista)
            self.file.write(f"\n\nGEOMETRY {material};\n{material} = {text};")
            
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
            text = ' + '.join(self.result1)
            self.file.write(f"\n\n{self.modelname} = {text};\n")
        else:
            text = ' + '.join(self.result2)
            self.file.write(f"\n\n{self.modelname} = {text};\n")

    def text_block(self, text : str):
        if text == "PODPIS":
            self.file.write("\n/*KONSTANTY KLOSIEWICZ*/\n")

        if text == "POINTS":
            self.file.write("\n/*--------------------------------------*/\n/*                 POINTS               */\n/*--------------------------------------*/\n")

        elif text == "OPTICAL":
            self.file.write("\n\n/*--------------------------------------*/\n/*          OPTICAL PROPERTIES          */\n/*--------------------------------------*/")

        elif text == "BULKS":
            self.file.write("\n/*--------------------------------------*/\n/*                 BULKS                */\n/*--------------------------------------*/")

        elif text == "SHELLS":
            self.file.write("\n/****************************************/\n/*      Start of geometry block         */\n/****************************************/\n\n/*--------------------------------------*/\n/*                 SHELLS               */\n/*--------------------------------------*/")

        elif text == "START GROUP BLOCKS":
            self.file.write("\n\n/****************************************/\n\n/****************************************/\n/*        Start of group block          */\n/****************************************/\n")

        elif text == "GROUPS":
            self.file.write("\n/*--------------------------------------*/\n/*                 GROUPS               */\n/*--------------------------------------*/")

        
        elif text == "HIERARCHY":
            self.file.write("\n\n/*--------------------------------------*/\n/*               HIERARCHY              */\n/*--------------------------------------*/")

        elif text == "ASSEMBLY":
            self.file.write("\n\n/*--------------------------------------*/\n/*               ASSEMBLY               */\n/*--------------------------------------*/")

        elif text == "END":
            self.file.write("\n/****************************************/\n\nPURGE_MODEL();\nEND_MODEL")