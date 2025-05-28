# AI Agent Data Extraction Plan: Complete 2024 NFL Season Data Pipeline

## Overview
This document provides detailed step-by-step instructions for an AI agent to create a comprehensive data extraction system that generates a spreadsheet matching the format and structure of `2024 NFL DEFENSE - Raw Player Data.csv`, including snapcount data from Football Guys, for all players across all games in the 2024 NFL season.

## Project Context
- **Framework**: Flask application with existing scraper patterns
- **Target Output**: CSV/Excel file matching `2024 NFL DEFENSE - Raw Player Data.csv` structure and format
- **Source of Truth**: `2024 NFL DEFENSE - Raw Player Data.csv` - this file defines the exact format, columns, and data structure the script should produce
- **Data Sources**: 
  - Existing Football Guys scrapers (game logs)
  - Pro Football Reference scrapers (player offense data)
  - New Football Guys snapcount scraper (to be created)
- **Scope**: All players, all games, entire 2024 season

## Required Columns (from 2024 NFL DEFENSE - Raw Player Data.csv)
- Season, Week, Player, Position, Team, Opponent
- Pass_Comp, Pass_Att, Pass_Yards, Pass_TD, Pass_Int
- Rush_Att, Rush_Yards, Rush_TD
- Rec_Targets, Rec_Recep, Rec_Yards, Rec_TD
- Snapcount (from new scraper)

**Excluded Columns**: PPR_Points, PPR_Average, Reg_League_Avg, Reg_Due_For (these are calculated/advanced analytics fields that should not be included in the script output)

**Note**: The script should produce all core statistical columns from the source CSV but exclude the calculated and advanced analytics fields listed above.

Additional Agent Instructions:

In cases where there are code edits, the ai agent is to perform the changes.

In cases where there are commands to be run, the ai agent is to run them in the chat window context and parse the output for errors and other actionable information.

---

## Phase 1: Environment Setup and Analysis

### Step 1.1: Verify Current Environment
**Goal**: Ensure the development environment is properly configured
**Actions**:
1. Navigate to the server directory: `cd server`
2. Activate virtual environment: `source venv/bin/activate`
3. Verify Python dependencies: `pip list | grep -E "(requests|beautifulsoup4|pandas|flask)"`
4. Manually verify existing scrapers work by running a simple test command

**Success Criteria**: 
- Virtual environment activated successfully
- All required packages present
- Existing scrapers can be imported without errors

### Step 1.2: Analyze Existing Scraper Patterns
**Goal**: Understand current codebase patterns for consistency
**Actions**:
1. Examine `server/football_guys_scrapers/game_logs_scraper.py` structure
2. Review `server/pro_football_reference_scrapers/all_games_scraper.py` patterns
3. Identify common utilities in `server/utils/`
4. Document team mappings and data structures used

**Success Criteria**:
- Clear understanding of existing scraper architecture
- Identified reusable patterns and utilities
- Documented team codes and data structures

---

## Phase 2: Snapcount Scraper Development

### Step 2.1: Create Snapcount Scraper Module
**Goal**: Build dedicated scraper for Football Guys snapcount data
**Actions**:
1. Create `server/football_guys_scrapers/snapcount_scraper.py`
2. Implement scraper following existing patterns:
   - Use same team list from `game_logs_scraper.py`
   - Implement rate limiting and error handling
   - Target URL pattern: `https://www.footballguys.com/stats/snap-counts/teams?team={team}&year=2024`
3. Parse snapcount data by week and player
4. Return structured data matching TSV format requirements

**Code Structure**:
```python
# Key functions to implement:
- scrape_team_snapcounts(team_code, year=2024)
- parse_snapcount_table(soup, team_code)
- get_all_snapcounts(year=2024)
```

**Success Criteria**:
- Scraper successfully extracts snapcount data for all teams
- Data structure matches expected format (Player, Position, Team, Week, Snapcount)
- Error handling for missing data or network issues

### Step 2.2: Validate Snapcount Scraper
**Goal**: Validate snapcount scraper functionality through manual testing
**Actions**:
1. Test single team scraping by running the scraper on a sample team (e.g., ARI)
2. Manually inspect the scraped data structure and content
3. Verify data parsing accuracy by comparing a few records against the website
4. Test error handling by attempting to scrape invalid team codes
5. Verify rate limiting by monitoring request timing during multiple team scrapes
6. **Compare sample output against `2024 NFL DEFENSE - Raw Player Data.csv` format to ensure compatibility**

**Success Criteria**:
- Manual validation confirms accurate data extraction
- Data structure matches expected format from source CSV
- Error handling works correctly for edge cases
- No rate limiting violations during testing

---

## Phase 3: Data Integration Pipeline

### Step 3.1: Create Master Data Orchestrator
**Goal**: Build central coordinator to combine all data sources
**Actions**:
1. Create `server/data_pipeline/master_orchestrator.py`
2. Implement data integration logic:
   - Coordinate existing game logs scraper
   - Integrate Pro Football Reference data
   - Merge snapcount data
   - Handle data normalization and cleaning
3. Implement data validation and quality checks
4. Create progress tracking and logging

