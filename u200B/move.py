import os
for f in os.listdir():
    if "@2x" in f:
        os.rename(f,"at2x/{}".format(f))