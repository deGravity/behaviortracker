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
            raise RuntimeError('Subject {} has no level for factor {}'.format(name, factor))
        if levelCount > 1:
            raise RuntimeError('Subject {} has {} levels for factor {}'.format(name, levelCount, factor))
    return subject_factors

def parse_file(path, parse_name = parse_name_from_dict):
    events = []
    _, subject_name = os.path.split(path)
    subject_factors = parse_name(subject_name)
    with open(path, 'r') as file:
        lines = file.readlines()[3:]
        for i in range(len(lines)):
            line = lines[i].strip()
            if len(line) == 0:
                continue # Ignore empty lines
            line_record = parse_line(line, parse_name)
            line_factors = parse_name(line_record['subject'])
            if subject_factors != line_factors:
                raise RuntimeError('File "{}" contains lines with factors different from its filename.'.format(path))
            if line_record['status'] == 'Started':
                start_record = line_record
                end_record = find_matching_end_record(lines, start_record, i)
                duration = end_record['latency'] - start_record['latency']
                event = {
                    'Subject': start_record['subject'],
                    'Behavior': start_record['behavior'],
                    'Start': start_record['latency'],
                    'End': end_record['latency'],
                    'Duration': duration
                }
                for factor in subject_factors:
                    event[factor] = subject_factors[factor]
                events.append(event)
    return events

def is_bt_file(f):
    with open(f, 'r') as file:
        lines = file.readlines()
    return lines[0].startswith("'Behavior Name', 'Status', 'Time Stamp', 'Milliseconds', 'Latency', 'Milliseconds', 'File Name', 'Modifier'")

def parse_line(line, parse_name):
    parts = line.split(',')
    behavior = parts[0].strip()
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

def find_matching_end_record(lines, start_record, start_line):
    j = start_line + 1
    while j < len(lines):
        if len(lines[j].strip()) <= 0:
            j = j + 1
            continue
        end_record = parse_line(lines[j], lambda x: None)
        if (end_record['status'] == 'Ended' and end_record['behavior'] == start_record['behavior']):
            break
        j = j + 1
    if j >= len(lines):
        raise RuntimeError('Error: Record\n{}\nhas no matching "Ended" record'.format(lines[start_line]))
    return end_record