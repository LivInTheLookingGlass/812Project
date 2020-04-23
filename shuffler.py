from random import shuffle
from sys import argv

filename = argv[-1]
with open(filename, 'r') as f:
    lines = f.readlines()

with open(filename + '.shuffled', 'w') as f:
    f.write(lines[0])
    lines = lines[1:]
    shuffle(lines)
    for line in lines:
        if line != '':
            f.write(line)
