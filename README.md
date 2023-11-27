# ESATAN-Parser
Is program developed to simplify workflow in the ESATAN software. User interface let combine geometry model from BDF format with Excel sheet with necessary material details to ERG format. 
This improves forkflow in thermal analysis because we skip creating model in clunky ESATAN software and go straight to thermal cases.


## Instruction
Program is divided in two parts, that can be used separately. PARSER contains class that converts data from two files .xls sheet and .bdf model. It is recommended to use it via PARSER-GUI to avoid further problems 
with moving files to another folders. ESATAN-TMS requires specific folders to exist and contain models and thermal-cases, but PARSER-GUI detects them and transfer files automatically after converting files to .erg format.
