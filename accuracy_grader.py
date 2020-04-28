# This script assesses the accuracy of a re-ordered log
# To run, call like "python accuracy_grader.py <bucketized log> <ordered log>"
import json
from sys import argv

bucketized = argv[-2]
comparison = argv[-1]

oracle_correct = causal_correct = wrong = 0

with open(bucketized, "r") as f:
    buckets = json.load(f)

with open(comparison, "r") as f:
    events = json.load(f)

for idx, bucket_1 in enumerate(buckets):
    for bucket_2 in buckets[idx + 1:]:
        for x in bucket_1:
            for y in bucket_2:
                if events.index(x) < events.index(y):
                    oracle_correct += 1
                elif 'hlc' in comparison:
                    if x['hlc'] >= y['hlc']:
                        causal_correct += 1
                    else:
                        wrong += 1
                elif 'vc' in comparison:
                    if not (all(a >= b for a, b in zip(x['vc'], y['vc'])) and any(a > b for a, b in zip(x['vc'], y['vc']))):  # first test is less expensive, but has false negatives
                        causal_correct += 1
                    else:
                        wrong += 1

print(f"{oracle_correct:,} / {causal_correct:,} / {wrong:,}")
