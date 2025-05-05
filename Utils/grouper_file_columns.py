'''
    This module provides functions for reading and processing data files
'''
from os import path
from typing import Optional
import pathlib as p
import Utils.constants as const


def parse_definition_file(rdf_file: p.Path) -> list[tuple]:
    '''
    Reads the definition file and extracts:
      - The delimiter based on the first line
      - The column specifications on subsequent lines

    Notes:
    The files are .rdf but this is NOT the same as that described
    here: http://www.w3.org/1999/02/22-rdf-syntax-ns#

    Information about the file can be found here in the user manual:
    HRG4++202425+Local+Payment+Grouper+User+Manual+v1.0.pdf

    Returns a tuple of (delimiter, column_mappings) where:
      - delimiter is a character
      - column_mappings is a list of [display_name, internal_name, position]
    '''
    #The examples all use comma delimited but we'll thrown in a couple more.
    delimiter_map = {
        "COMMA DELIMITED": ",",
        "TAB DELIMITED": "\t",
        "PIPE DELIMITED": "|"
    }

    with open(rdf_file, encoding='utf-8') as file:
        # First line defines the delimiter
        delim = file.readline().strip().upper()
        if delim not in delimiter_map:
            raise ValueError(f"Unsupported delimiter: {delim}")

        delimiter = delimiter_map[delim]

        # Column definitions
        column_definitions = []
        for line in file:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            fields = line.split(delimiter)

            display_name = fields[0].strip()
            internal_name = fields[1].strip()
            position = int(fields[2].strip())
            column_definitions.append((display_name, internal_name, position))

    # Sort the column mappings by position
    column_definitions.sort(key=lambda fields: fields[2])

    return delimiter, column_definitions


def append_grouper_columns(column_definitions: list, additional_columns: list) -> list:
    '''
        Type is the file postfix added by the grouper to the file name.
        We add a few columns to the end of the column definitions to
        match the processed files.

        options for type are sort, fce, spell, quality, and flag
    '''
    last_position = column_definitions[-1][2]

    for column in additional_columns:
        last_position += 1
        column_definitions.append((column, column, last_position))


def sort_file_additional_cols(columns: list[tuple]) -> list[tuple]:
    '''
        Adds the column for the sort file.
    '''
    additional_columns = ['RowNo']
    append_grouper_columns(columns, additional_columns)
    return columns


def fce_file_additional_cols(columns: list[tuple]) -> list[tuple]:
    '''
        Adds the columns for the FCE file.
    '''
    additional_columns = ['RowNo', 'FCE_HRG', 'GroupingMethodFlag',
                          'DominantProcedure', 'FCE_PBC', 'CalcEpidur',
                          'ReportingEPIDUR', 'FCETrimpoint', 'FCEExcessBeddays',
                          'SpellReportFlag', 'FCESSC_Ct', 'FCESSCs1', 'FCESSCs2',
                          'FCESSCs3', 'FCESSCs4', 'FCESSCs5', 'FCESSCs6',
                          'FCESSCs7', 'SpellHRG', 'SpellGroupingMethodFlag',
                          'SpellDominantProcedure', 'SpellPDiag', 'SpellSDiag',
                          'SpellEpisodeCount', 'SpellLOS', 'ReportingSpellLOS',
                          'SpellTrimpoint', 'SpellExcessBeddays', 'SpellCCDays',
                          'SpellPBC', 'UnbundledHRGs',
                         ]
    append_grouper_columns(columns, additional_columns)
    return columns


def fce_rel_file_additional_cols() -> list[tuple]:
    '''
        The columns for the FCE file.
        Note the rel files don't inlcude the input file columns.
    '''
    columns = [('RowNo', 'RowNo', 1),
               ('FCE_HRG', 'FCE_HRG', 2),
               ('GroupingMethodFlag', 'GroupingMethodFlag', 3),
               ('DominantProcedure', 'DominantProcedure', 4),
               ('FCE_PBC', 'FCE_PBC', 5),
               ('CalcEpidur', 'CalcEpidur', 6),
               ('ReportingEPIDUR', 'ReportingEPIDUR', 7),
               ('FCETrimpoint', 'FCETrimpoint', 8),
               ('FCEExcessBeddays', 'FCEExcessBeddays', 9),
               ('SpellReportFlag', 'SpellReportFlag', 10),
              ]

    return columns

