'''
    This module defines the Probe abstract base class.
'''
from abc import ABC, abstractmethod

class Probe(ABC):
    '''
        This class defines the Probe abstract base class.
    '''
    @classmethod
    @abstractmethod
    def column_name(cls) -> str:
        """Returns the name of the column to probe."""


    @classmethod
    @abstractmethod
    def probe_values(cls) -> list:
        """Returns the list of values to probe."""
