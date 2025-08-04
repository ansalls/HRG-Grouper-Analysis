'''
    End-to-End Pipeline for HRG Priority Score Analysis

    This module provides a comprehensive pipeline that processes raw data
    through the complete workflow:
    1. Raw data preprocessing with transformation plugins
    2. Running the grouper to generate initial HRG assignments
    3. Calculating CC scores and gap estimates
    4. Generating and verifying CC gaps
    5. Computing priority scores for potential revenue optimization
    6. Exporting results for review/follow up
'''
import os
from typing import Optional, Dict, List
from datetime import datetime
import logging
import pandas as pd
from Utils.constants import (
    DATA_FILE_FOLDER, PROCESSED_FILE_FOLDER,
    HRG_OUTPUT_FILE_FOLDER, HRG_COLUMN_NAME,
    DEFAULT_RDF_FILE, PERSON_TO_SPELLS_FILE,
    DIAGNOSIS_PREFIX, PROCEDURE_PREFIX,
    MAX_OPER_COLS, MAX_DIAG_COLS
)
from Utils.preprocess_raw_data_file import process_zl_data_file
from Utils.run_grouper import run_grouper
from Utils.grouper_data_import import (
    read_data, get_grouper_output_file_by_type
)
from Utils.grouper_file_columns import parse_definition_file, fce_file_additional_cols
from Utils.grouper_df_utils import apply_plugins, write_output
from Utils.priority_score import (
    calculate_priority_scores, generate_hrg_upgrade_verification_file,
    verify_cc_gaps
)
from Utils.diagnosis_history import get_person_to_spells_map

from Probe_classes.grouper_file_type import GrouperFileType

from Plugins.procodet_null_filler import ProcodetNullFillerPlugin
from Plugins.period_strip import PeriodStripPlugin
from Plugins.column_extender import ColumnExtenderPlugin
from Plugins.combination_row import CombinationRowPlugin
from Plugins.only_single_episode_spells import OnlySingleEpisodeSpellsPlugin
from Plugins.append_x import AppendXPlugin
from Plugins.only_inpatient_baseclass import OnlyInpatientPlugin
from Plugins.nc_strip import NcStripPlugin

from tariff_kv_store import add_tariff_columns


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PipelineConfig:
    '''
        Configuration class for pipeline parameters
    '''

    def __init__(
        self,
        raw_data_file: str,
        definitions_file: Optional[str] = None,
        output_prefix: Optional[str] = None,
        verify_gaps: bool = True,
        max_diag_cols: int = MAX_DIAG_COLS,
        max_oper_cols: int = MAX_OPER_COLS
    ):
        timestamp = datetime.now().isoformat()

        self.raw_data_file = raw_data_file
        self.definitions_file = definitions_file or os.path.join(DATA_FILE_FOLDER, DEFAULT_RDF_FILE)
        self.output_prefix = output_prefix or f"pipeline_output_{timestamp}"
        self.verify_gaps = verify_gaps
        self.max_diag_cols = max_diag_cols
        self.max_oper_cols = max_oper_cols

        # Generated file paths
        self.processed_file = os.path.join(
            PROCESSED_FILE_FOLDER, f"{self.output_prefix}_processed.csv")
        self.grouper_output_base = os.path.join(
            HRG_OUTPUT_FILE_FOLDER, f"{self.output_prefix}_grouped")
        self.priority_scores_file = os.path.join(
            PROCESSED_FILE_FOLDER, f"{self.output_prefix}_priority_scores.csv")
        self.verification_file = os.path.join(
            PROCESSED_FILE_FOLDER, f"{self.output_prefix}_verification.csv")
        self.final_results_file = os.path.join(
            PROCESSED_FILE_FOLDER, f"{self.output_prefix}_final_results.csv")


