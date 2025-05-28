#!/usr/bin/env python3
"""
Format Compliance Utility

This module ensures that the output data format exactly matches the source CSV format,
including proper data types and column structure.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Target data types based on the source CSV format
TARGET_DATA_TYPES = {
    'Season': 'int64',
    'Week': 'int64', 
    'Player': 'object',
    'Position': 'object',
    'Team': 'object',
    'Opponent': 'object',
    'Pass_Comp': 'int64',
    'Pass_Att': 'int64',
    'Pass_Yards': 'int64',
    'Pass_TD': 'int64',
    'Pass_Int': 'int64',
    'Rush_Att': 'int64',
    'Rush_Yards': 'int64',
    'Rush_TD': 'int64',
    'Rec_Targets': 'int64',
    'Rec_Recep': 'int64',
    'Rec_Yards': 'int64',
    'Rec_TD': 'int64',
    'Snapcount': 'int64',
    'PPR_Points': 'float64',
    'PPR_Average': 'float64',
    'Reg_League_Avg': 'float64',
    'Reg_Due_For': 'float64'
}

# Column order to match source CSV
TARGET_COLUMN_ORDER = [
    'Season', 'Week', 'Player', 'Position', 'Team', 'Opponent',
    'Pass_Comp', 'Pass_Att', 'Pass_Yards', 'Pass_TD', 'Pass_Int',
    'Rush_Att', 'Rush_Yards', 'Rush_TD',
    'Rec_Targets', 'Rec_Recep', 'Rec_Yards', 'Rec_TD',
    'Snapcount', 'PPR_Points', 'PPR_Average', 'Reg_League_Avg', 'Reg_Due_For'
]

class FormatComplianceManager:
    """Manages format compliance with the source CSV structure."""
    
    def __init__(self, source_csv_path: Optional[str] = None):
        """
        Initialize the format compliance manager.
        
        Args:
            source_csv_path (str, optional): Path to source CSV for reference
        """
        self.logger = logger
        self.target_types = TARGET_DATA_TYPES.copy()
        self.target_columns = TARGET_COLUMN_ORDER.copy()
        
        # Load source CSV if provided for dynamic type detection
        if source_csv_path and Path(source_csv_path).exists():
            self._load_source_format(source_csv_path)
    
    def _load_source_format(self, source_csv_path: str):
        """Load format information from source CSV."""
        try:
            source_df = pd.read_csv(source_csv_path, nrows=5)  # Just read a few rows for types
            
            # Update target types based on source
            for col in source_df.columns:
                if col in self.target_types:
                    self.target_types[col] = str(source_df[col].dtype)
            
            # Update column order based on source
            self.target_columns = [col for col in source_df.columns if col in TARGET_COLUMN_ORDER]
            
            self.logger.info(f"Loaded format from source CSV: {len(self.target_columns)} columns")
            
        except Exception as e:
            self.logger.warning(f"Could not load source format: {e}, using defaults")
    
    def convert_to_target_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert DataFrame to target data types.
        
        Args:
            df (pd.DataFrame): DataFrame to convert
            
        Returns:
            pd.DataFrame: DataFrame with correct data types
        """
        if df.empty:
            return df
        
        df = df.copy()
        conversion_errors = []
        
        for column, target_type in self.target_types.items():
            if column not in df.columns:
                continue
            
            try:
                if target_type == 'int64':
                    # Convert to numeric, handling NaN values
                    df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0).astype('int64')
                    
                elif target_type == 'float64':
                    # Convert to numeric, handling NaN values
                    df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0.0).astype('float64')
                    
                elif target_type == 'object':
                    # Convert to string, handling NaN values
                    df[column] = df[column].astype(str).replace('nan', '')
                    
                else:
                    # Try direct conversion
                    df[column] = df[column].astype(target_type)
                    
            except Exception as e:
                conversion_errors.append(f"{column}: {str(e)}")
                self.logger.warning(f"Could not convert {column} to {target_type}: {e}")
        
        if conversion_errors:
            self.logger.warning(f"Type conversion errors: {conversion_errors}")
        
        return df
    
    def ensure_column_order(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure DataFrame columns are in the correct order.
        
        Args:
            df (pd.DataFrame): DataFrame to reorder
            
        Returns:
            pd.DataFrame: DataFrame with correct column order
        """
        if df.empty:
            return df
        
        # Get columns that exist in both the DataFrame and target order
        available_columns = [col for col in self.target_columns if col in df.columns]
        
        # Add any extra columns at the end
        extra_columns = [col for col in df.columns if col not in self.target_columns]
        
        final_columns = available_columns + extra_columns
        
        return df[final_columns]
    
    def add_missing_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add any missing columns with appropriate default values.
        
        Args:
            df (pd.DataFrame): DataFrame to check
            
        Returns:
            pd.DataFrame: DataFrame with all required columns
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        for column in self.target_columns:
            if column not in df.columns:
                # Add missing column with appropriate default value
                if self.target_types.get(column) == 'int64':
                    df[column] = 0
                elif self.target_types.get(column) == 'float64':
                    df[column] = 0.0
                else:
                    df[column] = ''
                
                self.logger.info(f"Added missing column: {column}")
        
        return df
    
    def validate_format_compliance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate format compliance and return detailed report.
        
        Args:
            df (pd.DataFrame): DataFrame to validate
            
        Returns:
            Dict[str, Any]: Validation report
        """
        report = {
            'compliant': True,
            'issues': [],
            'column_count': len(df.columns),
            'target_column_count': len(self.target_columns),
            'missing_columns': [],
            'extra_columns': [],
            'type_mismatches': [],
            'column_order_correct': True
        }
        
        if df.empty:
            report['issues'].append('DataFrame is empty')
            report['compliant'] = False
            return report
        
        # Check for missing columns
        missing_columns = [col for col in self.target_columns if col not in df.columns]
        if missing_columns:
            report['missing_columns'] = missing_columns
            report['issues'].append(f"Missing columns: {missing_columns}")
            report['compliant'] = False
        
        # Check for extra columns
        extra_columns = [col for col in df.columns if col not in self.target_columns]
        if extra_columns:
            report['extra_columns'] = extra_columns
            report['issues'].append(f"Extra columns: {extra_columns}")
        
        # Check data types
        type_mismatches = []
        for column in df.columns:
            if column in self.target_types:
                actual_type = str(df[column].dtype)
                target_type = self.target_types[column]
                if actual_type != target_type:
                    type_mismatches.append({
                        'column': column,
                        'actual_type': actual_type,
                        'target_type': target_type
                    })
        
        if type_mismatches:
            report['type_mismatches'] = type_mismatches
            report['issues'].append(f"Type mismatches in {len(type_mismatches)} columns")
            report['compliant'] = False
        
        # Check column order
        available_target_columns = [col for col in self.target_columns if col in df.columns]
        actual_order = [col for col in df.columns if col in available_target_columns]
        if actual_order != available_target_columns:
            report['column_order_correct'] = False
            report['issues'].append("Column order does not match target")
        
        return report
    
    def make_compliant(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Make DataFrame fully compliant with target format.
        
        Args:
            df (pd.DataFrame): DataFrame to make compliant
            
        Returns:
            pd.DataFrame: Compliant DataFrame
        """
        if df.empty:
            return df
        
        self.logger.info("Making DataFrame format compliant...")
        
        # Step 1: Add missing columns
        df = self.add_missing_columns(df)
        
        # Step 2: Convert to target data types
        df = self.convert_to_target_types(df)
        
        # Step 3: Ensure correct column order
        df = self.ensure_column_order(df)
        
        # Step 4: Validate compliance
        validation_report = self.validate_format_compliance(df)
        
        if validation_report['compliant']:
            self.logger.info("DataFrame is now format compliant")
        else:
            self.logger.warning(f"DataFrame still has compliance issues: {validation_report['issues']}")
        
        return df


def make_dataframe_compliant(df: pd.DataFrame, source_csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Convenience function to make a DataFrame format compliant.
    
    Args:
        df (pd.DataFrame): DataFrame to make compliant
        source_csv_path (str, optional): Path to source CSV for reference
        
    Returns:
        pd.DataFrame: Compliant DataFrame
    """
    manager = FormatComplianceManager(source_csv_path)
    return manager.make_compliant(df)


def validate_dataframe_compliance(df: pd.DataFrame, source_csv_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to validate DataFrame compliance.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        source_csv_path (str, optional): Path to source CSV for reference
        
    Returns:
        Dict[str, Any]: Validation report
    """
    manager = FormatComplianceManager(source_csv_path)
    return manager.validate_format_compliance(df)


if __name__ == "__main__":
    # Example usage
    import json
    
    # Create test DataFrame
    test_data = {
        'Season': ['2024', '2024'],
        'Week': ['1', '2'],
        'Player': ['Test Player 1', 'Test Player 2'],
        'Position': ['QB', 'RB'],
        'Team': ['ARI', 'PHI'],
        'Opponent': ['BUF', 'LAR'],
        'Pass_Yards': ['250', '0'],
        'Rush_Yards': ['10', '85'],
        'Snapcount': ['65', '45'],
        'PPR_Points': ['18.5', '12.3']
    }
    
    test_df = pd.DataFrame(test_data)
    print("Original DataFrame:")
    print(test_df.dtypes)
    print()
    
    # Make compliant
    compliant_df = make_dataframe_compliant(test_df)
    print("Compliant DataFrame:")
    print(compliant_df.dtypes)
    print()
    
    # Validate compliance
    validation_report = validate_dataframe_compliance(compliant_df)
    print("Validation Report:")
    print(json.dumps(validation_report, indent=2)) 