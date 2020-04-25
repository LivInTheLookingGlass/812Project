# This script re-orders the events in a log at random
# To run, call like "python shuffler.py <log name>"
# It will produce a file called <log name>.shuffled
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
