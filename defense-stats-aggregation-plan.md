# Defense Stats Aggregation Plan

## Overview
This document provides detailed step-by-step instructions for an AI agent to aggregate individual player performance data from CSV files into team-level defensive statistics. The goal is to create four aggregate files (all-vs-QB.tsv, all-vs-RB.tsv, all-vs-WR.tsv, all-vs-TE.tsv) from individual team vs position CSV files.

## Data Structure Understanding

### Input Files Location
- Directory: `server/football_guys_scrapers/data/games_logs_against/`
- File naming pattern: `{TEAM}_{POSITION}_vs_{TEAM}.csv`
- Teams: 32 NFL teams (3-letter codes)
- Positions: Quarterbacks, Running_Backs, Wide_Receivers, Tight_Ends

### Column Structures by Position

#### Quarterbacks
- Columns: `name,week,team,cmp,att,pyd,ptd,int,rsh,rshyd,rshtd`
- Key stats: completions, attempts, passing yards, passing TDs, interceptions, rushing yards, rushing TDs

#### Running Backs
- Columns: `name,week,team,rsh,rshyd,rshtd,targ,rec,recyd,rectd`
- Key stats: rushes, rushing yards, rushing TDs, targets, receptions, receiving yards, receiving TDs

#### Wide Receivers
- Columns: `name,week,team,rsh,rshyd,rshtd,targ,rec,recyd,rectd`
- Key stats: rushes, rushing yards, rushing TDs, targets, receptions, receiving yards, receiving TDs

#### Tight Ends
- Columns: `name,week,team,targ,rec,recyd,rectd`
- Key stats: targets, receptions, receiving yards, receiving TDs

### Fantasy Points Calculation (PPR)
Based on `ppr-point-calculations.md`:
- Passing yards: 1 point per 25 yards
- Passing TDs: 6 points
- Interceptions: -2 points
- Rushing yards: 1 point per 10 yards
- Rushing TDs: 6 points
- Receiving yards: 1 point per 10 yards
- Receiving TDs: 6 points
- Receptions: 1 point each (PPR)
- Fumbles lost: -2 points (not in current data)

## Step-by-Step Implementation Plan

### Step 1: Environment Setup and Data Discovery
**Goal**: Set up the working environment and catalog all available data files.

**Actions**:
1. Navigate to the project root directory
2. Create a Python script called `aggregate_defense_stats.py`
3. Import necessary libraries (pandas, os, glob)
4. Scan the `games_logs_against` directory to identify all CSV files
5. Group files by position and validate that all 32 teams have files for each position

**Success Criteria**:
- Script successfully imports required libraries
- All CSV files are identified and categorized by position
- Validation confirms 32 teams × 4 positions = 128 files exist
- Any missing files are identified and reported

**Code Structure**:
```python
import pandas as pd
import os
import glob
from pathlib import Path

# Define constants
DATA_DIR = "server/football_guys_scrapers/data/games_logs_against/"
POSITIONS = ["Quarterbacks", "Running_Backs", "Wide_Receivers", "Tight_Ends"]
TEAMS = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", 
         "DET", "GB", "HOU", "IND", "JAX", "KC", "LAC", "LAR", "LV", "MIA", 
         "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB", 
         "TEN", "WAS"]

def discover_files():
    # Implementation here
    pass
```

### Step 2: Data Loading and Validation Functions
**Goal**: Create robust functions to load and validate individual CSV files.

**Actions**:
1. Create a function to load individual CSV files with error handling
2. Create validation functions to check column structure for each position
3. Create a function to validate data types and handle missing values
4. Test loading functions on sample files from each position

**Success Criteria**:
- Functions successfully load CSV files without errors
- Column validation correctly identifies position-specific structures
- Data type validation handles numeric conversions properly
- Missing value handling is implemented consistently

**Code Structure**:
```python
def load_team_position_data(team, position):
    """Load and validate data for a specific team vs position."""
    pass

def validate_columns(df, position):
    """Validate that DataFrame has expected columns for position."""
    pass

def clean_data(df):
    """Clean and standardize data types."""
    pass
```

