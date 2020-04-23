from json import dumps, loads

filepath = "/home/gappleto/Syncthing/MSU Notes/example.log"
events = []
NUM_NODES = 4
with open(filepath, 'r') as f:
    for idx, line in enumerate(f.readlines()):
        if idx:
            line = line[line.index(":")+1:-1]
            line = line[line.index(":")+1:]
            events.append(loads(line))

buckets = [[]]
curr_group = "send"
for event in events:
    if event[curr_group]:
        buckets[-1].append(event)
    else:
        if curr_group == "send":
            curr_group = "recv"
        elif curr_group == "recv":
            curr_group = "send"
        buckets.append([event])
with open(filepath + '.bucketized', 'w') as f:
    f.write(dumps(buckets))