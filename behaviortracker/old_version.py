from os import listdir
from sys import argv
import pandas as pd
from plotnine import *
import numpy as np
from scipy import stats
import argparse
from os import path


def group_data_by_mouse(data):
    byMouse = (data.groupby(['Mouse','Genotype', 'Condition','Behavior','Window'])
        .agg('sum').reset_index()
    )
    return (byMouse.sort_values('Window', kind='mergesort')
        .sort_values('Mouse', kind='mergesort')
        .sort_values('Behavior', kind='mergesort')
        .sort_values('Condition', kind='mergesort')
    )

def flattenHierarchicalCol(col,sep = '_'):
    if not type(col) is tuple:
        return col
    else:
        new_col = ''
        for leveli,level in enumerate(col):
            if not level == '':
                if not leveli == 0:
                    new_col += sep
                new_col += level
        return new_col

def group_and_average_data(data):
    byMouse = group_data_by_mouse(data)
    byWindow = byMouse.groupby(['Genotype', 'Condition', 'Behavior', 'Window']).aggregate([np.mean, np.std, stats.sem]).reset_index()
    byWindow.columns = byWindow.columns.map(flattenHierarchicalCol)
    byWindow['Duration_error_min'] = byWindow['Duration_mean'] - byWindow['Duration_sem']
    byWindow['Duration_error_max'] = byWindow['Duration_mean'] + byWindow['Duration_sem']
    return byWindow

def makePlot(events, behavior):
    data = group_and_average_data(events)
    plot = (
        ggplot(aes(x='Window', y='Duration_mean', color='Genotype', shape='Condition'),
            data=data[data['Behavior']==behavior])
        + geom_point()
        + geom_line()
        + geom_errorbar(aes(ymin = 'Duration_error_min', ymax='Duration_error_max'))
    )
    return plot

def parseLine(line):
    parts = line.split(',')
    behavior = parts[0][1:-1].strip()
    status = parts[1].strip()
    latency = int(parts[4].strip())
    mouse = parts[6].strip()
    genotype = 'WT'
    if "5AR2KO" in mouse:
        genotype = '5AR2KO'
    condition = "Exercise"
    if "Sedentary" in mouse:
        condition = "Sedentary"
        
    record = {
        'status': status,
        'mouse': mouse,
        'condition': condition,
        'genotype': genotype,
        'behavior': behavior,
        'latency': latency
    }

    return record

def findMatchingEndRecord(lines, startRecord, startLine):
    j = startLine + 1
    while j < len(lines):
        if len(lines[j].strip()) <= 0:
            j = j + 1
            continue
        endRecord = parseLine(lines[j])
        if (endRecord['status'] == 'Ended' and endRecord['behavior'] == startRecord['behavior']):
            break
        j = j + 1
    if j >= len(lines):
        print("Error: Record\n{}\nhas no matching 'Ended' record")
        exit()
    return endRecord

def makeEventRecord(record, window, duration):
    return {
        'mouse': record['mouse'],
        'condition': record['condition'],
        'genotype': record['genotype'],
        'behavior': record['behavior'],
        'window': window,
        'duration': duration
    }

def bucketData(sourceFiles, windowSize):
    events = []
    for file in sourceFiles:
        with open(file, 'r') as file:
            lines = file.readlines()
            for i in range(3, len(lines)):
                line = lines[i]
                if len(line.strip()) == 0:
                    continue
                record = parseLine(line)
                if record['status'] == 'Started':
                    endRecord = findMatchingEndRecord(lines, record, i)
                    startTime = record['latency']
                    endTime = endRecord['latency']
                    startWindow = int(startTime / windowSize)
                    endWindow = int(endTime / windowSize)

                    if (startWindow == endWindow):
                        duration = endTime - startTime
                    else:
                        duration = windowSize - startTime % windowSize # duration remaining in starting window

                        # Compute duration of behavior in last window and create a record
                        finalWindowDuration = endTime % windowSize
                        if finalWindowDuration > 0: # Only output a record if any time was spent in the ending window
                            events.append(makeEventRecord(record, endWindow, finalWindowDuration))
                        
                        # Add a record for each intermediate (full) window
                        for window in range(startWindow+1, endWindow):
                            events.append(makeEventRecord(record, window, windowSize))
                    # Output a record for the starting window if it is a non-zero amount of time
                    if duration > 0:
                        events.append(makeEventRecord(record, startWindow, duration))
    return events

def eventsToDataFrame(events):
    mouse = []
    condition = []
    genotype = []
    behavior = []
    window = []
    duration = []
    for event in events:
        mouse.append(event['mouse'])
        condition.append(event['condition'])
        genotype.append(event['genotype'])
        behavior.append(event['behavior'])
        window.append(event['window'])
        duration.append(event['duration'])
    data = {
        'Mouse': mouse,
        'Condition': condition,
        'Genotype': genotype,
        'Behavior': behavior,
        'Window': window,
        'Duration': duration
    }

    return pd.DataFrame(data)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process data exported from Behaviortracker.')
    # source dir (default .)
    # windowed csv output file (windowed.csv)
    # window duration (60 seconds)
    # plot behavior (-p Struggling)
    # group by mouse
    # averaged data output
    parser.add_argument('-s', '--source', nargs='+')
    parser.add_argument('-o', '--output', default='bt')
    parser.add_argument('-g', '--graph', nargs='+')
    parser.add_argument('-p', '--period', default=60, type=int)
    parser.add_argument('-w', '--windowedfile', action='store_true')
    parser.add_argument('-m', '--mousefile', action='store_true')
    parser.add_argument('-a', '--averagedfile', action='store_true')

    options = parser.parse_args()

    print(options)

    if options.source == None:
        options.source = ['.']
    sourceFiles = []
    for source in options.source:
        if path.isfile(source):
            sourceFiles.append(source)
        elif path.isdir(source):
            sourceFiles.extend(filter(lambda x: x.endswith('.csv'),listdir(source)))
        else:
            print('Error: {} is not a valid file or directory.'.format(source))
            exit()

    events = eventsToDataFrame(bucketData(sourceFiles, options.period))

    if options.windowedfile:
        windowFileName = options.output + '_windowed.csv'
        events.to_csv(windowFileName)
    
    if options.mousefile:
        mouseFileName = options.output + '_by_mouse.csv'
        byMouse = group_data_by_mouse(events)
        byMouse.to_csv(mouseFileName)
    
    if options.averagedfile:
        averagedFileName = options.output + '_averaged.csv'
        averaged = group_and_average_data(events)
        averaged.to_csv(averagedFileName)
    
    if options.graph != None:
        for behavior in options.graph:
            plot = makePlot(events, behavior)
            plotName = options.output + '_' + behavior + '_plot.png'
            plot.save(plotName)

    
