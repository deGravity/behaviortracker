from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from scipy import stats

def anova(experiment, behavior, factors = None):
    if factors == None:
        factors = experiment.get_factors()
    events = experiment.summed_by_subject()
    events = events[events['Behavior'] == behavior]
    events = events[['Subject'] + factors + ['Duration']]

    factor_formulas = ['C({})'.format(factor) for factor in factors]
    formula = 'Duration ~ ' + '*'.join(factor_formulas)
    model = ols(formula, events)
    aov_table = anova_lm(model, typ=2)

    return (model, aov_table)


def windowed_anova(experiment, behavior, window, window_size = 60, factors = None):
    if factors == None:
        factors = experiment.get_factors()
    events = experiment.windowed_summed_by_subject()
    events = events[events['Window'] == window]
    events = events[events['Behavior'] == behavior]
    events = events[['Subject'] + factors + ['Duration']]

    factor_formulas = ['C({})'.format(factor) for factor in factors]
    formula = 'Duration ~ ' + '*'.join(factor_formulas)
    model = ols(formula, events)
    aov_table = anova_lm(model, typ=2)

    return (model, aov_table)