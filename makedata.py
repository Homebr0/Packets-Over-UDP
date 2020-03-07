# Released under the MIT License

import string
import random


def data(size, prefix="KiB", output="output.txt"):
    fout = open(output, 'w')

    if prefix == "KiB":
        chars = size * 1024
    elif prefix == "KB":
        chars = size * 1000
    elif prefix == "MB":
        chars = size * 1000 * 1000
    elif prefix == "MiB":
        chars = size * 1024 * 1024
    elif prefix == "GB":
        chars = size * 1000 * 1000 * 1000
    elif prefix == "GiB":
        chars = size * 1024 * 1024 * 1024
    elif prefix == "TB":
        chars = size * 1000 * 1000 * 1000 * 1000
    elif prefix == "TiB":
        chars = size * 1024 * 1024 * 1024 * 1024

    i = 0
    while i < chars:
        fout.write(random.choice(string.ascii_letters + "1234567890!?."))

        i += 1

    fout.close()

def fileName(size="UnknownSize"):
    constStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    a = random.choice(constStr)
    b = random.choice(constStr)
    c = random.choice(constStr)
    d = random.choice(constStr)

    return str(a + b + c + d + "_" + size + ".txt")



data(10, "MiB", fileName("10MB"))