**Key Functions**:
```python
- orchestrate_full_season_data(year=2024)
- merge_data_sources(game_logs, pfr_data, snapcounts)
- validate_data_completeness(merged_data)
- export_to_csv(data, filename)
```

**Success Criteria**:
- Successfully coordinates all three data sources
- Produces merged dataset with all required columns
- Implements comprehensive error handling and logging

### Step 3.2: Implement Data Normalization
**Goal**: Ensure consistent data format across all sources
**Actions**:
1. Create `server/utils/data_normalizer.py`
2. Implement normalization functions:
   - Standardize player names across sources
   - Normalize team codes and opponent mappings
   - Handle missing data with appropriate defaults
   - Validate data types and ranges
3. Create mapping tables for team codes and player name variations

**Success Criteria**:
- Consistent player identification across all data sources
- Standardized team codes and opponent mappings
- Proper handling of missing or invalid data

### Step 3.3: Validate Data Integration
**Goal**: Validate complete data pipeline functionality through manual testing
**Actions**:
1. Run data integration for a single week to test the pipeline
2. Manually inspect the merged data for completeness and accuracy
3. Verify that all data sources are properly integrated
4. Test export functionality by generating a sample CSV file
5. Validate data quality by spot-checking player records against source websites
6. **Compare output structure and sample records against `2024 NFL DEFENSE - Raw Player Data.csv` to ensure exact format match**

**Success Criteria**:
- Data pipeline produces complete, accurate dataset for test week
- All data sources properly integrated without conflicts
- Export functionality generates properly formatted CSV matching source format
- Manual spot-checks confirm data accuracy
- **Output format exactly matches `2024 NFL DEFENSE - Raw Player Data.csv` structure**

---

## Phase 4: Performance Optimization and Scaling

### Step 4.1: Implement Caching and Rate Limiting
**Goal**: Optimize scraper performance and respect website limits
**Actions**:
1. Create `server/utils/cache_manager.py`
2. Implement caching strategy:
   - Cache scraped data to avoid re-scraping
   - Implement cache invalidation logic
   - Add cache warming for frequently accessed data
3. Enhance rate limiting across all scrapers
4. Add retry logic with exponential backoff

**Success Criteria**:
- Significant reduction in redundant network requests
- Consistent rate limiting across all scrapers
- Robust error recovery mechanisms

### Step 4.2: Add Progress Tracking and Monitoring
**Goal**: Provide visibility into long-running data extraction process
**Actions**:
1. Create `server/utils/progress_tracker.py`
2. Implement progress tracking:
   - Track completion percentage by team/week
   - Log extraction statistics and timing
   - Provide ETA calculations
   - Generate progress reports
3. Add monitoring for data quality metrics

**Success Criteria**:
- Clear visibility into extraction progress
- Detailed logging for debugging and optimization
- Quality metrics tracking and reporting

---

## Phase 5: Command Line Interface and Automation

### Step 5.1: Create CLI Tool
**Goal**: Provide easy-to-use command line interface for data extraction
**Actions**:
1. Create `server/cli/extract_season_data.py`
2. Implement CLI with options:
   - Full season extraction
   - Specific week/team extraction
   - Output format selection (CSV/Excel)
   - Verbose logging options
3. Add argument parsing and validation
4. Integrate with existing Flask app structure

**CLI Usage Examples**:
```bash
# Extract full 2024 season
python -m server.cli.extract_season_data --year 2024 --output full_season_2024.csv

# Extract specific weeks
python -m server.cli.extract_season_data --year 2024 --weeks 1-4 --output weeks_1_4.csv

# Extract specific teams
python -m server.cli.extract_season_data --year 2024 --teams ARI,PHI --output selected_teams.csv
```

**Success Criteria**:
- Functional CLI with comprehensive options
- Clear help documentation and error messages
- Integration with existing application structure

### Step 5.2: Create Automated Scheduling
**Goal**: Enable automated data extraction and updates
**Actions**:
1. Create `server/automation/scheduler.py`
2. Implement scheduling functionality:
   - Weekly data updates
   - Incremental data extraction
   - Error notification system
   - Data freshness validation
3. Add configuration for automated runs

**Success Criteria**:
- Reliable automated data extraction
- Proper error handling and notification
- Configurable scheduling options

---

## Phase 6: Manual Testing and Validation

### Step 6.1: Comprehensive Manual Testing
**Goal**: Ensure system reliability and data accuracy through manual validation
**Actions**:
1. Test all scraper modules individually:
   - Run each scraper on sample data and verify output
   - Test error handling with invalid inputs
   - Verify rate limiting compliance
2. Test data pipeline integration:
   - Run full pipeline on a subset of data (e.g., 2-3 weeks)
   - Manually verify data merging accuracy
   - Check for duplicate or missing records
3. Validate data quality:
   - **Compare extracted data against `2024 NFL DEFENSE - Raw Player Data.csv` for format consistency**
   - Spot-check player statistics against source websites
   - Verify data completeness across all required columns
   - **Validate that all columns from the source CSV are present and properly formatted**

