import re
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Team code mappings for consistency across data sources
TEAM_CODE_MAPPINGS = {
    # Standard NFL team codes
    'ARI': 'ARI', 'ATL': 'ATL', 'BAL': 'BAL', 'BUF': 'BUF',
    'CAR': 'CAR', 'CHI': 'CHI', 'CIN': 'CIN', 'CLE': 'CLE',
    'DAL': 'DAL', 'DEN': 'DEN', 'DET': 'DET', 'GB': 'GB',
    'HOU': 'HOU', 'IND': 'IND', 'JAX': 'JAX', 'KC': 'KC',
    'LAC': 'LAC', 'LAR': 'LAR', 'LV': 'LV', 'MIA': 'MIA',
    'MIN': 'MIN', 'NE': 'NE', 'NO': 'NO', 'NYG': 'NYG',
    'NYJ': 'NYJ', 'PHI': 'PHI', 'PIT': 'PIT', 'SEA': 'SEA',
    'SF': 'SF', 'TB': 'TB', 'TEN': 'TEN', 'WAS': 'WAS',
    
    # Alternative team codes that might appear in different sources
    'GNB': 'GB', 'GBP': 'GB',  # Green Bay Packers
    'KAN': 'KC', 'KCC': 'KC',  # Kansas City Chiefs
    'LVR': 'LV', 'RAI': 'LV', 'OAK': 'LV',  # Las Vegas Raiders
    'LAR': 'LAR', 'RAM': 'LAR',  # Los Angeles Rams
    'LAC': 'LAC', 'SDG': 'LAC',  # Los Angeles Chargers
    'NWE': 'NE', 'NEP': 'NE',   # New England Patriots
    'NOR': 'NO', 'NOS': 'NO',   # New Orleans Saints
    'SFO': 'SF', 'SF9': 'SF',   # San Francisco 49ers
    'TAM': 'TB', 'TBB': 'TB',   # Tampa Bay Buccaneers
    'WAS': 'WAS', 'WSH': 'WAS', # Washington Commanders
}

# Position standardization mappings
POSITION_MAPPINGS = {
    'QB': 'QB', 'RB': 'RB', 'WR': 'WR', 'TE': 'TE',
    'K': 'K', 'DEF': 'DEF', 'DST': 'DEF',
    
    # Alternative position codes
    'QUARTERBACK': 'QB', 'RUNNING BACK': 'RB', 'RUNNINGBACK': 'RB',
    'WIDE RECEIVER': 'WR', 'WIDERECEIVER': 'WR', 'RECEIVER': 'WR',
    'TIGHT END': 'TE', 'TIGHTEND': 'TE',
    'KICKER': 'K', 'PLACEKICKER': 'K',
    'DEFENSE': 'DEF', 'DEFENSE/ST': 'DEF', 'D/ST': 'DEF'
}

# Common player name variations and standardizations
PLAYER_NAME_CORRECTIONS = {
    # Common suffixes and variations
    'Jr.': 'Jr', 'Sr.': 'Sr', 'III': 'III', 'II': 'II', 'IV': 'IV',
    
    # Common name variations (add more as needed)
    'A.J.': 'AJ', 'D.J.': 'DJ', 'C.J.': 'CJ', 'T.J.': 'TJ',
    'J.J.': 'JJ', 'K.J.': 'KJ', 'P.J.': 'PJ', 'R.J.': 'RJ',
    
    # Specific player corrections (examples - add more as discovered)
    'DeAndre Washington': "De'Andre Washington",
    'DAndre Swift': "D'Andre Swift",
    'DeVonta Smith': "DeVonta Smith",
}

