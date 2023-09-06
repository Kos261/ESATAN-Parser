import pandas as pd
import re

tekst1 = "GRID      720008       0  -.0225-9.966-3.9274056       0"
tekst2 = "GRID      720049       0  -5.-3.0465932.8940374       0"
tekst3 = "GRID           9       0-.060285-.054981      0.       0"

          #.123         -5.123-3              ' '0.' '    -5.-3
regex = r'([+-]?\.\d+)|(([+-]?\d\.\d+)-(\d))|(\s0\.\s)|(([+-]?\d\.)-(\d))'
liczba1 = re.findall(regex,tekst1)
liczba2 = re.findall(regex,tekst2)
liczba3 = re.findall(regex,tekst3)
print(liczba1)
print(liczba2)
print(liczba3)