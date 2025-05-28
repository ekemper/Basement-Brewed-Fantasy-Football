# TSV Data Mapping Assessment: Football Guys Scrapers Coverage Analysis

## Executive Summary

This document provides a comprehensive assessment of whether the existing Football Guys scrapers can capture all data points required for the TSV file columns. The analysis reveals significant gaps in data availability that will require additional data sources or scraping targets.

## TSV File Column Analysis

### Available Columns (22 total)
```
Season, Week, Player, Position, Team, Opponent, Pass_Comp, Pass_Att, Pass_Yards, 
Pass_TD, Pass_Int, Rush_Att, Rush_Yards, Rush_TD, Rec_Targets, Rec_Recep, 
Rec_Yards, Rec_TD, PPR_Points, PPR_Average, Snapcount, Reg_League_Avg, Reg_Due_For
```

## Data Source Mapping

### ✅ FULLY AVAILABLE from Football Guys Scrapers

| TSV Column | Game Logs Scraper | Game Logs Against Scraper | Notes |
|------------|-------------------|---------------------------|-------|
| `Season` | ✓ (hardcoded 2024) | ✓ (implied) | Available |
| `Week` | ✓ | ✓ | Available |
| `Player` | ✓ | ✓ (`name`) | Available |
| `Position` | ✓ | ✓ (by section) | Available |
| `Team` | ✓ | ✓ | Available |
| `Opponent` | ✓ | ✓ (implied by page) | Available |
| `Pass_Yards` | ✓ | ✓ (`pyd`) | Available |
| `Pass_TD` | ✓ | ✓ (`ptd`) | Available |
| `Pass_Int` | ✓ | ✓ (`int`) | Available |
| `Rush_Att` | ✓ | ✓ (`rsh`) | Available |
| `Rush_Yards` | ✓ | ✓ (`rshyd`) | Available |
| `Rush_TD` | ✓ | ✓ (`rshtd`) | Available |
| `Rec_Recep` | ✓ | ✓ (`rec`) | Available |
| `Rec_Yards` | ✓ | ✓ (`recyd`) | Available |
| `Rec_TD` | ✓ | ✓ (`rectd`) | Available |

### ⚠️ PARTIALLY AVAILABLE from Football Guys Scrapers

| TSV Column | Game Logs Scraper | Game Logs Against Scraper | Gap Analysis |
|------------|-------------------|---------------------------|--------------|
| `Pass_Comp` | ❌ Missing | ✓ (`cmp`) | **CRITICAL GAP**: Game logs scraper doesn't extract completions |
| `Pass_Att` | ❌ Missing | ✓ (`att`) | **CRITICAL GAP**: Game logs scraper doesn't extract attempts |
| `Rec_Targets` | ❌ Missing | ✓ (`targ`) | **CRITICAL GAP**: Game logs scraper doesn't extract targets |

### ❌ NOT AVAILABLE from Football Guys Scrapers

| TSV Column | Availability | Required Data Source |
|------------|--------------|---------------------|
| `PPR_Points` | ❌ Not on Football Guys | External calculation or different source |
| `PPR_Average` | ❌ Not on Football Guys | External calculation or different source |
| `Snapcount` | ❌ Not on Football Guys | Pro Football Reference, ESPN, or NFL.com |
| `Reg_League_Avg` | ❌ Not on Football Guys | Advanced analytics source |
| `Reg_Due_For` | ❌ Not on Football Guys | Advanced analytics source |

## Critical Issues with Current Scrapers

### 1. Game Logs Scraper Data Parsing Issues

**Problem**: The current `game_logs_scraper.py` has significant parsing issues:

```python
# Current problematic parsing in game_logs_scraper.py
if position == "QB":
    if len(stat_lines) == 2:
        pass_yards, pass_td, pass_int = parse_stat_block(stat_lines[0], 3)
        # ❌ MISSING: Pass completions and attempts
```

**Evidence from Current Output**:
```csv
# From fbg_game_logs.csv - Notice Pass_Comp and Pass_Att are always 0
2024,1,Kyler Murray,QB,ARI,@ BUF,0,0,162,1,5,0,0,0,0,0,0,0
```

