'''
    This module defines the base plugin class that all data transformation
    plugins should inherit from.
'''
import pandas as pd

class BasePlugin:
    '''
    A base plugin class that defines the expected structure
    of any data transformation plugin.

    Each plugin should have a "transform(dataframe)" method that
    takes a pandas dataframe and returns a transformed dataframe.
    '''
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
            This method should be overridden by subclasses to provide
            the desired transformation of the input DataFrame.

            Parameters:
            -----------
            df : pd.DataFrame
                The input DataFrame to be transformed.

            Returns:
            --------
            pd.DataFrame
                The transformed DataFrame.
        '''
        raise NotImplementedError("Plugins must implement a transform method.")
