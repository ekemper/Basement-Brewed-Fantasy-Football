#!/usr/bin/env python3
"""
Command Line Interface for NFL Season Data Extraction

This CLI tool provides easy access to the data extraction pipeline with
various options for customizing the extraction scope and output format.
"""

import argparse
import sys
import os
import logging
from datetime import datetime
from typing import List, Optional
import pandas as pd

# Add the server directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.master_orchestrator import OptimizedMasterDataOrchestrator
from football_guys_scrapers.game_logs_scraper import teams
from utils.simple_progress import log_phase, log_step, log_success, log_error, log_stats


def parse_week_range(week_str: str) -> List[int]:
    """
    Parse week range string into list of week numbers.
    
    Examples:
        "1" -> [1]
        "1-4" -> [1, 2, 3, 4]
        "1,3,5" -> [1, 3, 5]
        "1-3,5,7-9" -> [1, 2, 3, 5, 7, 8, 9]
    """
    if not week_str or not week_str.strip():
        return []
    
    weeks = []
    for part in week_str.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = map(int, part.split('-'))
            weeks.extend(range(start, end + 1))
        else:
            weeks.append(int(part))
    return sorted(list(set(weeks)))


def parse_team_list(team_str: str) -> List[str]:
    """
    Parse team list string into list of team codes.
    
    Examples:
        "ARI" -> ["ARI"]
        "ARI,PHI,DAL" -> ["ARI", "PHI", "DAL"]
    """
    return [team.strip().upper() for team in team_str.split(',')]


def validate_teams(team_codes: List[str]) -> List[str]:
    """Validate team codes against available teams."""
    available_teams = [team_code for team_code, _ in teams]
    invalid_teams = [team for team in team_codes if team not in available_teams]
    
    if invalid_teams:
        print(f"❌ Invalid team codes: {invalid_teams}")
        print(f"Available teams: {', '.join(available_teams)}")
        sys.exit(1)
    
    return team_codes


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)


