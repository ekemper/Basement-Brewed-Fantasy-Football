# AI Agent Data Extraction Plan: Complete 2024 NFL Season Data Pipeline

## Overview
This document provides detailed step-by-step instructions for an AI agent to create a comprehensive data extraction system that generates a spreadsheet matching the TSV sample format, including snapcount data from Football Guys, for all players across all games in the 2024 NFL season.

## Project Context
- **Framework**: Flask application with existing scraper patterns
- **Target Output**: CSV/Excel file matching `raw-player-data-sample.tsv` structure
- **Data Sources**: 
  - Existing Football Guys scrapers (game logs)
  - Pro Football Reference scrapers (player offense data)
  - New Football Guys snapcount scraper (to be created)
- **Scope**: All players, all games, entire 2024 season

## Required Columns (from TSV sample)
- Season, Week, Player, Position, Team, Opponent
- Pass_Comp, Pass_Att, Pass_Yards, Pass_TD, Pass_Int
- Rush_Att, Rush_Yards, Rush_TD
- Rec_Targets, Rec_Recep, Rec_Yards, Rec_TD
- Snapcount (from new scraper)
- **Excluded**: PPR_Points, PPR_Average (calculable), Reg_League_Avg, Reg_Due_For (advanced analytics)

---

## Phase 1: Environment Setup and Analysis

### Step 1.1: Verify Current Environment
**Goal**: Ensure the development environment is properly configured
**Actions**:
1. Navigate to the server directory: `cd server`
2. Activate virtual environment: `source venv/bin/activate`
3. Verify Python dependencies: `pip list | grep -E "(requests|beautifulsoup4|pandas|flask)"`
4. Run existing tests to ensure baseline functionality: `python -m pytest tests/ -v`

**Success Criteria**: 
- Virtual environment activated successfully
- All required packages present
- Existing tests pass without errors

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

### Step 2.2: Test Snapcount Scraper
**Goal**: Validate snapcount scraper functionality
**Actions**:
1. Create `server/tests/test_snapcount_scraper.py`
2. Implement unit tests:
   - Test single team scraping
   - Test data parsing accuracy
   - Test error handling scenarios
   - Test rate limiting compliance
3. Run tests: `python -m pytest tests/test_snapcount_scraper.py -v`
4. Manual validation with sample team (e.g., ARI)

**Success Criteria**:
- All unit tests pass
- Manual validation confirms accurate data extraction
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

### Step 3.3: Test Data Integration
**Goal**: Validate complete data pipeline functionality
**Actions**:
1. Create `server/tests/test_master_orchestrator.py`
2. Implement integration tests:
   - Test single week data integration
   - Test full season data pipeline
   - Test data quality validation
   - Test export functionality
3. Run comprehensive test suite: `python -m pytest tests/ -v`

**Success Criteria**:
- All integration tests pass
- Data pipeline produces complete, accurate dataset
- Export functionality generates properly formatted CSV

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

## Phase 6: Testing and Validation

### Step 6.1: Comprehensive Testing Suite
**Goal**: Ensure system reliability and data accuracy
**Actions**:
1. Create comprehensive test suite covering:
   - Unit tests for all scraper modules
   - Integration tests for data pipeline
   - End-to-end tests for full extraction
   - Performance tests for large datasets
2. Implement data validation tests:
   - Compare against known good data samples
   - Validate data completeness and accuracy
   - Test edge cases and error scenarios
3. Run full test suite: `python -m pytest tests/ -v --cov=server`

**Success Criteria**:
- 90%+ test coverage across all modules
- All tests pass consistently
- Data validation confirms accuracy against known samples

### Step 6.2: Performance Benchmarking
**Goal**: Validate system performance and scalability
**Actions**:
1. Create `server/tests/test_performance.py`
2. Implement performance tests:
   - Measure extraction time for full season
   - Test memory usage during large extractions
   - Validate rate limiting effectiveness
   - Test concurrent extraction scenarios
3. Document performance baselines and optimization opportunities

**Success Criteria**:
- Full season extraction completes within reasonable timeframe
- Memory usage remains within acceptable limits
- Rate limiting prevents website overload

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
**Goal**: Validate complete system functionality
**Actions**:
1. Run full season data extraction
2. Validate output against TSV sample format
3. Verify data completeness and accuracy
4. Test all CLI options and API endpoints
5. Performance validation under production conditions

**Success Criteria**:
- Complete 2024 season data successfully extracted
- Output matches TSV sample format exactly
- All system components function correctly

### Step 8.2: Code Review and Cleanup
**Goal**: Ensure code quality and maintainability
**Actions**:
1. Conduct comprehensive code review
2. Remove any temporary files or test artifacts
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

### Performance Metrics
- **Extraction Time**: Full season extraction < 2 hours
- **Memory Usage**: Peak memory usage < 2GB
- **Error Rate**: < 1% of requests result in errors

### System Metrics
- **Test Coverage**: 90%+ code coverage
- **Documentation**: Complete documentation for all components
- **Maintainability**: Clear, modular code structure

---

## Risk Mitigation

### Technical Risks
- **Website Changes**: Implement robust parsing with fallback strategies
- **Rate Limiting**: Implement conservative rate limiting and retry logic
- **Data Quality**: Comprehensive validation and quality checks

### Operational Risks
- **Long Extraction Times**: Implement progress tracking and resumable extraction
- **Memory Issues**: Implement streaming data processing for large datasets
- **Network Issues**: Robust error handling and retry mechanisms

---

## Deliverables

1. **Snapcount Scraper Module** (`server/football_guys_scrapers/snapcount_scraper.py`)
2. **Master Data Orchestrator** (`server/data_pipeline/master_orchestrator.py`)
3. **Data Normalization Utilities** (`server/utils/data_normalizer.py`)
4. **CLI Tool** (`server/cli/extract_season_data.py`)
5. **Comprehensive Test Suite** (multiple test files)
6. **Complete Documentation** (updated README and guides)
7. **Final Dataset** (CSV file matching TSV sample format)

This plan provides a comprehensive roadmap for building a robust, scalable data extraction system that meets all specified requirements while maintaining consistency with existing codebase patterns and conventions. 