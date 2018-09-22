import os
import pandas as pd
from .parsing import parse_file
from .parsing import parse_name_from_dict
from .parsing import is_bt_file
import numpy as np
from scipy import stats
import behaviortracker as bt

class Experiment():
    def __init__(self, factors = parse_name_from_dict):
        self.events = []
        self.dirty = True
        self.files = []
        if type(factors) == dict:
            self.factors = lambda name: parse_name_from_dict(name, factors)
        else:
            self.factors = factors
        self.__events_df__ = None
    
    def add_file(self, path):
        path = os.path.abspath(path)
        if os.path.isdir(path):
            self.add_dir(path)
        elif os.path.isfile(path):
            if path not in self.files:
                self.dirty = True
                self.events += parse_file(path, self.factors)
                self.files.append(path)
            else:
                raise RuntimeWarning('{} is already in the experiment, skipping.'.format(path))
        else:
            raise RuntimeWarning('{} does not exist, skipping.'.format(path))
    
    def add_dir(self, path):
        path = os.path.abspath(path)
        if os.path.isdir(path):
            all_paths = filter(lambda x: x.endswith('.csv'),os.listdir(path)) # Todo crawl and check for correct formatting
            for p in all_paths:
                file = os.path.join(path, p)
                if is_bt_file(file):
                    self.add_file(file)
        elif os.path.isfile(path):
            raise RuntimeWarning('{} is a file, not a directory. Adding as a file.')
            self.add_file(path)
        else:
            raise RuntimeWarning('{} does not exist, skipping.'.format(path))

    def events_df(self):
        if not self.dirty:
            return self.__events_df__
        self.__events_df__ =  pd.DataFrame(self.events)
        self.dirty = False
        return self.__events_df__
    
    def windowed(self, window_size = 60):
        return bt.window(self.events_df(), window_size)
    
    def get_factors(self):
        non_factors = ['Start', 'End', 'Duration', 'Subject', 'Behavior', 'Window']
        return list(filter(lambda col: col not in non_factors, self.events_df()))
    
    def summed_by_subject(self):
        df = self.events_df().drop(columns=['Start', 'End'])
        grouping_columns = list(filter(lambda col: col != 'Duration', df.columns))
        return df.groupby(grouping_columns).aggregate('sum').reset_index()
    
    def windowed_summed_by_subject(self, window_size = 60):
        return self.windowed(window_size)
    
    def averaged_by_factor(self, factors=None):
        if factors == None:
            factors = self.get_factors()
        df = self.summed_by_subject()
        grouping_columns = factors + ['Behavior']
        df = df.groupby(grouping_columns).aggregate([np.mean, np.std, stats.sem]).reset_index()
        df.columns = df.columns.map(Experiment.flattenHierarchicalCol)
        df['Duration_error_min'] = df['Duration_mean'] - df['Duration_sem']
        df['Duration_error_max'] = df['Duration_mean'] + df['Duration_sem']
        return df
    
    def windowed_averaged_by_factor(self, factors=None, window_size = 60):
        if factors == None:
            factors = self.get_factors()
        df = self.windowed(window_size)
        grouping_columns = factors + ['Behavior', 'Window']
        df = df.groupby(grouping_columns).aggregate([np.mean, np.std, stats.sem]).reset_index()
        df.columns = df.columns.map(Experiment.flattenHierarchicalCol)
        df['Duration_error_min'] = df['Duration_mean'] - df['Duration_sem']
        df['Duration_error_max'] = df['Duration_mean'] + df['Duration_sem']
        return df
    
    @staticmethod
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