def create_output_filename(year: int, weeks: Optional[List[int]] = None, 
                          teams: Optional[List[str]] = None, 
                          format_type: str = 'csv') -> str:
    """Create a descriptive output filename based on extraction parameters."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if weeks and teams:
        scope = f"weeks_{min(weeks)}-{max(weeks)}_teams_{'_'.join(teams)}"
    elif weeks:
        scope = f"weeks_{min(weeks)}-{max(weeks)}"
    elif teams:
        scope = f"teams_{'_'.join(teams)}"
    else:
        scope = "full_season"
    
    return f"{year}_nfl_data_{scope}_{timestamp}.{format_type}"


def export_data(data: pd.DataFrame, filename: str, format_type: str):
    """Export data in the specified format."""
    try:
        if format_type.lower() == 'csv':
            data.to_csv(filename, index=False)
        elif format_type.lower() == 'excel':
            data.to_excel(filename, index=False, engine='openpyxl')
        elif format_type.lower() == 'json':
            data.to_json(filename, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        log_success(f"Data exported to {filename}")
        
    except Exception as e:
        log_error(f"Failed to export data: {e}")
        sys.exit(1)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Extract NFL season data with various filtering options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract full 2024 season
  python -m server.cli.extract_season_data --year 2024

  # Extract specific weeks
  python -m server.cli.extract_season_data --year 2024 --weeks 1-4

  # Extract specific teams
  python -m server.cli.extract_season_data --year 2024 --teams ARI,PHI,DAL

  # Extract with custom output
  python -m server.cli.extract_season_data --year 2024 --weeks 1-8 --output my_data.csv

  # Extract with optimization disabled
  python -m server.cli.extract_season_data --year 2024 --no-cache --no-rate-limit

  # Verbose logging with log file
  python -m server.cli.extract_season_data --year 2024 --verbose --log-file extraction.log
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--year', 
        type=int, 
        default=2024,
        help='Season year to extract (default: 2024)'
    )
    
    # Filtering options
    parser.add_argument(
        '--weeks',
        type=str,
        help='Week range to extract (e.g., "1-4", "1,3,5", "1-3,5,7-9")'
    )
    
    parser.add_argument(
        '--teams',
        type=str,
        help='Comma-separated list of team codes (e.g., "ARI,PHI,DAL")'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output filename (auto-generated if not specified)'
    )
    
    parser.add_argument(
        '--format',
        choices=['csv', 'excel', 'json'],
        default='csv',
        help='Output format (default: csv)'
    )
    
    # Performance options
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching'
    )
    
    parser.add_argument(
        '--no-rate-limit',
        action='store_true',
        help='Disable rate limiting (use with caution)'
    )
    
    parser.add_argument(
        '--cache-ttl',
        type=int,
        default=3600,
        help='Cache TTL in seconds (default: 3600)'
    )
    
    parser.add_argument(
        '--rate-limit-delay',
        type=float,
        default=1.0,
        help='Rate limit delay in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--warm-cache',
        action='store_true',
        help='Pre-warm cache before extraction'
    )
    
    # Logging options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log to file in addition to console'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be extracted without actually doing it'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose, args.log_file)
    
    # Parse and validate arguments
    weeks = None
    if args.weeks:
        try:
            weeks = parse_week_range(args.weeks)
            if not all(1 <= week <= 18 for week in weeks):
                print("❌ Week numbers must be between 1 and 18")
                sys.exit(1)
        except ValueError as e:
            print(f"❌ Invalid week format: {e}")
            sys.exit(1)
    
    team_codes = None
    if args.teams:
        try:
            team_codes = parse_team_list(args.teams)
            team_codes = validate_teams(team_codes)
        except ValueError as e:
            print(f"❌ Invalid team format: {e}")
            sys.exit(1)
    
    # Create output filename if not specified
    if not args.output:
        args.output = create_output_filename(args.year, weeks, team_codes, args.format)
    
    # Show extraction plan
    log_phase("NFL Data Extraction CLI")
    
    extraction_plan = {
        "Year": args.year,
        "Weeks": f"{min(weeks)}-{max(weeks)}" if weeks else "All weeks",
        "Teams": ", ".join(team_codes) if team_codes else "All teams",
        "Output file": args.output,
        "Output format": args.format,
        "Cache enabled": not args.no_cache,
        "Rate limiting enabled": not args.no_rate_limit,
        "Cache TTL": f"{args.cache_ttl}s" if not args.no_cache else "N/A",
        "Rate limit delay": f"{args.rate_limit_delay}s" if not args.no_rate_limit else "N/A"
    }
    
    log_stats(extraction_plan)
    
    if args.dry_run:
        log_success("Dry run completed - no data extracted")
        return
    
    # Create orchestrator with specified options
    try:
        log_step("Initializing data orchestrator")
        orchestrator = OptimizedMasterDataOrchestrator(
            year=args.year,
            use_cache=not args.no_cache,
            cache_ttl=args.cache_ttl,
            rate_limit_delay=0.1 if args.no_rate_limit else args.rate_limit_delay,
            enable_progress_tracking=True
        )
        
        # Extract data
        log_step("Starting data extraction")
        start_time = datetime.now()
        
        # Note: For now, we extract all data and filter afterwards
        # TODO: Implement week/team filtering in the orchestrator
        data = orchestrator.orchestrate_full_season_data(
            warm_cache=args.warm_cache
        )
        
        # Apply filtering if specified
        if weeks or team_codes:
            log_step("Applying filters to extracted data")
            original_size = len(data)
            
            if weeks:
                data = data[data['Week'].isin(weeks)]
            
            if team_codes:
                data = data[data['Team'].isin(team_codes)]
            
            filtered_size = len(data)
            log_stats({
                "Original records": original_size,
                "Filtered records": filtered_size,
                "Reduction": f"{((original_size - filtered_size) / original_size * 100):.1f}%"
            })
        
        # Export data
        log_step("Exporting data", f"Format: {args.format}")
        export_data(data, args.output, args.format)
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        final_stats = {
            "Total records extracted": len(data),
            "Total processing time": str(duration),
            "Output file": args.output,
            "File size": f"{os.path.getsize(args.output) / 1024 / 1024:.1f} MB" if os.path.exists(args.output) else "Unknown"
        }
        
        log_stats(final_stats)
        log_success("Data extraction completed successfully!")
        
    except KeyboardInterrupt:
        log_error("Extraction cancelled by user")
        sys.exit(1)
    except Exception as e:
        log_error(f"Extraction failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        if 'orchestrator' in locals():
            orchestrator.session.close()


if __name__ == '__main__':
    main() 