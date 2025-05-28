import pandas as pd
import time
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import os
import sys

# Add the server directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from football_guys_scrapers.game_logs_scraper import scrape_team as scrape_game_logs_team, teams
from football_guys_scrapers.snapcount_scraper import get_all_snapcounts
# from pro_football_reference_scrapers.all_games_scraper import get_week_links, get_all_game_summaries
from utils.data_normalizer import DataNormalizer, validate_and_normalize_dataframe
from utils.format_compliance import make_dataframe_compliant, validate_dataframe_compliance
from utils.cache_manager import get_cache_manager, CacheManager
from utils.rate_limiter import get_rate_limiter, RateLimiter, RequestSession
from utils.simple_progress import (
    track_progress, log_phase, log_step, log_stats, 
    log_error, log_warning, log_success, SimpleProgress
)

# Set up logging for the data pipeline
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Target columns matching the CSV format (excluding calculated fields)
TARGET_COLUMNS = [
    "Season", "Week", "Player", "Position", "Team", "Opponent",
    "Pass_Comp", "Pass_Att", "Pass_Yards", "Pass_TD", "Pass_Int",
    "Rush_Att", "Rush_Yards", "Rush_TD",
    "Rec_Targets", "Rec_Recep", "Rec_Yards", "Rec_TD",
    "Snapcount"
]

