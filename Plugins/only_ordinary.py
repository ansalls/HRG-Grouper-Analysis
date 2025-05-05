'''
This plugin is used to filter out non inpatient activity.
Named as such because the zl output is always 1 for inpatient activity but what
the plug in is actually acheiving this by filtering out non-ordinary activity,
which is not intuitively or normally the same thing.
'''
import pandas as pd
from Plugins.base_plugin import BasePlugin

class OnlyInpatientPlugin(BasePlugin):
    '''
    Filter to keep only inpatient base class activity.

    Includes:
    - 1: Ordinary admission
    - 2: Day case admission
    - 3: Regular day attender
    - 4: Regular night attender
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[df['CLASSPAT'].isin(['1', '2', '3', '4'])]

        return df
