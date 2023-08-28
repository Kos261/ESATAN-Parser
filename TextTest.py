
import pandas as pd

data = [
    [None, None, None, None],
    [None, "PSU_MZ", None, None],
    [None, None, "PSU_FRAME_MZ", None],
    [None, None, None, "PSU_FR_ST_MZ_1_5"],
    [None, None, None, "PSU_FR_ST_MZ_2"],
    [None, None, None, "PSU_FR_ST_MZ_2_2"],
    [None, None, None, "PSU_FR_ST_MZ_3"],
    [None, None, None, "PSU_FR_WDG_MZ_PX"],
    [None, None, None, "PSU_FR_WDG_MZ_MX"],
    [None, None, None, "PSU_IF_DCDC_MZ"],
    [None, None, None, "PSU_FR_ST_MZ_6"],
    [None, None, "PSU_CMD_MZ", None],
    [None, None, "PSU_PCB_MZ", None],
    [None, None, "PSU_FP_MZ", None],
    [None, None, "PSU_NVENT_MZ", None],
    [None, None, None, "PSU_NVENT_MZ_PX"],
    [None, None, None, "PSU_NVENT_MZ_MX"],
    [None, None, "PSU_SND_MZ", None],
    [None, None, "DPU_COMP_MZ", None],
    [None, None, None, "PSU_MZ_DC_1"],
    [None, None, None, "PSU_MZ_DC_2"],
    [None, None, None, "D2_MZ"],
    [None, None, None, "D3_MZ"],
    [None, None, None, "D4_MZ"],
    [None, None, None, "D5_MZ"],
    [None, None, None, "D6_MZ"],
    [None, None, None, "D7_MZ"],
    [None, None, None, "U12A_MZ"],
    [None, None, None, "U6C_MZ"],
    [None, None, None, "X1_MZ"],
    [None, None, None, "U1_MZ"],
    [None, "PSU_PZ", None, None],
    [None, None, "PSU_FRAME_PZ", None],
    [None, None, None, "PSU_FR_ST_PZ_1_5"],
    [None, None, None, "PSU_FR_ST_PZ_2"],
    [None, None, None, "PSU_IF_DCDC_PZ"],
    [None, None, None, "PSU_FR_ST_PZ_6"],
    [None, None, "PSU_CMD_PZ", None],
    [None, None, "PSU_PCB_PZ", None]
]
df = pd.DataFrame(data)



hierarchy = {}

for row in df.iterrows():
    parent = hierarchy
    for item in row:
        if pd.notna(item):
            parent[item] = {}
            parent = parent[item]

print(hierarchy)







model = "FCU_PSU_v03"
