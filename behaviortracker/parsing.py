import os
import pandas as pd

default_factors = {
    'Genotype': {
        'WT': 'Wild Type',
        'KO': 'Knockout'
    },
    'Condition': {
        'Sedentary': 'Sedentary',
        'Exercise': 'Exercise'
    }
} 

def parse_name_from_dict(name, factors = default_factors):
    subject_factors = {}
    for factor in factors:
        levelCount = 0
        for level in factors[factor]:
            if level in name:
                levelCount += 1
                subject_factors[factor] = level
        if levelCount == 0:
            raise NameError('Subject {} has no level for factor {}'.format(name, factor))
        if levelCount > 1:
            raise NameError('Subject {} has {} levels for factor {}'.format(name, levelCount, factor))
    return subject_factors

def parse_file(path, parse_name = parse_name_from_dict):
    events = []
    _, subject_name = os.path.split(path)
    subject_factors = parse_name(subject_name)
    with open(path, 'r') as file:
        lines = file.readlines[3:]
        for i in range(len(lines)):
            line = lines[i].strip()
            if len(line) == 0:
                continue # Ignore empty lines
            line_record = parse_line(line, parse_name)

def parse_line(line, parse_name):
    parts = line.split(',')
    behavior = parts[0][1:-1].strip()
    status = parts[1].strip()
    latency = int(parts[4].strip())
    subject_name = parts[6].strip()
    factors = parse_name(subject_name)
        
    record = {
        'status': status,
        'behavior': behavior,
        'subject': subject_name,
        'factors': factors,
        'latency': latency
    }

    return record

def findMatchingEndRecord(lines, startRecord, startLine):
    j = startLine + 1
    while j < len(lines):
        if len(lines[j].strip()) <= 0:
            j = j + 1
            continue
        endRecord = parse_line(lines[j], lambda x: None)
        if (endRecord['status'] == 'Ended' and endRecord['behavior'] == startRecord['behavior']):
            break
        j = j + 1
    if j >= len(lines):
        print("Error: Record\n{}\nhas no matching 'Ended' record")
        exit()
    return endRecord