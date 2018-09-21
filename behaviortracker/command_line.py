import behaviortracker
import argparse
from os import path

def main():
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
    parser.add_argument('-f', '--factor', action='append', nargs='+')

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

    #events = eventsToDataFrame(bucketData(sourceFiles, options.period))

    if options.windowedfile:
        windowFileName = options.output + '_windowed.csv'
        #events.to_csv(windowFileName)
    
    if options.mousefile:
        mouseFileName = options.output + '_by_mouse.csv'
        #byMouse = group_data_by_mouse(events)
        #byMouse.to_csv(mouseFileName)
    
    if options.averagedfile:
        averagedFileName = options.output + '_averaged.csv'
        #averaged = group_and_average_data(events)
        #averaged.to_csv(averagedFileName)
    
    if options.graph != None:
        for behavior in options.graph:
            #plot = makePlot(events, behavior)
            plotName = options.output + '_' + behavior + '_plot.png'
            #plot.save(plotName)