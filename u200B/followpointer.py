import os
import sys

from PIL import Image
from itertools import takewhile


def normalize():
    extension = ".png"

    highest_digit = 0
    for f in os.listdir("."):
        if f.startswith("followpoint-"):
            extension = os.path.splitext(f)[1]
            highest_digit = max(highest_digit, len("".join(takewhile(str.isdigit, f[12:]))))

    for f in os.listdir("."):
        if f.startswith("followpoint-"):
            index = int("".join(takewhile(str.isdigit, f[12:])))
            extra_crap = ""
            while os.path.isfile(f"aaaaaaaaaaa-{str(index).rjust(highest_digit, '0')}{extra_crap}{extension}"):
                extra_crap += 'x'
            os.rename(f, f"aaaaaaaaaaa-{str(index).rjust(highest_digit, '0')}{extra_crap}{extension}")

    files = dict()
    for f in os.listdir("."):
        if f.startswith("aaaaaaaaaaa-"):
            print(f)
            index = int("".join(takewhile(str.isdigit, f[12:])))
            while index in files.keys():
                index += 1
            print(index)
            files[index] = f

    target = -1
    visible_start = -1
    visible_end = None

    for _, f in sorted(files.items()):
        target += 1
        img = Image.open(f)
        if img.size[0] < 2:
            if visible_start == target - 1:
                visible_start = target
            elif visible_end is None:
                visible_end = target
        img.close()
        os.rename(f, f"followpoint-{target}{extension}")

    if visible_end is None:
        visible_end = target + 1
    return target, visible_start, visible_end


start = sys.maxsize
end = 0
for i in os.listdir("."):
    if i.startswith("followpoint-"):
        index = int("".join(takewhile(str.isdigit, i[12:])))
        start = min(index, start)
        end = max(index, end)

if start > end:
    print("Seems your followpoint-X.png files are missing")
else:
    n, start, end = normalize()
    start_amount = start + 1
    visible_amount = end-start-1
    end_amount = n-end+1
    print(f"Found {n + 1} files.")
    print(f"{start_amount}:{visible_amount}:{end_amount}")
    print(f"{int(start_amount/(n+1)*100)}% : {int(visible_amount/(n+1)*100)}% : {int(end_amount/(n+1)*100)}%")
    print("They have been normalized")
