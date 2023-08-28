import pandas as pd
excel_path = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER\2_FCU_PSU_v03.xlsx"
data = pd.read_excel(excel_path,sheet_name="HIERARCHY",na_filter = True)
new_column_names = [f'Col{i+1}' for i in range(len(data.columns))]
parent_child_data = data[['Col3', 'Col4']].dropna()

# Tworzymy słownik, gdzie klucz to rodzic, a wartość to lista dzieci lub pusta lista
parent_child_dict = {}
for row in parent_child_data.itertuples(index=False):
    parent = row.Col3
    child = row.Col4
    if parent not in parent_child_dict:
        parent_child_dict[parent] = []
    if pd.notna(child):
        parent_child_dict[parent].append(child)

print(parent_child_dict)