### Step 3: Fantasy Points Calculation Engine
**Goal**: Implement accurate fantasy points calculation based on PPR scoring.

**Actions**:
1. Create a function to calculate fantasy points for quarterbacks
2. Create a function to calculate fantasy points for skill position players (RB/WR/TE)
3. Implement proper handling of missing statistics (treat as 0)
4. Test calculations against known examples from existing aggregate files

**Success Criteria**:
- Fantasy points calculations match PPR scoring rules exactly
- Functions handle missing data appropriately
- Test cases validate accuracy against existing aggregate data
- Edge cases (negative yards, etc.) are handled correctly

**Code Structure**:
```python
def calculate_qb_fantasy_points(row):
    """Calculate fantasy points for quarterback performance."""
    fp = 0
    # Passing yards: 1 point per 25 yards
    fp += (row.get('pyd', 0) / 25)
    # Passing TDs: 6 points each
    fp += (row.get('ptd', 0) * 6)
    # Interceptions: -2 points each
    fp -= (row.get('int', 0) * 2)
    # Rushing yards: 1 point per 10 yards
    fp += (row.get('rshyd', 0) / 10)
    # Rushing TDs: 6 points each
    fp += (row.get('rshtd', 0) * 6)
    return fp

def calculate_skill_fantasy_points(row):
    """Calculate fantasy points for RB/WR/TE performance."""
    fp = 0
    # Rushing yards: 1 point per 10 yards
    fp += (row.get('rshyd', 0) / 10)
    # Rushing TDs: 6 points each
    fp += (row.get('rshtd', 0) * 6)
    # Receiving yards: 1 point per 10 yards
    fp += (row.get('recyd', 0) / 10)
    # Receiving TDs: 6 points each
    fp += (row.get('rectd', 0) * 6)
    # Receptions: 1 point each (PPR)
    fp += row.get('rec', 0)
    return fp
```

### Step 4: Team-Level Aggregation Functions
**Goal**: Create functions to aggregate individual player stats to team level.

**Actions**:
1. Create aggregation function for quarterback stats
2. Create aggregation function for running back stats
3. Create aggregation function for wide receiver stats
4. Create aggregation function for tight end stats
5. Implement game counting and averaging calculations
6. Test aggregation on sample teams

**Success Criteria**:
- All relevant statistics are properly summed at team level
- Game counts are accurate
- Averages are calculated correctly
- Touch calculations (for RB/WR) include both rushing and receiving
- Scrimmage yards calculations are accurate

**Code Structure**:
```python
def aggregate_qb_stats(team_data):
    """Aggregate QB stats for a team."""
    agg_stats = {
        'Team': team_data['team'].iloc[0] if len(team_data) > 0 else '',
        'GM': len(team_data['week'].unique()) if len(team_data) > 0 else 0,
        'PYD': team_data['pyd'].sum(),
        'PTD': team_data['ptd'].sum(),
        'INT': team_data['int'].sum(),
        'RSHYD': team_data['rshyd'].sum(),
        'RSHTD': team_data['rshtd'].sum(),
    }
    # Calculate fantasy points
    team_data['fp'] = team_data.apply(calculate_qb_fantasy_points, axis=1)
    agg_stats['FP'] = team_data['fp'].sum()
    return agg_stats

def aggregate_rb_stats(team_data):
    """Aggregate RB stats for a team."""
    # Similar structure for RB stats
    pass

def aggregate_wr_stats(team_data):
    """Aggregate WR stats for a team."""
    # Similar structure for WR stats
    pass

def aggregate_te_stats(team_data):
    """Aggregate TE stats for a team."""
    # Similar structure for TE stats
    pass
```

### Step 5: Ranking and Average Calculation Engine
**Goal**: Calculate averages and rankings for all aggregated statistics.

