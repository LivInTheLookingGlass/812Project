from collections import defaultdict
from json import dumps, loads
from sys import stdout


def lattice_with_sum(n, s):
    if n == 1:
        yield [s]
        return
    if s == 0:
        yield [0] * n
        return
    for x in range(s + 1):
        for partial in lattice_with_sum(n - 1, s - x):
            yield [x, *partial]


filepath = "/home/gappleto/Syncthing/MSU Notes/example.log"
events = []
NUM_NODES = 4
with open(filepath, 'r') as f:
    for idx, line in enumerate(f.readlines()):
        if idx:
            line = line[line.index(":")+1:-1]
            line = line[line.index(":")+1:]
            events.append(loads(line))


ordered_events = []
sums = defaultdict(list)
for event in events:
    sums[sum(event['vc'])].append(event)

max_sum = max(sums.keys())
for key in sorted(sums.keys()):
    print(f"Doing sum {key}/{max_sum}")
    stdout.flush()
    curr_events = sums[key]
    if len(curr_events) == 1:
        ordered_events.extend(curr_events)
    else:
        sort_reference = tuple(lattice_with_sum(NUM_NODES, key))  # this takes a crapton of memory
        ordered_events.extend(sorted(curr_events, key=lambda event: sort_reference.index(event['vc'])))
    del sums[key]  # try to reduce memory load somewhat

with open(filepath + '.vc_ordered', 'w') as f:
    f.write(dumps(events))