def spell_file_additional_cols() -> list[tuple]:
    '''
        The columns for the spell file.
    '''
    columns = [('RowNo', 'RowNo', 1),
               ('PROCODET', 'PROCODET', 2),
               ('PROVSPNO', 'PROVSPNO', 3),
               ('SpellHRG', 'SpellHRG', 4),
               ('SpellGroupingMethodFlag', 'SpellGroupingMethodFlag', 5),
               ('SpellDominantProcedure', 'SpellDominantProcedure', 6),
               ('SpellPDiag', 'SpellPDiag', 7),
               ('SpellSDiag', 'SpellSDiag', 8),
               ('SpellEpisodeCount', 'SpellEpisodeCount', 9),
               ('SpellLOS', 'SpellLOS', 10),
               ('ReportingSpellLOS', 'ReportingSpellLOS', 11),
               ('SpellTrimpoint', 'SpellTrimpoint', 12),
               ('SpellExcessBeddays', 'SpellExcessBeddays', 13),
               ('SpellCCDays', 'SpellCCDays', 14),
               ('SpellPBC', 'SpellPBC', 15),
               ('SpellSSC_Ct', 'SpellSSC_Ct', 16),
               ('SpellSSCs1', 'SpellSSCs1', 17),
               ('SpellSSCs2', 'SpellSSCs2', 18),
               ('SpellSSCs3', 'SpellSSCs3', 19),
               ('SpellSSCs4', 'SpellSSCs4', 20),
               ('SpellSSCs5', 'SpellSSCs5', 21),
               ('SpellSSCs6', 'SpellSSCs6', 22),
               ('SpellSSCs7', 'SpellSSCs7', 23),
               ('SpellBP_Ct', 'SpellBP_Ct', 24),
               ('SpellBP1', 'SpellBP1', 25),
               ('SpellBP2', 'SpellBP2', 26),
               ('SpellBP3', 'SpellBP3', 27),
               ('SpellBP4', 'SpellBP4', 28),
               ('SpellBP5', 'SpellBP5', 29),
               ('SpellBP6', 'SpellBP6', 30),
               ('SpellBP7', 'SpellBP7', 31),
               ('SpellFlag_Ct', 'SpellFlag_Ct', 32),
               ('SpellFlag1', 'SpellFlag1', 33),
               ('SpellFlag2', 'SpellFlag2', 34),
               ('SpellFlag3', 'SpellFlag3', 35),
               ('SpellFlag4', 'SpellFlag4', 36),
               ('SpellFlag5', 'SpellFlag5', 37),
               ('SpellFlag6', 'SpellFlag6', 38),
               ('SpellFlag7', 'SpellFlag7', 39),
               ('UnbundledHRGs', 'UnbundledHRGs', 40),
              ]
    return columns

def spell_rel_file_additional_cols() -> list[tuple]:
    '''
        Adds the columns for the FCE file.
    '''
    columns = [('RowNo', 'RowNo', 1),
               ('PROCODET', 'PROCODET', 2),
               ('PROVSPNO', 'PROVSPNO', 3),
               ('SpellHRG', 'SpellHRG', 4),
               ('SpellGroupingMethodFlag', 'SpellGroupingMethodFlag', 5),
               ('SpellDominantProcedure', 'SpellDominantProcedure', 6),
               ('SpellPDiag', 'SpellPDiag', 7),
               ('SpellSDiag', 'SpellSDiag', 8),
               ('SpellEpisodeCount', 'SpellEpisodeCount', 9),
               ('SpellLOS', 'SpellLOS', 10),
               ('ReportingSpellLOS', 'ReportingSpellLOS', 11),
               ('SpellTrimpoint', 'SpellTrimpoint', 12),
               ('SpellExcessBeddays', 'SpellExcessBeddays', 13),
               ('SpellCCDays', 'SpellCCDays', 14),
               ('SpellPBC', 'SpellPBC', 15),
              ]
    return columns

