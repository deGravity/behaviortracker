import behaviortracker
import argparse
import os

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
    parser.add_argument('-s', '--subjectfile', action='store_true')
    parser.add_argument('-a', '--averagedfile', action='store_true')
    parser.add_argument('-f', '--factor', action='append', nargs='+')

    options = parser.parse_args()

    if options.source == None:
        options.source = ['.']
    sourceFiles = []
    for source in options.source:
        if os.path.isfile(source):
            sourceFiles.append(source)
        elif os.path.isdir(source):
            sourceFiles.extend(filter(lambda x: x.endswith('.csv'),os.listdir(source)))
        else:
            raise RuntimeError('Error: {} is not a valid file or directory.'.format(source))
    
    if options.factor == None or len(options.factor) == 0:
        factors = behaviortracker.parse_name_from_dict
    else:
        factors_dict = {}
        for cond in factors:
            levels = {}
            for level in cond[1:]:
                levels[level] = level
            factors_dict[cond[0]] = levels
        factors = lambda subject: behaviortracker.parse_name_from_dict(subject, factors_dict)
    
    experiment = behaviortracker.Experiment(factors)
    for path in sourceFiles:
        experiment.add_file(path)
    
    if options.subjectfile:
        subjectFileName = options.output + '_by_subject.csv'
        experiment.windowed_summed_by_subject(options.period).to_csv(subjectFileName)
    
    if options.averagedfile:
        averagedFileName = options.output + '_averaged.csv'
        experiment.windowed_averaged_by_factor(options.period).to_csv(averagedFileName)
    
    if options.graph != None:
        for behavior in options.graph:
            #plot = makePlot(events, behavior)
            plotName = options.output + '_' + behavior + '_plot.png'
            #plot.save(plotName)