class EndToEndPipeline:
    '''
        Main pipeline class that orchestrates the complete HRG priority score analysis workflow.

        This class provides a high-level interface for running the entire analysis pipeline,
        from raw data processing to final priority score calculation and output generation.
    '''

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.processed_df = None
        self.grouper_output_df = None
        self.person_to_spells_df = None
        self.priority_scores_df = None
        self.verification_df = None
        self.final_results_df = None

        logger.info("Initialized pipeline with config: %s", config.output_prefix)

    def run_complete_pipeline(self) -> Dict[str, str]:
        '''
            Execute the complete end-to-end pipeline.

            Returns:
                Dict containing paths to all generated output files
        '''
        logger.info("Starting complete end-to-end pipeline execution")

        try:
            # Step 1: Preprocess raw data
            self.preprocess_raw_data()

            # Step 2: Run grouper
            self.run_grouper_analysis()

            # Step 3: Load and prepare grouper output
            self.load_grouper_output()

            # Step 4: Create or load person-to-spells mapping
            self.prepare_person_mapping()

            # Step 5: Calculate initial priority scores
            self.calculate_priority_scores()

            # Step 6: Generate verification scenarios (if requested)
            if self.config.verify_gaps:
                self.generate_verification_scenarios()
                self.verify_gap_scenarios()

            # Step 7: Generate final results
            self.generate_final_results()

            # Step 8: Export all outputs
            export_files = self.export_results()

            logger.info("Pipeline execution completed successfully")
            return export_files

        except Exception as e:
            logger.error("Pipeline execution failed: %s", str(e))
            raise

    def preprocess_raw_data(self) -> str:
        '''
            Apply data transformation plugins to raw data.

            Returns:
                Path to processed data file
        '''
        logger.info("Step 1: Preprocessing raw data")

        if not os.path.exists(self.config.raw_data_file):
            raise FileNotFoundError(f"Raw data file not found: {self.config.raw_data_file}")

        # Check if this is a ZL data file (based on file extension)
        if self.config.raw_data_file.endswith('.txt'):
            processed_file = process_zl_data_file(
                self.config.raw_data_file,
                self.config.definitions_file
            )
        else:
            processed_file = self.process_csv_data()

        logger.info("Raw data processed and saved to: %s", processed_file)
        self.config.processed_file = processed_file
        return processed_file

    def process_csv_data(self) -> str:
        '''
            Process CSV data with plugins
        '''
        # Parse definition file
        delimiter, column_mappings = parse_definition_file(self.config.definitions_file)

        # Load data
        df = read_data(self.config.raw_data_file, column_mappings, delimiter)

        # Apply transformation plugins
        plugins = self.get_transformation_plugins()
        df_transformed = apply_plugins(df, plugins)

        # Write output
        write_output(df_transformed, self.config.processed_file, delimiter)

        return self.config.processed_file

    def get_transformation_plugins(self) -> List:
        '''
            Get list of transformation plugins to apply
        '''
        return [
            OnlyInpatientPlugin(),
            ProcodetNullFillerPlugin(),
            PeriodStripPlugin(),
            NcStripPlugin(),
            AppendXPlugin(),
            ColumnExtenderPlugin(prefix=DIAGNOSIS_PREFIX, maximum=self.config.max_diag_cols),
            ColumnExtenderPlugin(prefix=PROCEDURE_PREFIX, maximum=self.config.max_oper_cols),
            CombinationRowPlugin(replace_rows=True),
            OnlySingleEpisodeSpellsPlugin(),
        ]

    def run_grouper_analysis(self) -> str:
        '''
            Run the NHS grouper on processed data.

            Returns:
                Path to grouper output base file
        '''
        logger.info("Step 2: Running the grouper")

        grouper_output = run_grouper(
            input_file=self.config.processed_file,
            definitions_file=self.config.definitions_file,
            output_file=self.config.grouper_output_base
        )

        logger.info("Grouper completed: %s", grouper_output)
        self.config.grouper_output_base = grouper_output
        return grouper_output

    def load_grouper_output(self) -> pd.DataFrame:
        '''
            Load and prepare grouper output data.

            Returns:
                DataFrame containing grouper output with FCE data
        '''
        logger.info("Step 3: Loading grouper output")

        # Get FCE output file
        fce_output_file = get_grouper_output_file_by_type(
            self.config.grouper_output_base,
            GrouperFileType.FCE
        )

        if not os.path.exists(fce_output_file):
            raise FileNotFoundError(f"Grouper FCE output not found: {fce_output_file}")

        delimiter, column_mappings = parse_definition_file(self.config.definitions_file)
        column_mappings = fce_file_additional_cols(column_mappings)

        self.grouper_output_df = read_data(fce_output_file, column_mappings, delimiter)

        self.grouper_output_df = add_tariff_columns(self.grouper_output_df)

        logger.info("Loaded %d records from grouper output", len(self.grouper_output_df))
        return self.grouper_output_df

    def prepare_person_mapping(self) -> pd.DataFrame:
        '''
            Load person-to-spells mapping.

            Returns:
                DataFrame containing person to spells mapping
        '''
        logger.info("Step 4: Preparing person-to-spells mapping")

        person_mapping_file = os.path.join(DATA_FILE_FOLDER, PERSON_TO_SPELLS_FILE)

        if os.path.exists(person_mapping_file):
            logger.info("Loading existing person-to-spells mapping")
            self.person_to_spells_df = get_person_to_spells_map()
        else:
            raise FileNotFoundError(
                f"Person-to-spells mapping file not found: {person_mapping_file}"
            )

        logger.info("Person mapping prepared with %d records", len(self.person_to_spells_df))
        return self.person_to_spells_df

    def calculate_priority_scores(self) -> pd.DataFrame:
        '''
            Calculate priority scores for all spells.

            Returns:
                DataFrame with priority scores added
        '''
        logger.info("Step 5: Calculating priority scores")

        if self.grouper_output_df is None:
            raise ValueError("Grouper output must be loaded before calculating priority scores")

        self.priority_scores_df = calculate_priority_scores(
            self.grouper_output_df,
            self.person_to_spells_df,
            verify_gaps=False  # Initial calculation without verification
        )

        logger.info("Calculated priority scores for %d records", len(self.priority_scores_df))
        return self.priority_scores_df

    def generate_verification_scenarios(self) -> pd.DataFrame:
        '''
            Generate test scenarios for CC gap verification.

            Returns:
                DataFrame containing verification test data
        '''
        logger.info("Step 6: Generating verification scenarios")

        if self.grouper_output_df is None:
            raise ValueError(
                "Grouper output must be loaded before generating verification scenarios")

        self.verification_df = generate_hrg_upgrade_verification_file(self.grouper_output_df)

        logger.info("Generated %d verification scenarios", len(self.verification_df))
        return self.verification_df

    def verify_gap_scenarios(self) -> pd.DataFrame:
        '''
            Run grouper verification on test scenarios.

            Returns:
                DataFrame with verified gap results
        '''
        logger.info("Step 7: Verifying CC gap scenarios")

        if self.verification_df is None:
            raise ValueError("Verification scenarios must be generated first")

        if self.grouper_output_df is None:
            raise ValueError("Grouper output must be loaded before verifying gaps")

        verified_results = verify_cc_gaps(
            self.verification_df,
            output_file=self.config.verification_file
        )

        # Recalculate priority scores with verified gaps
        self.priority_scores_df = calculate_priority_scores(
            self.grouper_output_df,
            self.person_to_spells_df,
            verify_gaps=True
        )

        logger.info("CC gap verification completed and priority scores updated")
        return verified_results

    def generate_final_results(self) -> pd.DataFrame:
        '''
            Combine all analysis results into final output.

            Returns:
                DataFrame containing complete analysis results
        '''
        logger.info("Step 8: Generating final results")

        if self.grouper_output_df is None:
            raise ValueError("Grouper output must be loaded before generating final results")

        self.final_results_df = self.grouper_output_df.copy()

        # Merge priority scores
        if self.priority_scores_df is not None:
            self.final_results_df = self.final_results_df.merge(
                self.priority_scores_df[['PROVSPNO', 'PriorityScore']],
                on='PROVSPNO',
                how='left'
            )

        self.add_summary_statistics()

        logger.info("Final results prepared with %d records", len(self.final_results_df))
        return self.final_results_df

    def add_summary_statistics(self):
        '''
            Add summary statistics to final results
        '''
        if (self.final_results_df is not None and
                'PriorityScore' in self.final_results_df.columns):
            # Add priority score rankings
            self.final_results_df['PriorityRank'] = self.final_results_df['PriorityScore'].rank(
                method='dense', ascending=False
            )

            # Add priority categories
            self.final_results_df['PriorityCategory'] = pd.cut(
                self.final_results_df['PriorityScore'],
                bins=[0, 50, 100, 200, float('inf')],
                labels=['Low', 'Medium', 'High', 'Very High'],
                include_lowest=True
            )

    def export_results(self) -> Dict[str, str]:
        '''
            Export all pipeline results to files.

            Returns:
                Dictionary mapping result type to file path
        '''
        logger.info("Step 9: Exporting results")

        export_files = {}

        # Export final results
        if self.final_results_df is not None:
            self.final_results_df.to_csv(self.config.final_results_file, index=False)
            export_files['final_results'] = self.config.final_results_file
            logger.info("Final results exported to: %s", self.config.final_results_file)

        # Export priority scores separately
        if self.priority_scores_df is not None:
            self.priority_scores_df.to_csv(self.config.priority_scores_file, index=False)
            export_files['priority_scores'] = self.config.priority_scores_file
            logger.info("Priority scores exported to: %s", self.config.priority_scores_file)

        # Export verification results (if generated)
        if self.verification_df is not None:
            verification_export_file = self.config.verification_file.replace(
                '.csv', '_exported.csv')
            self.verification_df.to_csv(verification_export_file, index=False)
            export_files['verification'] = verification_export_file
            logger.info("Verification results exported to: %s", verification_export_file)

        # Export person mapping
        if self.person_to_spells_df is not None:
            person_mapping_export = os.path.join(
                PROCESSED_FILE_FOLDER,
                f"{self.config.output_prefix}_person_mapping.csv"
            )
            self.person_to_spells_df.to_csv(person_mapping_export, index=False)
            export_files['person_mapping'] = person_mapping_export

        return export_files

    def get_pipeline_summary(self) -> Dict:
        '''
            Generate summary statistics for the pipeline run.

            Returns:
                Dictionary containing pipeline execution summary
        '''
        sumary = {
            'pipeline_config': {
                'raw_data_file': self.config.raw_data_file,
                'output_prefix': self.config.output_prefix,
                'verify_gaps': self.config.verify_gaps,
            },
            'data_summary': {},
            'execution_timestamp': datetime.now().isoformat()
        }

        if self.final_results_df is not None:
            sumary['data_summary'] = {
                'total_spells': len(self.final_results_df),
                'unique_hrg_codes': self.final_results_df[HRG_COLUMN_NAME].nunique(),
                'avg_priority_score': self.final_results_df.get(
                    'PriorityScore', pd.Series()).mean(),
                'high_priority_spells': len(self.final_results_df[
                    self.final_results_df.get('PriorityScore', 0) > 100
                ])
            }

        return sumary


