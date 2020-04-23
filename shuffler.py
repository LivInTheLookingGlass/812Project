from random import shuffle

filename = "/home/gappleto/Syncthing/MSU Notes/example.log"
with open(filename, 'r') as f:
    lines = f.readlines()

with open(filename + '.shuffled', 'w') as f:
    f.write(lines[0])
    lines = lines[1:]
    shuffle(lines)
    for line in lines:
        if line != '':
            f.write(line)
