import json

bucketized = "/home/gappleto/Syncthing/MSU Notes/example.log.bucketized"
comparison = "/home/gappleto/Syncthing/MSU Notes/example.log.vc_ordered"

correct = total = 0

with open(bucketized, "r") as f:
    buckets = json.load(f)

with open(comparison, "r") as f:
    events = json.load(f)

for idx, bucket_1 in enumerate(buckets):
    for bucket_2 in buckets[idx + 1:]:
        for x in bucket_1:
            for y in bucket_2:
                if events.index(x) < events.index(y):
                    correct += 1
                total += 1

print(f"{correct:,}/{total:,} = {correct/total:.02%}")
