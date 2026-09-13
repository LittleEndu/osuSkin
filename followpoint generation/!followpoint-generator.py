import random
from pathlib import Path

from PIL import Image
import numpy as np

OUTPUT_PATH = Path('out')
TARGET_MASK = Image.open('followpoint-mask.png').convert('L')

HEIGHT = 16  # 32
WIDTH = 352
COLOR = (255, 255, 255)

START = 17
PEAK = 25
END = 54
FINAL = 64

GRAPH_FUNC = np.linspace

alpha_timing = np.concatenate((
    np.zeros(START),
    GRAPH_FUNC(0, 1, PEAK - START),
    GRAPH_FUNC(1, 0, END - PEAK),
    np.zeros(FINAL - END)
))

# blank canvas shape (HEIGHT, WIDTH, FINAL)
canvas = np.zeros((HEIGHT, WIDTH, FINAL), np.bool_)

# make ramp-up part
for i in range(START, PEAK):
    target = alpha_timing[i] * WIDTH * HEIGHT
    attempt = 0
    while np.sum(canvas[:, :, i]) < target:
        attempt += 1
        if attempt % 7270 == 0:
            print(f"ramp up {i} attempt {attempt}")
        # select random coord
        x = int(random.randint(0, WIDTH - 1) * random.random())
        y = random.randint(0, HEIGHT - 1)
        decider = random.random()
        if decider > TARGET_MASK.getpixel((x, y)) / 255:
            # the logic here is it's now likely to hit high L areas
            # if we chose low L coord but `decider` was high, we skip
            continue
        if canvas[y, x, i]:
            # try again but not weighted
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
        if canvas[y, x, i]:
            continue
        # set every pixel on that coord from this frame onwards'
        canvas[y, x, i:] = True

# make ramp-down part
for i in range(PEAK, END):
    target = alpha_timing[i] * WIDTH * HEIGHT
    attempt = 0
    while np.sum(canvas[:, :, i]) > target:
        attempt += 1
        if attempt % 7270 == 0:
            print(f"ramp down {i} attempt {attempt}")
        x = int(random.randint(0, WIDTH - 1) * random.random())
        y = random.randint(0, HEIGHT - 1)
        decider = random.random()
        if decider < TARGET_MASK.getpixel((x, y)) / 255:
            # reverse logic here
            continue
        if not canvas[y, x, i]:
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
        if not canvas[y, x, i]:
            continue

        canvas[y, x, i:] = False

# turn into frames
OUTPUT_PATH.mkdir(exist_ok=True)
blank_frame = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
blank_frame[:, :, :3] = COLOR

for i in range(FINAL):
    print(f"saving {i}")
    this_frame = blank_frame.copy()
    this_alpha = canvas[:, :, i].astype(np.uint8) * 255
    this_frame[:, :, 3] = this_alpha
    # save to the output path
    Image.fromarray(this_frame).save(OUTPUT_PATH / f'followpoint-{i}@2x.png')
