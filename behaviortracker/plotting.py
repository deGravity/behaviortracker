from plotnine import *

def makePlot(experiment, behavior, factors=None):
    if factors == None:
        factors = experiment.get_factors()
    data = experiment.windowed_averaged_by_factor(factors)
    plot = (
        ggplot(aes(x='Window', y='Duration_mean', color='Genotype', shape='Condition'),
            data=data[data['Behavior']==behavior])
        + geom_point()
        + geom_line()
        + geom_errorbar(aes(ymin = 'Duration_error_min', ymax='Duration_error_max'))
    )
    return plot


def plotOverTime(experiment, windowSize, behavior, factors):
    return None

def barChart(experiment, behavior, factors)