def quality_file_additional_cols(columns: list[tuple]) -> list[tuple]:
    '''
        Adds the columns for the quality file.
        Note error message is variable length.
    '''
    additional_columns = ['RowNo', 'Error Message1',
                          'Error Message2', 'Error Message4',
                          'Error Message5', 'Error Message6',
                          'Error Message7', 'Error Message8',
                          'Error Message9', 'Error Message10',
                         ]
    append_grouper_columns(columns, additional_columns)
    return columns

def quality_rel_file_additional_cols() -> list[tuple]:
    '''
        The columns for the quality file.
        Note iteration is really a line number and it's one error per line
    '''
    columns = [('RowNo', 'RowNo', 1),
               ('Iteration', 'Iteration', 2),
               ('Code Type', 'Code Type', 3),
               ('Code', 'Code', 4),
               ('Error Message', 'Error Message', 5),
              ]

    return columns

def flag_rel_file_additional_cols() -> list[tuple]:
    '''
        The columns for the flag file.
        Note iteration is really a line number and it's one flag per line.
    '''
    columns = [('RowNo', 'RowNo', 1),
               ('PROCODET', 'PROCODET', 2),
               ('PROVSPNO', 'PROVSPNO', 3),
               ('Iteration', 'Iteration', 4),
               ('SpellFlag', 'SpellFlag', 5),
              ]

    return columns

def ub_rel_file_additional_cols() -> list[tuple]:
    '''
        Note iteration is really a line number and it's one uHRG per line.
        e.g.
            RowNo	Iteration	UnbundledHRGs
            1	    1	        VC14Z
            1	    2	        RD26Z
    '''
    columns = [('RowNo', 'RowNo', 1),
               ('Iteration', 'Iteration', 2),
               ('UnbundledHRGs', 'UnbundledHRGs', 3),
              ]

    return columns


def summary_file_additional_cols() -> list[tuple]:
    '''
        The columns for the summary file.
    '''
    columns = [('Grouper Version', 'Grouper Version', 1),
               ('Database Version', 'Database Version', 2),
               ('FCE Count', 'FCE Count', 3),
               ('Spell Count', 'Spell Count', 4),
               ('FCE Error Count', 'FCE Error Count', 5),
               ('Spell Error Count', 'Spell Error Count', 6),
               ('Run Start Date/Time', 'Run Start Date/Time', 7),
               ('Run End Date/Time', 'Run End Date/Time', 8),
               ('Input Filename', 'Input Filename', 9),
               ('Output Filename', 'Output Filename', 10),
               ('RDF path and name', 'RDF path and name', 11),
              ]
    return columns

class GrouperFileDefinitions:
    '''
        A class to hold the file definitions for the various files consumed
        or produced by the NHS grouper software.
    '''
    def __init__(self, rdf_file: Optional[p.Path]):

        if not rdf_file.exists():
            rdf_file = path.join(const.DATA_FILE_FOLDER, const.DEFAULT_RDF_FILE)
        if not rdf_file.exists():
            raise FileNotFoundError(f"File not found: {rdf_file}")

        self.delimiter, self.input_file_columns = parse_definition_file(rdf_file)
        self.sort_file = sort_file_additional_cols(self.input_file_columns)
        self.fce_file = fce_file_additional_cols(self.input_file_columns)
        self.fce_rel_file = fce_rel_file_additional_cols()
        self.spell_file = spell_file_additional_cols()
        self.spell_rel_file = spell_rel_file_additional_cols()
        self.quality_file = quality_file_additional_cols(self.input_file_columns)
        self.quality_rel_file = quality_rel_file_additional_cols()
        self.flag_rel_file = flag_rel_file_additional_cols()
        self.ub_rel_file = ub_rel_file_additional_cols()
        self.summary_file = summary_file_additional_cols()


    def error_parser(self, error_field: str) -> dict:
        '''
            The error field is a string with 3 pieces
            Each piece is separated by a pipe.
        '''
        error_source, code, error_message = error_field.split('|')
        return {'Source_Column': error_source, 'Code': code, 'Description': error_message}