**Success Criteria**:
- All individual scrapers function correctly
- Data pipeline produces accurate, complete datasets
- **Manual validation confirms data format exactly matches `2024 NFL DEFENSE - Raw Player Data.csv`**
- All required columns present with correct data types

### Step 6.2: Performance Validation
**Goal**: Validate system performance and scalability through manual testing
**Actions**:
1. Run performance tests manually:
   - Time full season extraction and document duration
   - Monitor memory usage during large extractions using system tools
   - Verify rate limiting effectiveness by monitoring request patterns
   - Test extraction of different data subsets (weeks, teams)
2. Document performance baselines and identify optimization opportunities
3. Test system behavior under various load conditions

**Success Criteria**:
- Full season extraction completes within reasonable timeframe
- Memory usage remains within acceptable limits
- Rate limiting prevents website overload
- System performs consistently across different data subsets

---

## Phase 7: Documentation and Deployment

### Step 7.1: Create Comprehensive Documentation
**Goal**: Provide complete documentation for system usage and maintenance
**Actions**:
1. Update `server/README.md` with:
   - System overview and architecture
   - Installation and setup instructions
   - Usage examples and CLI documentation
   - Troubleshooting guide
2. Create API documentation for programmatic access
3. Document data schema and field definitions
4. Create maintenance and monitoring guide

**Success Criteria**:
- Complete, accurate documentation
- Clear setup and usage instructions
- Comprehensive troubleshooting guide

### Step 7.2: Final Integration and Deployment
**Goal**: Integrate system into existing application and prepare for production
**Actions**:
1. Update Flask application to include new endpoints
2. Create API endpoints for data access:
   - `/api/data/extract` - Trigger data extraction
   - `/api/data/status` - Check extraction status
   - `/api/data/download` - Download extracted data
3. Update Docker configuration if needed
4. Create deployment scripts and documentation

**Success Criteria**:
- Seamless integration with existing Flask application
- Functional API endpoints for data access
- Ready for production deployment

---

## Phase 8: Final Validation and Cleanup

### Step 8.1: End-to-End System Test
**Goal**: Validate complete system functionality through comprehensive manual testing
**Actions**:
1. Run full season data extraction and monitor the entire process
2. **Validate output against `2024 NFL DEFENSE - Raw Player Data.csv` format by comparing structure, column names, and data types**
3. Verify data completeness and accuracy through statistical analysis
4. Test all CLI options and API endpoints manually
5. Perform final performance validation under production-like conditions
6. **Conduct detailed comparison of sample records between generated output and source CSV**

**Success Criteria**:
- Complete 2024 season data successfully extracted
- **Output matches `2024 NFL DEFENSE - Raw Player Data.csv` format exactly**
- All system components function correctly
- Performance meets established benchmarks
- **Generated CSV has identical structure and format to source file**

### Step 8.2: Code Review and Cleanup
**Goal**: Ensure code quality and maintainability
**Actions**:
1. Conduct comprehensive code review for consistency and best practices
2. Remove any temporary files or development artifacts
3. Optimize code for performance and readability
4. Update all documentation and comments
5. Ensure consistent coding standards throughout

**Success Criteria**:
- Clean, well-documented codebase
- Consistent coding standards
- No temporary or unnecessary files

---

## Success Metrics

### Data Quality Metrics
- **Completeness**: 95%+ of expected player-game records present
- **Accuracy**: Data matches known samples within 1% variance
- **Consistency**: No duplicate or conflicting records
- **Format Compliance**: Output exactly matches `2024 NFL DEFENSE - Raw Player Data.csv` structure

### Performance Metrics
- **Extraction Time**: Full season extraction < 2 hours
- **Memory Usage**: Peak memory usage < 2GB
- **Error Rate**: < 1% of requests result in errors

### System Metrics
- **Documentation**: Complete documentation for all components
- **Maintainability**: Clear, modular code structure
- **Reliability**: Consistent performance across multiple runs
- **Format Accuracy**: Generated CSV identical in structure to source file

---

## Risk Mitigation

### Technical Risks
- **Website Changes**: Implement robust parsing with fallback strategies
- **Rate Limiting**: Implement conservative rate limiting and retry logic
- **Data Quality**: Comprehensive validation and quality checks

### Operational Risks
- **Long Extraction Times**: Implement progress tracking and resumable extraction
- **Network Issues**: Robust error handling and retry mechanisms

---

## Deliverables

1. **Snapcount Scraper Module** (`server/football_guys_scrapers/snapcount_scraper.py`)
2. **Master Data Orchestrator** (`server/data_pipeline/master_orchestrator.py`)
3. **Data Normalization Utilities** (`server/utils/data_normalizer.py`)
4. **CLI Tool** (`server/cli/extract_season_data.py`)
5. **Complete Documentation** (updated README and guides)
6. **Final Dataset** (CSV file matching `2024 NFL DEFENSE - Raw Player Data.csv` format exactly)

This plan provides a comprehensive roadmap for building a robust, scalable data extraction system that meets all specified requirements while maintaining consistency with existing codebase patterns and conventions. The output will exactly match the format and structure of the provided `2024 NFL DEFENSE - Raw Player Data.csv` file. 