**Actions**:
1. Create function to calculate per-game averages for all statistics
2. Create function to calculate rankings (1 = worst defense, 32 = best defense)
3. Implement special ratio calculations (FP/REC, FP/RUSH, FP/TCH)
4. Create comprehensive ranking function for all metrics
5. Test ranking calculations against existing files

**Success Criteria**:
- All averages are calculated as total/games played
- Rankings correctly identify best (lowest allowed) and worst (highest allowed) defenses
- Ratio calculations handle division by zero appropriately
- Rankings match the pattern in existing aggregate files

**Code Structure**:
```python
def calculate_averages_and_rankings(df):
    """Calculate per-game averages and rankings for all teams."""
    # Calculate averages
    numeric_cols = ['PYD', 'PTD', 'INT', 'RSHYD', 'RSHTD', 'FP']
    for col in numeric_cols:
        df[f'{col} AVG'] = df[col] / df['GM']
    
    # Calculate rankings (1 = worst defense, higher = better defense)
    for col in numeric_cols:
        if col == 'INT':  # More interceptions = better defense
            df[f'{col} RNK'] = df[f'{col} AVG'].rank(ascending=False, method='min')
        else:  # Less allowed = better defense
            df[f'{col} RNK'] = df[f'{col} AVG'].rank(ascending=True, method='min')
    
    return df
```

### Step 6: Position-Specific Processing Implementation
**Goal**: Implement complete processing pipeline for each position.

**Actions**:
1. Create main processing function for quarterbacks
2. Create main processing function for running backs
3. Create main processing function for wide receivers
4. Create main processing function for tight ends
5. Test each position processor independently
6. Validate output format matches target TSV structure

**Success Criteria**:
- Each position processor generates complete aggregate statistics
- Output format exactly matches existing TSV file structure
- All 32 teams are included in each output
- Column order and naming match target files exactly

**Code Structure**:
```python
def process_quarterbacks():
    """Process all QB data and create aggregate file."""
    all_teams_data = []
    
    for team in TEAMS:
        try:
            # Load team data
            team_data = load_team_position_data(team, "Quarterbacks")
            # Aggregate stats
            agg_stats = aggregate_qb_stats(team_data)
            all_teams_data.append(agg_stats)
        except Exception as e:
            print(f"Error processing {team} quarterbacks: {e}")
    
    # Convert to DataFrame and calculate rankings
    df = pd.DataFrame(all_teams_data)
    df = calculate_averages_and_rankings(df)
    
    return df

# Similar functions for other positions
```

### Step 7: Output File Generation
**Goal**: Generate properly formatted TSV files matching the target structure.

**Actions**:
1. Create function to format and save TSV files
2. Ensure column ordering matches existing files exactly
3. Implement proper number formatting (2 decimal places for averages)
4. Generate all four target files
5. Validate file format and structure

**Success Criteria**:
- TSV files are generated with correct tab separation
- Column headers match existing files exactly
- Number formatting is consistent with existing files
- All 32 teams are present in each file
- Files are saved to correct locations

**Code Structure**:
```python
def save_aggregate_file(df, filename, column_order):
    """Save DataFrame as properly formatted TSV file."""
    # Reorder columns to match target format
    df = df[column_order]
    
    # Format numeric columns
    for col in df.columns:
        if 'AVG' in col or 'FP/' in col:
            df[col] = df[col].round(2)
        elif 'RNK' in col or col in ['GM', 'PYD', 'PTD', 'INT', 'RSHYD', 'RSHTD', 'FP']:
            df[col] = df[col].astype(int)
    
    # Save as TSV
    df.to_csv(filename, sep='\t', index=False)
    print(f"Saved {filename}")
```

### Step 8: Data Validation and Testing
**Goal**: Validate output accuracy against existing aggregate files.

**Actions**:
1. Load existing aggregate files for comparison
2. Compare team totals and averages for accuracy
3. Validate ranking calculations
4. Check for any significant discrepancies
5. Create validation report

**Success Criteria**:
- Generated files match existing files within acceptable tolerance
- Any discrepancies are identified and explained
- Validation report confirms data accuracy
- Edge cases are properly handled

