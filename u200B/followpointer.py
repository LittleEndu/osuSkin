import os
import sys


def normalize():
    extension = ".png"
    files = dict()
    for f in os.listdir("."):
        if f.startswith("followpoint-"):
            index = int(f[12:f.find(".")])
            files[index] = f
            extension = os.path.splitext(f)[1]

    target = 0
    for f in sorted(files.items()):
        os.rename(f[1],"followpoint-{}{}".format(target,extension))
        target += 1
    return target-1


start = sys.maxsize
end = 0
for i in os.listdir("."):
    if i.startswith("followpoint-"):
        index = int(i[12:i.find(".")])
        start = min(index, start)
        end = max(index, end)

if start > end:
    print("Seems your followpoint-X.png files are missing")
else:
    n = normalize()
    print("Found {} files".format(n+1))
    requested = int(input("How many files do you want to delete from the beginning.\n"
                          "Use negative if you want to delete from the end.\n"))
    start = 0 if requested > 0 else n+requested+1
    for i in os.listdir("."):
        if i.startswith("followpoint-{}.".format(start)):
            os.remove(i)
            start += 1
            if start >= requested > 0:
                break
    normalize()
    print("Done")

# TODO: Allow insertion and arbitrary deleting
