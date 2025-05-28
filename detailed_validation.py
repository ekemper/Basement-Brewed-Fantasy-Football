#!/usr/bin/env python3
"""
Detailed Data Validation Script

This script provides deeper analysis of the data extraction issues.
"""

import pandas as pd
import sys
import os

def analyze_data_issues():
    """Analyze the specific data issues found."""
    
    print("DETAILED DATA ANALYSIS")
    print("="*60)
    
    # Load files
    extracted_file = "2024_nfl_data_weeks_1-1_20250528_025359.csv"
    source_file = "/home/ek/dev/Basement-Brewed-Fantasy-Football/2024 NFL DEFENSE - Raw Player Data.csv"
    
    extracted_df = pd.read_csv(extracted_file)
    source_df = pd.read_csv(source_file)
    
    print(f"Extracted data: {extracted_df.shape}")
    print(f"Source data: {source_df.shape}")
    
    # Check Week 1 data in source
    source_week1 = source_df[source_df['Week'] == 1]
    print(f"Source Week 1 data: {source_week1.shape}")
    
    # Check Arizona Cardinals data specifically
    print("\n" + "="*60)
    print("ARIZONA CARDINALS ANALYSIS")
    print("="*60)
    
    # Extracted ARI data
    extracted_ari = extracted_df[extracted_df['Team'] == 'ARI']
    print(f"Extracted ARI players: {len(extracted_ari)}")
    print("Sample extracted ARI players:")
    for i, row in extracted_ari.head(10).iterrows():
        print(f"  {row['Player']} ({row['Position']}) - Opponent: {row['Opponent']}")
    
    # Source ARI data
    source_ari_week1 = source_df[(source_df['Team'] == 'ARI') & (source_df['Week'] == 1)]
    print(f"\nSource ARI Week 1 players: {len(source_ari_week1)}")
    print("Sample source ARI players:")
    for i, row in source_ari_week1.head(10).iterrows():
        print(f"  {row['Player']} ({row['Position']}) - Opponent: {row['Opponent']}")
    
    # Check opponent format differences
    print("\n" + "="*60)
    print("OPPONENT FORMAT ANALYSIS")
    print("="*60)
    
    extracted_opponents = extracted_df['Opponent'].unique()
    source_opponents = source_df[source_df['Week'] == 1]['Opponent'].unique()
    
    print("Extracted opponent formats (sample):")
    for opp in sorted(extracted_opponents)[:10]:
        print(f"  '{opp}'")
    
    print("\nSource opponent formats (sample):")
    for opp in sorted(source_opponents)[:10]:
        print(f"  '{opp}'")
    
    # Check for specific player matches
    print("\n" + "="*60)
    print("SPECIFIC PLAYER ANALYSIS")
    print("="*60)
    
    # Look for Kyler Murray in both datasets
    extracted_kyler = extracted_df[extracted_df['Player'] == 'Kyler Murray']
    source_kyler = source_df[(source_df['Player'] == 'Kyler Murray') & (source_df['Week'] == 1)]
    
    print("Kyler Murray in extracted data:")
    if not extracted_kyler.empty:
        row = extracted_kyler.iloc[0]
        print(f"  Team: {row['Team']}, Opponent: {row['Opponent']}")
        print(f"  Pass_Comp: {row['Pass_Comp']}, Pass_Att: {row['Pass_Att']}")
        print(f"  Pass_Yards: {row['Pass_Yards']}, Pass_TD: {row['Pass_TD']}")
    else:
        print("  Not found!")
    
    print("\nKyler Murray in source data:")
    if not source_kyler.empty:
        row = source_kyler.iloc[0]
        print(f"  Team: {row['Team']}, Opponent: {row['Opponent']}")
        print(f"  Pass_Comp: {row['Pass_Comp']}, Pass_Att: {row['Pass_Att']}")
        print(f"  Pass_Yards: {row['Pass_Yards']}, Pass_TD: {row['Pass_TD']}")
    else:
        print("  Not found!")
    
    # Check data types
    print("\n" + "="*60)
    print("DATA TYPE ANALYSIS")
    print("="*60)
    
    print("Extracted data types:")
    for col in ['Pass_Comp', 'Pass_Att', 'Pass_Yards', 'Rush_Att', 'Rec_Targets']:
        if col in extracted_df.columns:
            print(f"  {col}: {extracted_df[col].dtype}")
    
    print("\nSource data types:")
    for col in ['Pass_Comp', 'Pass_Att', 'Pass_Yards', 'Rush_Att', 'Rec_Targets']:
        if col in source_df.columns:
            print(f"  {col}: {source_df[col].dtype}")
    
    # Check for zero values
    print("\n" + "="*60)
    print("ZERO VALUES ANALYSIS")
    print("="*60)
    
    # Count zero values in extracted data
    extracted_zeros = {}
    for col in ['Pass_Comp', 'Pass_Att', 'Pass_Yards', 'Rush_Att', 'Rec_Targets']:
        if col in extracted_df.columns:
            zeros = (extracted_df[col] == 0).sum()
            total = len(extracted_df)
            extracted_zeros[col] = f"{zeros}/{total} ({zeros/total*100:.1f}%)"
    
    print("Zero values in extracted data:")
    for col, pct in extracted_zeros.items():
        print(f"  {col}: {pct}")
    
    # Check snapcount data
    print("\n" + "="*60)
    print("SNAPCOUNT ANALYSIS")
    print("="*60)
    
    extracted_snapcount_zeros = (extracted_df['Snapcount'] == 0).sum()
    extracted_snapcount_total = len(extracted_df)
    
    source_week1_snapcount_zeros = (source_week1['Snapcount'] == 0).sum()
    source_week1_snapcount_total = len(source_week1)
    
    print(f"Extracted snapcount zeros: {extracted_snapcount_zeros}/{extracted_snapcount_total} ({extracted_snapcount_zeros/extracted_snapcount_total*100:.1f}%)")
    print(f"Source Week 1 snapcount zeros: {source_week1_snapcount_zeros}/{source_week1_snapcount_total} ({source_week1_snapcount_zeros/source_week1_snapcount_total*100:.1f}%)")
    
    # Check for missing players
    print("\n" + "="*60)
    print("MISSING PLAYERS ANALYSIS")
    print("="*60)
    
    # Players in extracted but not in source
    extracted_players = set(extracted_df['Player'].unique())
    source_week1_players = set(source_week1['Player'].unique())
    
    missing_from_source = extracted_players - source_week1_players
    missing_from_extracted = source_week1_players - extracted_players
    
    print(f"Players in extracted but not in source Week 1: {len(missing_from_source)}")
    if missing_from_source:
        print("Sample missing players:")
        for player in sorted(list(missing_from_source))[:10]:
            print(f"  {player}")
    
    print(f"\nPlayers in source Week 1 but not in extracted: {len(missing_from_extracted)}")
    if missing_from_extracted:
        print("Sample missing players:")
        for player in sorted(list(missing_from_extracted))[:10]:
            print(f"  {player}")

if __name__ == "__main__":
    analyze_data_issues() 