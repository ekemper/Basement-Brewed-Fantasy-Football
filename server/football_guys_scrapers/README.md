# Footballguys Game Logs Scraper

This README documents how the `game_logs_scraper.py` script extracts and maps player game log data from the Footballguys HTML (e.g., `fbg-gamelogs.html`) to the output columns in the resulting CSV or DataFrame.

## Overview

The script scrapes and parses game log tables for each NFL team and each position group (Quarterbacks, Running Backs, Wide Receivers, Tight Ends). It maps the stats for each player and week into a standardized set of columns for downstream analysis.

## Output Columns

The output columns are defined as follows:

```
Season, Week, Player, Position, Team, Opponent,
Pass_Comp, Pass_Att, Pass_Yards, Pass_TD, Pass_Int,
Rush_Att, Rush_Yards, Rush_TD,
Rec_Targets, Rec_Recep, Rec_Yards, Rec_TD,
PPR_Points, PPR_Average, Snapcount, Reg_League_Avg, Reg_Due_For
```

## Section Keys and Stat Mapping

Each section in the HTML (e.g., Quarterbacks, Running Backs) has a key that describes the format of the stats for each player. The script parses these keys and maps the stats to the output columns as follows:

### Quarterbacks
- **Key:**
  - `Passing Yards - Passing Touchdowns - Interceptions`
  - `Rushes - Rushing Yards - Rushing Touchdowns`
- **Mapping:**
  - First line (e.g., `145-1-1`):
    - `Pass_Yards`, `Pass_TD`, `Pass_Int`
  - Second line (e.g., `6-64-1`):
    - `Rush_Att`, `Rush_Yards`, `Rush_TD`
  - `Pass_Comp` and `Pass_Att` are set to 0 (not available in the source data)
  - Receiving stats are set to 0

### Running Backs
- **Key:**
  - `Rushes - Rushing Yards - Rushing Touchdowns`
  - `Receptions - Receiving Yards - Receiving Touchdowns`
- **Mapping:**
  - First line (e.g., `19-101-0`):
    - `Rush_Att`, `Rush_Yards`, `Rush_TD`
  - Second line (e.g., `2-51-0`):
    - `Rec_Recep`, `Rec_Yards`, `Rec_TD`
  - Passing stats are set to 0
  - `Rec_Targets` is set to 0 (not available in the source data)

### Wide Receivers
- **Key:**
  - `Rushes - Rushing Yards - Rushing Touchdowns`
  - `Receptions - Receiving Yards - Receiving Touchdowns`
- **Mapping:**
  - First line: `Rush_Att`, `Rush_Yards`, `Rush_TD`
  - Second line: `Rec_Recep`, `Rec_Yards`, `Rec_TD`
  - Passing stats are set to 0
  - `Rec_Targets` is set to 0

### Tight Ends
- **Key:**
  - `Receptions - Receiving Yards - Receiving Touchdowns`
- **Mapping:**
  - Only line: `Rec_Recep`, `Rec_Yards`, `Rec_TD`
  - All other stats are set to 0

## General Notes

- If a stat cell is `0`, all mapped stats for that week/player are set to 0.
- If a stat line is missing or incomplete, missing values are padded with zeros.
- The script does not currently extract targets, completions, or attempts unless they are present in the HTML.
- The script is designed to be robust to missing or malformed data, defaulting to zeros where necessary.

## Limitations

- **Targets, Pass Completions/Attempts:** These are not available in the Footballguys HTML and are set to 0 in the output.
- **Other Positions:** Only QB, RB, WR, and TE are supported. Additional positions would require updating the mapping logic.
- **PPR Points, Snapcount, etc.:** These columns are included for compatibility but are not populated by this script.

## Example Mapping

For a Quarterback stat cell:

```
266-3-0<br>5-59-0
```
- `266-3-0` → Pass_Yards: 266, Pass_TD: 3, Pass_Int: 0
- `5-59-0` → Rush_Att: 5, Rush_Yards: 59, Rush_TD: 0

For a Running Back stat cell:

```
19-101-0<br>2-51-0
```
- `19-101-0` → Rush_Att: 19, Rush_Yards: 101, Rush_TD: 0
- `2-51-0` → Rec_Recep: 2, Rec_Yards: 51, Rec_TD: 0

## Updating the Mapping

If the Footballguys HTML format changes or new stat types are added, update the `get_position_and_patterns` and the main parsing logic in `game_logs_scraper.py` accordingly. 