**Comparison with Game Logs Against Data**:
```csv
# From ARI_Quarterbacks_vs_ARI.csv - Shows completions and attempts ARE available
Josh Allen,1,BUF,18,23,232,2,0,9,39,2
#              ↑  ↑  = cmp, att available
```

### 2. Missing Target Data for Receivers

**Problem**: The `game_logs_scraper.py` sets `Rec_Targets` to 0 for all players:

```python
# Current code always sets targets to 0
"Rec_Targets": 0,
```

**Evidence**: Game logs against scraper shows targets (`targ`) are available on Football Guys.

### 3. Data Format Inconsistencies

**Problem**: The two scrapers parse different data formats:
- **Game Logs Scraper**: Parses condensed format like "145-1-1" 
- **Game Logs Against Scraper**: Parses individual table cells

## Required Actions for Complete Data Coverage

### 1. Fix Game Logs Scraper (HIGH PRIORITY)

**Required Changes**:
```python
# Need to extract completions/attempts for QBs
if position == "QB":
    if len(stat_lines) >= 1:
        # Parse format: "cmp/att-yards-td-int" or similar
        pass_comp, pass_att, pass_yards, pass_td, pass_int = parse_qb_stats(stat_lines[0])
        
# Need to extract targets for receivers
if position in ("RB", "WR", "TE"):
    if len(stat_lines) >= 2:
        # Parse receiving line: "targ-rec-yards-td" or similar
        rec_targets, rec_recep, rec_yards, rec_td = parse_receiving_stats(stat_lines[1])
```

### 2. Add Missing Data Sources (MEDIUM PRIORITY)

**For Snap Counts**:
- **Option 1**: Pro Football Reference scraper
- **Option 2**: ESPN player pages
- **Option 3**: NFL.com snap count data

**For PPR Points**:
- **Option 1**: Calculate from available stats (Rec + Rec_Yards*0.1 + Rec_TD*6 + Rush_Yards*0.1 + Rush_TD*6 + Pass_Yards*0.04 + Pass_TD*4 - Pass_Int*2)
- **Option 2**: FantasyPros or similar fantasy data source

**For Advanced Analytics** (`Reg_League_Avg`, `Reg_Due_For`):
- **Option 1**: Calculate internally using historical data
- **Option 2**: Advanced analytics providers (PFF, Football Outsiders)
- **Option 3**: Build regression models from collected data

### 3. Data Integration Strategy (LOW PRIORITY)

**Recommended Approach**:
1. **Primary Source**: Enhanced game logs scraper (for basic stats)
2. **Secondary Source**: Game logs against scraper (for validation/backup)
3. **Tertiary Sources**: Additional scrapers for missing data

## Implementation Priority

### Phase 1: Critical Fixes (Week 1)
1. Fix `Pass_Comp` and `Pass_Att` extraction in game logs scraper
2. Fix `Rec_Targets` extraction in game logs scraper
3. Validate data accuracy against game logs against scraper

### Phase 2: Missing Data Sources (Week 2-3)
1. Implement snap count scraper (Pro Football Reference recommended)
2. Implement PPR points calculation
3. Create data validation pipeline

### Phase 3: Advanced Analytics (Week 4+)
1. Develop regression analysis for `Reg_League_Avg` and `Reg_Due_For`
2. Implement historical data collection
3. Create predictive modeling pipeline

## Data Quality Validation

### Current Issues
1. **Inconsistent Parsing**: Game logs scraper missing key fields
2. **Zero Values**: Many fields incorrectly set to 0
3. **Format Differences**: Two scrapers use different parsing logic

### Recommended Validation
1. **Cross-Reference**: Compare game logs vs game logs against data
2. **Spot Checks**: Manual verification against official NFL stats
3. **Completeness Checks**: Ensure no missing weeks/players

## Conclusion

**Current Coverage**: 15/22 columns (68%) can be sourced from Football Guys
**Critical Gaps**: 3 columns have parsing issues, 5 columns need external sources

**Immediate Action Required**: Fix the game logs scraper to properly extract completions, attempts, and targets. This will bring coverage to 18/22 columns (82%).

**Long-term Strategy**: Implement additional scrapers for snap counts and calculate PPR/analytics internally to achieve 100% coverage.

The existing Football Guys infrastructure provides a solid foundation, but significant enhancements are needed to achieve complete TSV data coverage for the 2024 season. 