from unittest import TestCase

import behaviortracker
import os

class TestParsing(TestCase):
    # Dummy test for now
    def test_total(self):
        # Struggling should be 60, immobility 6
        experiment = behaviortracker.Experiment()
        dir, _ = os.path.split(__file__)
        experiment.add_file(os.path.join(dir, 'test_data_WT_Exercise.csv'))
        events = experiment.events_df()
        summed = events.groupby('Behavior').agg('sum').reset_index()
        immobilityDuration = list(summed[summed['Behavior'] == 'Immobility']['Duration'])[0]
        strugglingDuration = list(summed[summed['Behavior'] == 'Struggling']['Duration'])[0]
        self.assertEqual(immobilityDuration, 6)
        self.assertEqual(strugglingDuration, 60)
    def test_name_parsing_defaults(self):
        factors = behaviortracker.parse_name_from_dict('Sedentary WT 1-2')
        self.assertDictEqual(factors, {
            'Condition': 'Sedentary',
            'Genotype': 'WT'
        })
    