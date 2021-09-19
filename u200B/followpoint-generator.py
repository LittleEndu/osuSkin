import random

from PIL import Image

HEIGHT = 32
WIDTH = 352
COLOR = (255, 255, 255)
AP = 4  # Aliased pixels


def anti_aliasing(y, a):
    m = 1 if AP <= y < HEIGHT - AP else (
        (y + 1) / (AP + random.random()) if y < AP else (HEIGHT - y) / (AP + random.random()))
    return m * a


def alpha_rand(a):
    return int(max(0, min(255, a + random.randint(-2, 2))))


def alpha_func(x):
    if x % 3 == 0:
        return min(1, x + 0.3)

    if x < 0.66:
        return x ** 1.5 * 2
    return x ** 0.5


with Image.open('followpoint-alpha.png').convert('L') as img:
    alpha_time = list(img.getdata())

alpha_band = [int(alpha_func((i + 1) * 2 / WIDTH) * 233) for i in range(int(WIDTH / 2))]
alpha_band.sort()
alpha_band += alpha_band[::-1]

full_alpha = Image.new("RGB", (WIDTH, HEIGHT), COLOR)
r, g, b = full_alpha.split()
a = Image.new("L", (WIDTH, HEIGHT))
data = alpha_band * HEIGHT
data = [int(anti_aliasing(n // WIDTH, i)) for n, i in enumerate(data)]
a.putdata(data)
a.save('followpoint-mask.png')

for n, i in enumerate(alpha_time):
    this_alpha = a.point(lambda a: alpha_rand(a * i / 255))
    img = Image.merge("RGBA", (r, g, b, this_alpha))
    img.save(f"followpoint-{n}@2x.png")
