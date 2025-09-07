#!/usr/bin/env python3

import json
import sys
from collections import defaultdict

def preprocess_rules(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    unified_rules = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))

    for bucket, patterns in data.items():
        for pattern in patterns:
            if ',' in pattern:
                pattern, op = pattern.split(',')
            else:
                op = '*'

            if '.' in pattern:
                receiver, member = pattern.split('.', 1)
            else:
                receiver, member = pattern, '*'

            unified_rules[receiver][member][op] = bucket

    unified_rules = {k: {sk: dict(sv) for sk, sv in v.items()} for k, v in unified_rules.items()}

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unified_rules, f, indent=4)

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    preprocess_rules(input_file, output_file)
