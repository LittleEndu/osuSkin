import pathlib
import re

from PIL import Image

current_alpha = {}

for i in pathlib.Path('.').iterdir():
    match = re.match(r"followpoint-(\d+)(@2x)?\.png$", i.name)
    if match:
        nr = int(match.groups()[0])
        with Image.open(i).convert('RGBA') as img:
            _, _, _, aa = img.split()
        aa_max = max(aa.getdata())
        current_alpha[nr] = aa_max

alpha_list = [v for _, v in sorted(current_alpha.items(), key=lambda a: a[0])]

img = Image.new("L", (len(alpha_list), 1))
img.putdata(alpha_list)
index = 0

img.save(f'followpoint-alpha.png')