def run_basic_pipeline(
    raw_data_file: str,
    definitions_file: Optional[str] = None,
    output_prefix: Optional[str] = None
) -> Dict[str, str]:
    '''
        Run a basic pipeline without gap verification.

        Args:
            raw_data_file: Path to raw data file
            definitions_file: Path to RDF definitions file
            output_prefix: Prefix for output files

        Returns:
            Dictionary of output file paths
    '''
    config = PipelineConfig(
        raw_data_file=raw_data_file,
        definitions_file=definitions_file,
        output_prefix=output_prefix,
        verify_gaps=False
    )

    pipeline = EndToEndPipeline(config)
    return pipeline.run_complete_pipeline()


def run_full_pipeline_with_verification(
    raw_data_file: str,
    definitions_file: Optional[str] = None,
    output_prefix: Optional[str] = None
) -> Dict[str, str]:
    '''
        Run complete pipeline including gap verification.

        Args:
            raw_data_file: Path to raw data file
            definitions_file: Path to RDF definitions file
            output_prefix: Prefix for output files

        Returns:
            Dictionary of output file paths
    '''
    config = PipelineConfig(
        raw_data_file=raw_data_file,
        definitions_file=definitions_file,
        output_prefix=output_prefix,
        verify_gaps=True
    )

    pipeline = EndToEndPipeline(config)
    return pipeline.run_complete_pipeline()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run HRG Priority Score Analysis Pipeline")
    parser.add_argument("raw_data_file", help="Path to raw data file")
    parser.add_argument("--definitions", help="Path to RDF definitions file")
    parser.add_argument("--output-prefix", help="Prefix for output files")
    parser.add_argument("--verify-gaps", action="store_true", help="Run gap verification")

    args = parser.parse_args()

    if not args.raw_data_file:
        default_config = PipelineConfig(
            raw_data_file=args.raw_data_file,
            definitions_file=args.definitions,
            output_prefix=args.output_prefix,
            verify_gaps=args.verify_gaps
        )

        default_pipeline = EndToEndPipeline(default_config)
        output_files = default_pipeline.run_complete_pipeline()

        print("Pipeline completed successfully!")
        print("Output files:")
        for key, path in output_files.items():
            print(f"  {key}: {path}")

        summary = default_pipeline.get_pipeline_summary()
        print("\nPipeline Summary:")
        print(f" Total spells processed: {summary['data_summary'].get('total_spells', 'N/A')}")
        print(f" Unique HRG codes: {summary['data_summary'].get('unique_hrg_codes', 'N/A')}")
        print(
            f" Avg. priority score: {summary['data_summary'].get('avg_priority_score', 'N/A'):.2f}")