class OptimizedMasterDataOrchestrator:
    """
    Enhanced master orchestrator with performance optimization features including
    caching, rate limiting, and comprehensive progress tracking.
    """
    
    def __init__(self, year: int = 2024, 
                 use_cache: bool = True,
                 cache_ttl: int = 3600,
                 rate_limit_delay: float = 1.0,
                 enable_progress_tracking: bool = True):
        """
        Initialize the optimized master data orchestrator.
        
        Args:
            year (int): Year to extract data for
            use_cache (bool): Whether to use caching
            cache_ttl (int): Cache time-to-live in seconds
            rate_limit_delay (float): Delay between requests in seconds
            enable_progress_tracking (bool): Whether to enable progress tracking
        """
        # Initialize base attributes
        self.year = year
        self.logger = logger
        self.normalizer = DataNormalizer()
        
        # Initialize optimization components
        self.cache_manager = get_cache_manager() if use_cache else None
        self.rate_limiter = get_rate_limiter(default_delay=rate_limit_delay)
        self.cache_ttl = cache_ttl
        
        # Create a requests session with rate limiting
        self.session = RequestSession(rate_limiter=self.rate_limiter)
        
        # Performance metrics
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0,
            'phase_timings': {},
            'start_time': time.time()
        }
        
        # Progress tracking
        self.progress = {
            'start_time': datetime.now(),
            'validation_issues': {},
            'errors': []
        }
        
        self.logger.info(f"Initialized OptimizedMasterDataOrchestrator for {year}")
        if self.cache_manager:
            self.logger.info("Cache manager enabled")
        self.logger.info(f"Rate limiting: {rate_limit_delay}s delay between requests")
    
    def orchestrate_full_season_data(self, output_filename: str = None, 
                                   warm_cache: bool = False) -> pd.DataFrame:
        """
        Orchestrate the complete data extraction process with optimization.
        
        Args:
            output_filename (str, optional): Output CSV filename
            warm_cache (bool): Whether to warm the cache before extraction
            
        Returns:
            pd.DataFrame: Complete merged dataset
        """
        log_phase(f"Full Season {self.year} Data Extraction")
        
        if warm_cache and self.cache_manager:
            log_step("Warming cache")
            self._warm_cache()
        
        try:
            # Phase 1: Extract game logs data
            log_step("Extracting game logs data", "Football Guys scraper")
            phase_start = time.time()
            game_logs_data = self._extract_game_logs_data_optimized()
            self.performance_metrics['phase_timings']['game_logs'] = time.time() - phase_start
            
            # Phase 2: Extract snapcount data
            log_step("Extracting snapcount data", "Football Guys snapcount scraper")
            phase_start = time.time()
            snapcount_data = self._extract_snapcount_data_optimized()
            self.performance_metrics['phase_timings']['snapcounts'] = time.time() - phase_start
            
            # Phase 3: Extract Pro Football Reference data
            # log_step("Extracting Pro Football Reference data", "PFR scraper")
            # phase_start = time.time()
            # pfr_data = self._extract_pfr_data_optimized()
            # self.performance_metrics['phase_timings']['pfr'] = time.time() - phase_start
            
            # Phase 4: Merge all data sources
            log_step("Merging data sources", "Combining game logs and snapcounts")
            phase_start = time.time()
            merged_data = self._merge_data_sources(game_logs_data, snapcount_data)
            self.performance_metrics['phase_timings']['merging'] = time.time() - phase_start
            
            # Phase 5: Validate and clean data
            log_step("Validating and cleaning data", "Data quality checks")
            phase_start = time.time()
            final_data = self._validate_and_clean_data(merged_data)
            self.performance_metrics['phase_timings']['validation'] = time.time() - phase_start
            
            # Phase 6: Export data
            if output_filename:
                log_step("Exporting data", f"Writing to {output_filename}")
                self._export_to_csv(final_data, output_filename)
            
            # Log final statistics
            total_time = time.time() - self.performance_metrics['start_time']
            log_stats({
                "Total records": len(final_data),
                "Total processing time": f"{total_time/60:.1f} minutes",
                "Cache hit rate": f"{self.performance_metrics['cache_hits']}/{self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses']} ({(self.performance_metrics['cache_hits']/(self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses'])*100) if (self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses']) > 0 else 0:.1f}%)",
                "Total requests": self.performance_metrics['total_requests']
            })
            
            log_success(f"Data extraction completed successfully - {len(final_data)} records extracted")
            return final_data
            
        except Exception as e:
            log_error(f"Data extraction failed: {str(e)}")
            raise
        finally:
            # Close session
            self.session.close()
    
    def _warm_cache(self) -> None:
        """Pre-warm cache with frequently accessed data."""
        if not self.cache_manager:
            return
        
        self.logger.info("Warming cache with frequently accessed data...")
        
        # Define cache warming functions
        warm_functions = [
            {
                'function': lambda: [team for team, _ in teams[:5]],  # Sample teams
                'args': (),
                'kwargs': {}
            }
        ]
        
        results = self.cache_manager.warm_cache(warm_functions)
        self.logger.info(f"Cache warming completed: {results}")
    
    def _extract_game_logs_data_optimized(self) -> List[Dict]:
        """Extract game logs data with caching and rate limiting."""
        all_game_logs = []
        
        # Process teams with simple progress tracking
        with track_progress("Processing teams for game logs", len(teams)) as progress:
            for i, (team_code, team_name) in enumerate(teams):
                try:
                    team_data = self._scrape_team_game_logs(team_code, team_name)
                    all_game_logs.extend(team_data)
                    progress.update()
                    
                except Exception as e:
                    log_error(f"Error processing {team_code}: {e}")
                    continue
        
        self.logger.info(f"Extracted {len(all_game_logs)} game log records")
        return all_game_logs
    
    def _extract_snapcount_data_optimized(self) -> List[Dict]:
        """Extract snapcount data with caching."""
        cache_key = f"snapcounts_{self.year}"
        
        # Try cache first
        if self.cache_manager:
            cached_data = self.cache_manager.get('snapcounts', cache_key, ttl=self.cache_ttl)
            if cached_data:
                self.performance_metrics['cache_hits'] += 1
                self.logger.info(f"Retrieved {len(cached_data)} snapcount records from cache")
                return cached_data
            else:
                self.performance_metrics['cache_misses'] += 1
        
        try:
            # Extract fresh data
            snapcount_data = get_all_snapcounts(year=self.year)
            
            # Cache the results
            if self.cache_manager:
                self.cache_manager.set('snapcounts', cache_key, snapcount_data, ttl=self.cache_ttl)
            
            self.logger.info(f"Extracted {len(snapcount_data)} snapcount records")
            return snapcount_data
            
        except Exception as e:
            log_error(f"Error extracting snapcount data: {e}")
            return []
    
    # def _extract_pfr_data_optimized(self) -> List[Dict]:
    #     """Extract Pro Football Reference data with caching."""
    #     cache_key = f"pfr_data_{self.year}"
    #     
    #     # Try cache first
    #     if self.cache_manager:
    #         cached_data = self.cache_manager.get('pfr_data', cache_key, ttl=self.cache_ttl)
    #         if cached_data:
    #             self.performance_metrics['cache_hits'] += 1
    #             self.logger.info(f"Retrieved {len(cached_data)} PFR records from cache")
    #             return cached_data
    #         else:
    #             self.performance_metrics['cache_misses'] += 1
    #     
    #     try:
    #         # Extract limited data for validation
    #         weeks = get_week_links()
    #         pfr_data = get_all_game_summaries(weeks[:2])  # Limit to first 2 weeks
    #         
    #         # Cache the results
    #         if self.cache_manager:
    #             self.cache_manager.set('pfr_data', cache_key, pfr_data, ttl=self.cache_ttl)
    #         
    #         self.logger.info(f"Extracted {len(pfr_data)} PFR game records")
    #         return pfr_data
    #         
    #     except Exception as e:
    #         log_error(f"Error extracting PFR data: {e}")
    #         return []
    
    def _scrape_team_game_logs(self, team_code: str, team_name: str) -> List[Dict]:
        """Scrape game logs for a team with caching."""
        cache_key = f"game_logs_{team_code}_{self.year}"
        
        # Try cache first
        if self.cache_manager:
            cached_data = self.cache_manager.get('game_logs', cache_key, ttl=self.cache_ttl)
            if cached_data:
                self.performance_metrics['cache_hits'] += 1
                return cached_data
            else:
                self.performance_metrics['cache_misses'] += 1
        
        # Extract fresh data with rate limiting
        self.performance_metrics['total_requests'] += 1
        team_data = scrape_game_logs_team(team_code, team_name)
        
        # Cache the results
        if self.cache_manager:
            self.cache_manager.set('game_logs', cache_key, team_data, ttl=self.cache_ttl)
        
        return team_data
    
    def _merge_data_sources(self, game_logs: List[Dict], snapcounts: List[Dict]) -> pd.DataFrame:
        """Merge data sources with enhanced logging."""
        # Convert game logs to DataFrame and normalize
        df_game_logs = pd.DataFrame(game_logs)
        self.logger.info(f"Game logs DataFrame shape: {df_game_logs.shape}")
        
        if not df_game_logs.empty:
            df_game_logs, game_logs_issues = validate_and_normalize_dataframe(df_game_logs)
            self.progress['validation_issues']['game_logs'] = game_logs_issues
            self._log_validation_issues('game_logs', game_logs_issues)
        
        # Convert snapcounts to DataFrame and normalize
        df_snapcounts = pd.DataFrame(snapcounts)
        self.logger.info(f"Snapcounts DataFrame shape: {df_snapcounts.shape}")
        
        if not df_snapcounts.empty:
            df_snapcounts, snapcount_issues = validate_and_normalize_dataframe(df_snapcounts)
            self.progress['validation_issues']['snapcounts'] = snapcount_issues
            self._log_validation_issues('snapcounts', snapcount_issues)
        
        if df_game_logs.empty:
            self.logger.warning("No game logs data available")
            return pd.DataFrame(columns=TARGET_COLUMNS)
        
        # Merge snapcount data with game logs using the normalizer
        if not df_snapcounts.empty:
            merged_df = self.normalizer.merge_player_data(
                df_game_logs, 
                df_snapcounts[['Season', 'Week', 'Player', 'Team', 'Snapcount']], 
                merge_keys=['Season', 'Week', 'Player', 'Team']
            )
            merged_df['Snapcount'] = merged_df['Snapcount'].fillna(0)
            self.logger.info(f"Merged DataFrame shape: {merged_df.shape}")
        else:
            self.logger.warning("No snapcount data available, using game logs only")
            merged_df = df_game_logs.copy()
            merged_df['Snapcount'] = 0
        
        return merged_df
    
    def _validate_and_clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean data with enhanced metrics and format compliance."""
        if data.empty:
            self.logger.warning("No data to validate")
            return pd.DataFrame(columns=TARGET_COLUMNS)
        
        # Apply initial normalization and validation
        normalized_data, initial_issues = validate_and_normalize_dataframe(data)
        self.progress['validation_issues']['final'] = initial_issues
        self._log_validation_issues('final', initial_issues)
        
        # Apply format compliance to ensure proper data types and structure
        source_csv_path = '../2024 NFL DEFENSE - Raw Player Data.csv'
        compliant_data = make_dataframe_compliant(normalized_data, source_csv_path)
        
        # Validate format compliance
        compliance_report = validate_dataframe_compliance(compliant_data, source_csv_path)
        if not compliance_report['compliant']:
            self.logger.warning(f"Format compliance issues: {compliance_report['issues']}")
        else:
            self.logger.info("Data is fully format compliant")
        
        # Ensure all target columns are present
        for col in TARGET_COLUMNS:
            if col not in compliant_data.columns:
                if col in ['Pass_Comp', 'Pass_Att', 'Pass_Yards', 'Pass_TD', 'Pass_Int',
                          'Rush_Att', 'Rush_Yards', 'Rush_TD', 'Rec_Targets', 
                          'Rec_Recep', 'Rec_Yards', 'Rec_TD', 'Snapcount']:
                    compliant_data[col] = 0
                elif col in ['PPR_Points', 'PPR_Average', 'Reg_League_Avg', 'Reg_Due_For']:
                    compliant_data[col] = 0.0
                else:
                    compliant_data[col] = ""
        
        # Select only target columns in the correct order
        final_data = compliant_data[TARGET_COLUMNS]
        
        # Remove rows with missing essential data
        final_data = final_data[final_data['Player'] != '']
        final_data = final_data[final_data['Team'] != '']
        
        # Sort by Season, Week, Team, Player for consistency
        final_data = final_data.sort_values(['Season', 'Week', 'Team', 'Player']).reset_index(drop=True)
        
        self.logger.info(f"Final cleaned dataset shape: {final_data.shape}")
        self._log_data_quality_metrics(final_data)
        
        return final_data
    
    def _export_to_csv(self, data: pd.DataFrame, filename: str) -> None:
        """Export data with format compliance and performance tracking."""
        try:
            # Ensure the output directory exists
            output_dir = os.path.dirname(filename) if os.path.dirname(filename) else '.'
            os.makedirs(output_dir, exist_ok=True)
            
            # Apply final format compliance before export
            source_csv_path = '../2024 NFL DEFENSE - Raw Player Data.csv'
            export_ready_data = make_dataframe_compliant(data, source_csv_path)
            
            # Validate final compliance
            compliance_report = validate_dataframe_compliance(export_ready_data, source_csv_path)
            if compliance_report['compliant']:
                self.logger.info("Export data is format compliant")
            else:
                self.logger.warning(f"Export data compliance issues: {compliance_report['issues']}")
            
            # Export to CSV
            export_start = time.time()
            export_ready_data.to_csv(filename, index=False)
            export_time = time.time() - export_start
            
            self.logger.info(f"Data exported to {filename} in {export_time:.2f}s")
            self.logger.info(f"Exported {len(export_ready_data)} records to {filename}")
            
            # Log data types for verification
            self.logger.info("Export data types:")
            for col, dtype in export_ready_data.dtypes.items():
                self.logger.info(f"  {col}: {dtype}")
            
        except Exception as e:
            error_msg = f"Error exporting data to {filename}: {e}"
            self.logger.error(error_msg)
            self.progress['errors'].append(error_msg)
            raise
    
    def _log_performance_summary(self) -> None:
        """Log comprehensive performance summary."""
        total_time = (datetime.now() - self.progress['start_time']).total_seconds()
        
        self.logger.info("=" * 60)
        self.logger.info("PERFORMANCE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total execution time: {total_time:.2f}s")
        
        # Phase timings
        for phase, timing in self.performance_metrics['phase_timings'].items():
            percentage = (timing / total_time) * 100
            self.logger.info(f"  {phase}: {timing:.2f}s ({percentage:.1f}%)")
        
        # Cache performance
        if self.cache_manager:
            cache_stats = self.cache_manager.get_stats()
            self.logger.info(f"Cache performance:")
            self.logger.info(f"  Hit rate: {cache_stats['hit_rate_percent']:.1f}%")
            self.logger.info(f"  Cache size: {cache_stats['current_size_mb']:.1f} MB")
        
        # Rate limiter performance
        if self.rate_limiter:
            rate_stats = self.rate_limiter.get_stats()
            self.logger.info(f"Rate limiter performance:")
            self.logger.info(f"  Total requests: {rate_stats['total_requests']}")
            self.logger.info(f"  Success rate: {rate_stats['success_rate_percent']:.1f}%")
            self.logger.info(f"  Total delay time: {rate_stats['total_delay_time_seconds']:.2f}s")
        
        # Progress tracker summary
        if self.progress_tracker:
            overall_progress = self.progress_tracker.get_overall_progress()
            self.logger.info(f"Progress tracking:")
            self.logger.info(f"  Total tasks: {overall_progress['total_tasks']}")
            self.logger.info(f"  Completed tasks: {overall_progress['completed_tasks']}")
            self.logger.info(f"  Failed tasks: {overall_progress['failed_tasks']}")
        
        self.logger.info("=" * 60)
    
    def _log_validation_issues(self, source: str, issues: Dict[str, List]) -> None:
        """Log validation issues for a data source."""
        if any(issues.values()):
            self.logger.warning(f"Validation issues found in {source}:")
            for issue_type, issue_list in issues.items():
                if issue_list:
                    self.logger.warning(f"  {issue_type}: {len(issue_list)} issues")
                    if len(issue_list) <= 5:  # Log details for small lists
                        self.logger.warning(f"    Details: {issue_list}")
        else:
            self.logger.info(f"No validation issues found in {source}")
    
    def _log_data_quality_metrics(self, data: pd.DataFrame) -> None:
        """Log data quality metrics."""
        if data.empty:
            self.logger.warning("No data for quality metrics")
            return
        
        total_records = len(data)
        unique_players = data['Player'].nunique()
        unique_teams = data['Team'].nunique()
        weeks_covered = sorted(data['Week'].unique())
        
        # Calculate completeness metrics
        snapcount_coverage = (data['Snapcount'] > 0).sum() / total_records * 100
        
        # Calculate data completeness by position
        position_stats = data.groupby('Position').agg({
            'Player': 'nunique',
            'Snapcount': lambda x: (x > 0).sum() / len(x) * 100
        }).round(1)
        
        self.logger.info(f"Data Quality Metrics:")
        self.logger.info(f"  Total records: {total_records}")
        self.logger.info(f"  Unique players: {unique_players}")
        self.logger.info(f"  Unique teams: {unique_teams}")
        self.logger.info(f"  Weeks covered: {weeks_covered}")
        self.logger.info(f"  Snapcount coverage: {snapcount_coverage:.1f}%")
        self.logger.info(f"  Position breakdown:")
        for pos, stats in position_stats.iterrows():
            self.logger.info(f"    {pos}: {stats['Player']} players, {stats['Snapcount']:.1f}% snapcount coverage")
    
    def get_progress_status(self) -> Dict:
        """Get current progress status with performance metrics."""
        status = self.progress.copy()
        if status['start_time']:
            status['elapsed_time'] = str(datetime.now() - status['start_time'])
        
        # Add performance metrics
        status['performance_metrics'] = self.performance_metrics.copy()
        
        # Add component stats
        if self.cache_manager:
            status['cache_stats'] = self.cache_manager.get_stats()
        
        if self.rate_limiter:
            status['rate_limiter_stats'] = self.rate_limiter.get_stats()
        
        if self.progress_tracker:
            status['progress_tracker_stats'] = self.progress_tracker.get_overall_progress()
        
        return status
    
    def get_validation_summary(self) -> Dict:
        """Get a summary of all validation issues encountered."""
        return self.progress.get('validation_issues', {})
    
    def cleanup_cache(self, older_than_hours: int = 24) -> Dict[str, int]:
        """
        Clean up old cache entries and completed tasks.
        
        Args:
            older_than_hours (int): Remove entries older than this many hours
            
        Returns:
            Dict[str, int]: Cleanup statistics
        """
        cleanup_stats = {}
        
        if self.cache_manager:
            expired_count = self.cache_manager.cleanup_expired()
            cleanup_stats['expired_cache_entries'] = expired_count
        
        if self.progress_tracker:
            completed_tasks = self.progress_tracker.cleanup_completed_tasks(older_than_hours)
            cleanup_stats['completed_tasks'] = completed_tasks
        
        self.logger.info(f"Cleanup completed: {cleanup_stats}")
        return cleanup_stats


# Maintain backward compatibility
class MasterDataOrchestrator(OptimizedMasterDataOrchestrator):
    """Backward compatible alias for the optimized orchestrator."""
    pass


def orchestrate_full_season_data(year: int = 2024, output_filename: str = None,
                                use_optimization: bool = True, **kwargs) -> pd.DataFrame:
    """
    Convenience function to orchestrate full season data extraction.
    
    Args:
        year: Season year
        output_filename: Optional filename to save the data
        use_optimization: Whether to use performance optimizations
        **kwargs: Additional arguments for the orchestrator
        
    Returns:
        pd.DataFrame: Complete merged dataset
    """
    if use_optimization:
        orchestrator = OptimizedMasterDataOrchestrator(year=year, **kwargs)
    else:
        # Use legacy orchestrator for compatibility
        from .master_orchestrator import MasterDataOrchestrator as LegacyOrchestrator
        orchestrator = LegacyOrchestrator(year=year)
    
    return orchestrator.orchestrate_full_season_data(output_filename=output_filename)


if __name__ == "__main__":
    # Example usage with optimization
    output_file = f"2024_nfl_season_data_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Create optimized orchestrator
    orchestrator = OptimizedMasterDataOrchestrator(
        year=2024,
        use_cache=True,
        cache_ttl=3600,  # 1 hour cache
        rate_limit_delay=1.0,
        enable_progress_tracking=True
    )
    
    # Run extraction with cache warming
    data = orchestrator.orchestrate_full_season_data(
        output_filename=output_file,
        warm_cache=True
    )
    
    print(f"Optimized extraction completed. Data shape: {data.shape}")
    
    # Print performance summary
    status = orchestrator.get_progress_status()
    print(f"Performance metrics: {status['performance_metrics']}")
    
    # Cleanup old cache entries
    cleanup_stats = orchestrator.cleanup_cache(older_than_hours=24)
    print(f"Cleanup stats: {cleanup_stats}") 