class DataNormalizer:
    """
    Utility class for normalizing and standardizing data across different sources.
    """
    
    def __init__(self):
        self.logger = logger
        self.team_mappings = TEAM_CODE_MAPPINGS
        self.position_mappings = POSITION_MAPPINGS
        self.name_corrections = PLAYER_NAME_CORRECTIONS
    
    def normalize_team_code(self, team_code: str) -> str:
        """
        Normalize team codes to standard format.
        
        Args:
            team_code (str): Team code to normalize
            
        Returns:
            str: Standardized team code
        """
        if not team_code or pd.isna(team_code):
            return ""
        
        team_code = str(team_code).strip().upper()
        return self.team_mappings.get(team_code, team_code)
    
    def normalize_position(self, position: str) -> str:
        """
        Normalize position codes to standard format.
        
        Args:
            position (str): Position to normalize
            
        Returns:
            str: Standardized position code
        """
        if not position or pd.isna(position):
            return ""
        
        position = str(position).strip().upper()
        return self.position_mappings.get(position, position)
    
    def normalize_player_name(self, player_name: str) -> str:
        """
        Normalize player names for consistent matching across sources.
        
        Args:
            player_name (str): Player name to normalize
            
        Returns:
            str: Normalized player name
        """
        if not player_name or pd.isna(player_name):
            return ""
        
        # Convert to string and strip whitespace
        name = str(player_name).strip()
        
        # Apply specific corrections
        for old_name, new_name in self.name_corrections.items():
            if old_name in name:
                name = name.replace(old_name, new_name)
        
        # Standardize common patterns
        name = self._standardize_name_patterns(name)
        
        # Clean up extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _standardize_name_patterns(self, name: str) -> str:
        """
        Standardize common name patterns.
        
        Args:
            name (str): Name to standardize
            
        Returns:
            str: Standardized name
        """
        # Standardize apostrophes
        name = name.replace("'", "'")
        
        # Standardize periods in initials
        name = re.sub(r'([A-Z])\.([A-Z])', r'\1.\2', name)
        
        # Standardize Jr/Sr suffixes
        name = re.sub(r'\bJr\.?\b', 'Jr', name)
        name = re.sub(r'\bSr\.?\b', 'Sr', name)
        
        # Standardize Roman numerals
        name = re.sub(r'\bII\b', 'II', name)
        name = re.sub(r'\bIII\b', 'III', name)
        name = re.sub(r'\bIV\b', 'IV', name)
        
        return name
    
    def normalize_numeric_stat(self, value, default: int = 0, allow_float: bool = False):
        """
        Normalize numeric statistics, handling various formats and missing values.
        
        Args:
            value: Value to normalize
            default (int): Default value for missing/invalid data
            allow_float (bool): Whether to return float values (for averages, etc.)
            
        Returns:
            int or float: Normalized numeric value
        """
        if pd.isna(value) or value == '' or value is None:
            return default
        
        try:
            # Handle string representations
            if isinstance(value, str):
                value = value.strip()
                if value == '' or value.lower() in ['na', 'n/a', 'null', 'none']:
                    return default
                
                # Remove any non-numeric characters except decimal point and negative sign
                value = re.sub(r'[^\d.-]', '', value)
                if value == '' or value == '-':
                    return default
            
            # Convert to float first
            float_value = float(value)
            
            # Return float if allowed, otherwise int
            if allow_float:
                return float_value
            else:
                return int(float_value)
            
        except (ValueError, TypeError):
            self.logger.warning(f"Could not normalize numeric value: {value}, using default: {default}")
            return default
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize an entire DataFrame with player data.
        
        Args:
            df (pd.DataFrame): DataFrame to normalize
            
        Returns:
            pd.DataFrame: Normalized DataFrame
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        # Normalize team codes
        if 'Team' in df.columns:
            df['Team'] = df['Team'].apply(self.normalize_team_code)
        
        if 'Opponent' in df.columns:
            df['Opponent'] = df['Opponent'].apply(self.normalize_team_code)
        
        # Normalize positions
        if 'Position' in df.columns:
            df['Position'] = df['Position'].apply(self.normalize_position)
        
        # Normalize player names
        if 'Player' in df.columns:
            df['Player'] = df['Player'].apply(self.normalize_player_name)
        
        # Normalize integer statistics
        integer_columns = [
            'Season', 'Week', 'Pass_Comp', 'Pass_Att', 'Pass_Yards', 'Pass_TD', 'Pass_Int',
            'Rush_Att', 'Rush_Yards', 'Rush_TD', 'Rec_Targets', 'Rec_Recep', 'Rec_Yards', 
            'Rec_TD', 'Snapcount'
        ]
        
        for col in integer_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: self.normalize_numeric_stat(x, allow_float=False))
        
        # Normalize float statistics (averages, points, etc.)
        float_columns = [
            'PPR_Points', 'PPR_Average', 'Reg_League_Avg', 'Reg_Due_For'
        ]
        
        for col in float_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: self.normalize_numeric_stat(x, default=0.0, allow_float=True))
        
        return df
    
    def create_player_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Create a mapping of player name variations to standardized names.
        
        Args:
            df (pd.DataFrame): DataFrame containing player data
            
        Returns:
            Dict[str, str]: Mapping of variations to standard names
        """
        if 'Player' in df.columns:
            unique_players = df['Player'].unique()
            mapping = {}
            
            for player in unique_players:
                normalized = self.normalize_player_name(player)
                if player != normalized:
                    mapping[player] = normalized
            
            return mapping
        
        return {}
    
    def validate_data_consistency(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Validate data consistency and identify potential issues.
        
        Args:
            df (pd.DataFrame): DataFrame to validate
            
        Returns:
            Dict[str, List[str]]: Dictionary of validation issues
        """
        issues = {
            'invalid_teams': [],
            'invalid_positions': [],
            'missing_players': [],
            'negative_stats': [],
            'duplicate_records': []
        }
        
        if df.empty:
            return issues
        
        # Check for invalid team codes
        if 'Team' in df.columns:
            valid_teams = set(self.team_mappings.values())
            invalid_teams = df[~df['Team'].isin(valid_teams)]['Team'].unique()
            issues['invalid_teams'] = list(invalid_teams)
        
        # Check for invalid positions
        if 'Position' in df.columns:
            valid_positions = set(self.position_mappings.values())
            invalid_positions = df[~df['Position'].isin(valid_positions)]['Position'].unique()
            issues['invalid_positions'] = list(invalid_positions)
        
        # Check for missing player names
        if 'Player' in df.columns:
            missing_players = df[df['Player'].isin(['', 'nan', 'NaN']) | df['Player'].isna()]
            if not missing_players.empty:
                issues['missing_players'] = missing_players.index.tolist()
        
        # Check for negative statistics (where they shouldn't be)
        stat_columns = ['Pass_Att', 'Pass_Yards', 'Rush_Att', 'Rush_Yards', 'Rec_Targets', 'Rec_Recep', 'Rec_Yards', 'Snapcount']
        for col in stat_columns:
            if col in df.columns:
                negative_stats = df[df[col] < 0]
                if not negative_stats.empty:
                    issues['negative_stats'].extend([f"{col}: {len(negative_stats)} records"])
        
        # Check for duplicate records
        if all(col in df.columns for col in ['Season', 'Week', 'Player', 'Team']):
            duplicates = df.duplicated(subset=['Season', 'Week', 'Player', 'Team'], keep=False)
            if duplicates.any():
                issues['duplicate_records'] = df[duplicates].index.tolist()
        
        return issues
    
    def merge_player_data(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                         merge_keys: List[str] = None) -> pd.DataFrame:
        """
        Merge two DataFrames with player data, handling name variations.
        
        Args:
            df1 (pd.DataFrame): First DataFrame
            df2 (pd.DataFrame): Second DataFrame
            merge_keys (List[str]): Keys to merge on
            
        Returns:
            pd.DataFrame: Merged DataFrame
        """
        if merge_keys is None:
            merge_keys = ['Season', 'Week', 'Player', 'Team']
        
        # Normalize both DataFrames
        df1_norm = self.normalize_dataframe(df1)
        df2_norm = self.normalize_dataframe(df2)
        
        # Perform the merge
        merged = df1_norm.merge(df2_norm, on=merge_keys, how='left', suffixes=('', '_y'))
        
        # Remove duplicate columns from the merge
        cols_to_drop = [col for col in merged.columns if col.endswith('_y')]
        merged = merged.drop(columns=cols_to_drop)
        
        return merged


