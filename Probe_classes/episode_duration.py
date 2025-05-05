'''
    Class for episode duration.
'''
from Utils.constants import MAX_EPISODE_DURATION
from Probe_classes.probe import Probe

class EpisodeDuration(Probe):
    '''
    Class for episode duration.
    '''
    @classmethod
    def column_name(cls) -> str:
        return "EPIDUR"

    @classmethod
    def probe_values(cls) -> list[int]:
        '''
        Idea here is to take all days up to month+1, then 5 days up to 100,
        then 25 days up to 500, then 500 days up to 1000, then 1000 days up
        to 2000, then 10000 days up to max.
        This should give us enough granularity around likely cutoff points
        to dig deeper into those points without having to probe every single
        possible value between 0 and MAX_EPISODE_DURATION (99999).
        '''
        return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                28, 29, 30, 31, 32,
                40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100,
                105, 110, 115, 120, 125, 130, 135, 140, 145, 150,
                175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425,
                450, 475, 500,
                1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
                10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000,
                MAX_EPISODE_DURATION]
