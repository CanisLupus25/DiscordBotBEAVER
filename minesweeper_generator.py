import string

import numpy
import random

import numpy as np

ROLLS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
SYMBOLS = open('SYMBOLS.txt', encoding='UTF-8').read().split()
SPOILER = '||'
SEP = ''
HEADER = ''


def generate_field(size: int, mines: int):
    shape = (size + 2, size + 2)
    field_mines = numpy.zeros(shape, dtype=np.uint8)
    field_neighbs = field_mines.copy()
    bombs = random.sample(range(size * size), mines)
    for i in bombs:
        field_mines[i // size + 1, i % size + 1] = 1
    field_neighbs = sum([np.roll(field_mines, i, axis=(0, 1)) for i in ROLLS])
    np.putmask(field_neighbs, field_mines == 1, 9)
    cutten_field = field_neighbs[1:size + 1, 1:size + 1]
    string_field = ''
    for i in range(size):
        string_field += HEADER
        for j in range(size):
            string_field += f"{SPOILER}{SYMBOLS[cutten_field[i, j]]}{SPOILER}"
        string_field += '\n'
    return string_field


if __name__ == '__main__':
    print(generate_field(10, 10))
