
import re

text = r"C:\Users\koste\OneDrive\Pulpit\ESATAN_PARSER\Wynikmoj"

result = re.findall(r'[^\\]+',text)
print(result[-1])