# This script re-orders the events in a log based on the provided vector clock data
# To run, call like "python vc_orderer.py <log name>"
# It will produce a file called <log name>.vc_ordered
from collections import defaultdict
from json import dumps, loads
from sys import argv


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


filepath = argv[-1]
events = []
with open(filepath, 'r') as f:
    for idx, line in enumerate(f.readlines()):
        if idx:
            line = line[line.index(":")+1:-1]
            line = line[line.index(":")+1:]
            events.append(loads(line))


ordered_events = []
sums = defaultdict(list)
NUM_NODES = len(events[0]['vc'])
for event in events:
    sums[sum(event['vc'])].append(event)

del events

max_sum = max(sums.keys())
for key in sorted(sums.keys()):
    curr_events = sums[key]
    if len(curr_events) == 1:
        ordered_events.extend(curr_events)
    else:
        # relevant = tuple(event['vc'] for event in curr_events)
        # sort_reference = tuple(x for x in lattice_with_sum(NUM_NODES, key) if x in relevant)
        # ordered_events.extend(sorted(curr_events, key=lambda event: sort_reference.index(event['vc'])))
        ordered_events.extend(sorted(curr_events, key=lambda event: event['vc']))
    del sums[key]  # try to reduce memory load somewhat

with open(filepath + '.vc_ordered', 'w') as f:
    f.write(dumps(ordered_events))