**Code Structure**:
```python
def validate_output(generated_file, reference_file):
    """Compare generated file with reference for validation."""
    gen_df = pd.read_csv(generated_file, sep='\t')
    ref_df = pd.read_csv(reference_file, sep='\t')
    
    # Compare key statistics
    discrepancies = []
    for col in ['Team', 'GM', 'FP', 'FP AVG']:
        if col in gen_df.columns and col in ref_df.columns:
            # Compare values with tolerance for floating point
            pass
    
    return discrepancies
```

### Step 9: Main Execution Pipeline
**Goal**: Create main execution function that orchestrates the entire process.

**Actions**:
1. Create main function that calls all processing steps
2. Implement error handling and logging
3. Add progress reporting
4. Create command-line interface if needed
5. Test complete pipeline execution

**Success Criteria**:
- Main function executes all steps in correct order
- Error handling prevents crashes and provides useful feedback
- Progress is clearly reported to user
- Complete pipeline generates all four target files successfully

**Code Structure**:
```python
def main():
    """Main execution pipeline."""
    print("Starting defense stats aggregation...")
    
    try:
        # Step 1: Discover and validate files
        print("Step 1: Discovering data files...")
        discover_files()
        
        # Step 2-6: Process each position
        positions = [
            ("Quarterbacks", "all-vs-QB.tsv"),
            ("Running_Backs", "all-vs-RB.tsv"),
            ("Wide_Receivers", "all-vs-WR.tsv"),
            ("Tight_Ends", "all-vs-TE.tsv")
        ]
        
        for position, output_file in positions:
            print(f"Processing {position}...")
            # Process position and save file
            
        # Step 8: Validation
        print("Validating output files...")
        # Run validation
        
        print("Aggregation complete!")
        
    except Exception as e:
        print(f"Error in main pipeline: {e}")
        raise

if __name__ == "__main__":
    main()
```

### Step 10: Documentation and Cleanup
**Goal**: Document the process and clean up temporary files.

**Actions**:
1. Add comprehensive docstrings to all functions
2. Create usage documentation
3. Add inline comments for complex calculations
4. Remove any temporary files created during processing
5. Create summary report of processing results

**Success Criteria**:
- All functions have clear docstrings
- Usage documentation is complete and accurate
- Code is well-commented and maintainable
- No temporary files remain after execution
- Summary report provides useful insights

## Testing Strategy

### Unit Testing
- Test each aggregation function with known data
- Validate fantasy points calculations with manual calculations
- Test ranking algorithms with sample data

### Integration Testing
- Process one complete position end-to-end
- Compare output with existing aggregate files
- Test error handling with malformed data

### Validation Testing
- Compare generated files with existing reference files
- Validate statistical accuracy within acceptable tolerance
- Check edge cases and boundary conditions

## Error Handling Strategy

### File-Level Errors
- Missing CSV files: Log warning and continue with available data
- Malformed CSV files: Log error and skip file
- Permission errors: Report and exit gracefully

### Data-Level Errors
- Missing columns: Use default values (0) and log warning
- Invalid data types: Attempt conversion, use 0 if failed
- Negative values: Allow for rushing yards, validate others

### Calculation Errors
- Division by zero: Handle gracefully in ratio calculations
- Ranking ties: Use pandas ranking with 'min' method
- Floating point precision: Round appropriately for output

## Success Metrics

### Accuracy Metrics
- Generated team totals match reference files within 1% tolerance
- Rankings match reference files exactly or within 1 position
- All 32 teams present in each output file

### Completeness Metrics
- All expected columns present in output files
- All statistical categories properly calculated
- No missing or null values in final output

### Performance Metrics
- Complete processing completes within 60 seconds
- Memory usage remains reasonable for dataset size
- Error rate less than 5% of total operations

This plan provides a comprehensive, step-by-step approach for an AI agent to successfully aggregate individual player performance data into team-level defensive statistics while maintaining accuracy and consistency with existing data formats. 