# Convenience functions for common operations
def normalize_team_codes(team_codes: List[str]) -> List[str]:
    """Normalize a list of team codes."""
    normalizer = DataNormalizer()
    return [normalizer.normalize_team_code(code) for code in team_codes]

def normalize_player_names(player_names: List[str]) -> List[str]:
    """Normalize a list of player names."""
    normalizer = DataNormalizer()
    return [normalizer.normalize_player_name(name) for name in player_names]

def normalize_positions(positions: List[str]) -> List[str]:
    """Normalize a list of positions."""
    normalizer = DataNormalizer()
    return [normalizer.normalize_position(pos) for pos in positions]

def validate_and_normalize_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    """
    Validate and normalize a DataFrame in one operation.
    
    Args:
        df (pd.DataFrame): DataFrame to process
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, List[str]]]: Normalized DataFrame and validation issues
    """
    normalizer = DataNormalizer()
    
    # Normalize the data
    normalized_df = normalizer.normalize_dataframe(df)
    
    # Validate the normalized data
    issues = normalizer.validate_data_consistency(normalized_df)
    
    return normalized_df, issues


if __name__ == "__main__":
    # Example usage and testing
    normalizer = DataNormalizer()
    
    # Test team code normalization
    test_teams = ['GNB', 'KAN', 'NWE', 'SFO', 'TB']
    normalized_teams = [normalizer.normalize_team_code(team) for team in test_teams]
    print(f"Team normalization: {dict(zip(test_teams, normalized_teams))}")
    
    # Test player name normalization
    test_names = ['A.J. Brown', 'DeAndre Washington', 'C.J. Stroud Jr.']
    normalized_names = [normalizer.normalize_player_name(name) for name in test_names]
    print(f"Name normalization: {dict(zip(test_names, normalized_names))}")
    
    # Test position normalization
    test_positions = ['QUARTERBACK', 'RUNNING BACK', 'WIDE RECEIVER']
    normalized_positions = [normalizer.normalize_position(pos) for pos in test_positions]
    print(f"Position normalization: {dict(zip(test_positions, normalized_positions))}") 