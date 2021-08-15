import os
from PIL import Image

for i in os.listdir():
    if i.startswith('followpoint-'):
        print(i)
        img = Image.open(i)
        if img.size[0] < 2:
            print('skip')
            continue
        out = Image.new('RGBA', (img.size[0], img.size[1] + 2))
        out.paste(img, (0, 1))
        alpha = img.crop((0, 0, img.size[0], 1))
        alpha.putdata([i[:3] + (int(i[3]*0.4),) for i in alpha.getdata()])
        out.paste(alpha, (0, 0))
        out.paste(alpha, (0, out.size[1]-1))
        img.close()
        out.save(i)
        print('done')
