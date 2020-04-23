from json import dumps, loads
from sys import argv


filepath = argv[-1]
events = []
NUM_NODES = 4
with open(filepath, 'r') as f:
    for idx, line in enumerate(f.readlines()):
        if idx:
            line = line[line.index(":")+1:-1]
            line = line[line.index(":")+1:]
            events.append(loads(line))

with open(filepath + '.hlc_ordered', 'w') as f:
    f.write(dumps(sorted(events, key=lambda event: event['hlc'])))
