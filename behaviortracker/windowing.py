import pandas as pd
from behaviortracker import Experiment

def window(data, window_size = 60):
    if type(data) == pd.DataFrame:
        return window_df(data, window_size)
    elif type(data) == Experiment:
        return window_df(data.events_df(), window_size)

def window_df(events, windowSize):
    windowed_events = []
    columns = list(filter(lambda col: col != 'Start' and col != 'End' and col != 'Duration', events.columns))
    for i in events.index:
        startTime = events['Start'][i]
        endTime = events['End'][i]
        startWindow = int(startTime / windowSize)
        endWindow = int(endTime / windowSize)

        if (startWindow == endWindow):
            duration = endTime - startTime
        else:
            duration = windowSize - startTime % windowSize # duration remaining in starting window

            # Compute duration of behavior in last window and create a record
            finalWindowDuration = endTime % windowSize
            if finalWindowDuration > 0: # Only output a record if any time was spent in the ending window
                windowed_events.append(makeEventRecord(events, columns, i, endWindow, finalWindowDuration))
            
            # Add a record for each intermediate (full) window
            for window in range(startWindow+1, endWindow):
                windowed_events.append(makeEventRecord(events, columns, i, window, windowSize))
        # Output a record for the starting window if it is a non-zero amount of time
        if duration > 0:
            windowed_events.append(makeEventRecord(events, columns, i, startWindow, duration))
    df = pd.DataFrame(windowed_events)
    return df.groupby(columns + ['Window']).agg('sum').reset_index()

def makeEventRecord(events, columns, index, window, duration):
    record = {}
    for col in columns:
        record[col] = events[col][index]
    record['Window'] = window
    record['Duration'] = duration
    return record