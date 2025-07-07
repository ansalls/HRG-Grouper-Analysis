'''
    This module defines the Probe abstract base class.
'''
from typing import Protocol, Iterable, runtime_checkable
from enum import Enum


@runtime_checkable
class Probe(Protocol):
    '''
        This class defines the Probe protocol.
    '''
    # pylint: disable=unnecessary-ellipsis
    # https://github.com/pylint-dev/pylint/issues/9319
    @classmethod
    def column_name(cls) -> str:
        '''
            Returns the name of the column to probe.
        '''
        ...

    @classmethod
    def probe_values(cls) -> Iterable:
        '''
            Returns the list of values to probe.
        '''
        ...

    @classmethod
    def probe_value_names(cls) -> Iterable:
        '''
            Returns the list of value names to probe.
        '''
        ...


class EnumProbeMixin(Enum):
    '''
        A mixin class to provide enumeration probing functionality.
    '''
    @classmethod
    def probe_values(cls) -> list:
        '''
            Returns a list of values for all members of the enumeration.
        '''
        return [m.value for m in cls]

    @classmethod
    def probe_value_names(cls) -> list:
        '''
            Returns a string representation of the enum class.
        '''
        return [m.name for m in cls]
