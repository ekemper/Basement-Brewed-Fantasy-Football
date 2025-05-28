# Cron Setup Guide for NFL Data Extraction

This guide shows how to set up automated data extraction using cron and the CLI tool.

## Prerequisites

1. Ensure the CLI tool works correctly:
   ```bash
   cd /path/to/server
   source venv/bin/activate
   python -m cli.extract_season_data --help
   ```

2. Test a dry run:
   ```bash
   python -m cli.extract_season_data --year 2024 --dry-run
   ```

## Basic Cron Setup

### 1. Edit your crontab
```bash
crontab -e
```

### 2. Add environment variables (at the top of crontab)
```bash
# Set PATH to include Python
PATH=/usr/local/bin:/usr/bin:/bin

# Set project paths
PROJECT_DIR=/path/to/Basement-Brewed-Fantasy-Football/server
PYTHON_ENV=/path/to/Basement-Brewed-Fantasy-Football/server/venv/bin/python

# Email for cron notifications (optional)
MAILTO=your-email@example.com
```

## Common Cron Schedules

### Daily Full Season Extraction
Extract complete season data every day at 2 AM:
```bash
0 2 * * * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --output /data/daily/nfl_data_$(date +\%Y\%m\%d).csv
```

### Weekly Backup
Create a weekly backup every Sunday at midnight:
```bash
0 0 * * 0 cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --output /data/weekly/nfl_backup_$(date +\%Y\%m\%d).csv --warm-cache
```

### Game Day Updates
Extract data every hour on Sundays (game day):
```bash
0 * * * 0 cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --output /data/gameday/nfl_update_$(date +\%Y\%m\%d_\%H).csv
```

### Specific Team Monitoring
Monitor specific teams every 6 hours:
```bash
0 */6 * * * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --teams ARI,PHI,DAL --output /data/teams/team_update_$(date +\%Y\%m\%d_\%H).csv
```

### Current Week Focus
Extract current week data every 2 hours during football season:
```bash
0 */2 * * * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --weeks $(date +\%V) --output /data/weekly/week_$(date +\%V)_$(date +\%Y\%m\%d_\%H).csv
```

## Advanced Cron Examples

### Conditional Execution (Football Season Only)
Only run during football season (September through February):
```bash
0 2 * 9-12,1-2 * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --output /data/season/nfl_data_$(date +\%Y\%m\%d).csv
```

### Different Formats for Different Schedules
```bash
# Daily CSV for processing
0 2 * * * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --format csv --output /data/daily/nfl_$(date +\%Y\%m\%d).csv

# Weekly Excel for reports
0 0 * * 0 cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --format excel --output /data/reports/weekly_report_$(date +\%Y\%m\%d).xlsx

# Hourly JSON for APIs
0 * * * * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --format json --output /data/api/nfl_$(date +\%Y\%m\%d_\%H).json
```

### Performance Optimized Schedules
```bash
# Fast extraction with no cache during peak hours
0 */2 9-23 * * 0 cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --no-cache --rate-limit-delay 0.5 --output /data/fast/nfl_$(date +\%Y\%m\%d_\%H).csv

# Slow, comprehensive extraction during off-hours
0 3 * * 1-6 cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --warm-cache --cache-ttl 7200 --output /data/comprehensive/nfl_$(date +\%Y\%m\%d).csv
```

## Logging and Monitoring

### Enable Logging
```bash
# Create log directory
mkdir -p /var/log/nfl-extraction

# Add logging to cron jobs
0 2 * * * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --verbose --log-file /var/log/nfl-extraction/daily_$(date +\%Y\%m\%d).log --output /data/daily/nfl_$(date +\%Y\%m\%d).csv 2>&1
```

### Monitor Cron Job Status
```bash
# Check cron logs
tail -f /var/log/cron

# Check extraction logs
tail -f /var/log/nfl-extraction/daily_$(date +%Y%m%d).log

# List recent extractions
ls -la /data/daily/ | head -10
```

## Error Handling and Notifications

### Email Notifications on Failure
```bash
# Set MAILTO at top of crontab
MAILTO=admin@yourcompany.com

# Cron will automatically email on non-zero exit codes
0 2 * * * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --output /data/daily/nfl_$(date +\%Y\%m\%d).csv
```

### Custom Error Handling Script
Create `/scripts/nfl_extraction_wrapper.sh`:
```bash
#!/bin/bash
set -e

PROJECT_DIR="/path/to/Basement-Brewed-Fantasy-Football/server"
PYTHON_ENV="$PROJECT_DIR/venv/bin/python"
OUTPUT_DIR="/data/extractions"
LOG_DIR="/var/log/nfl-extraction"

# Create directories if they don't exist
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

# Generate filenames
DATE=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/nfl_data_$DATE.csv"
LOG_FILE="$LOG_DIR/extraction_$DATE.log"

# Run extraction
cd "$PROJECT_DIR"
if $PYTHON_ENV -m cli.extract_season_data --year 2024 --output "$OUTPUT_FILE" --log-file "$LOG_FILE" --verbose; then
    echo "✅ Extraction successful: $OUTPUT_FILE" | mail -s "NFL Data Extraction Success" admin@yourcompany.com
    
    # Clean up old files (keep last 30 days)
    find "$OUTPUT_DIR" -name "nfl_data_*.csv" -mtime +30 -delete
    find "$LOG_DIR" -name "extraction_*.log" -mtime +30 -delete
else
    echo "❌ Extraction failed. Check log: $LOG_FILE" | mail -s "NFL Data Extraction FAILED" admin@yourcompany.com
    exit 1
fi
```

Then use in crontab:
```bash
0 2 * * * /scripts/nfl_extraction_wrapper.sh
```

## Directory Structure Recommendations

```
/data/
├── extractions/
│   ├── daily/          # Daily full extractions
│   ├── weekly/         # Weekly backups
│   ├── gameday/        # Game day updates
│   ├── teams/          # Team-specific data
│   └── archive/        # Archived old data
├── logs/
│   ├── cron/           # Cron execution logs
│   └── extraction/     # Extraction process logs
└── scripts/
    ├── wrappers/       # Cron wrapper scripts
    └── cleanup/        # Maintenance scripts
```

## Maintenance Commands

### Check Cron Status
```bash
# List current cron jobs
crontab -l

# Check if cron service is running
systemctl status cron

# View recent cron executions
grep CRON /var/log/syslog | tail -20
```

### Cleanup Old Data
```bash
# Remove files older than 30 days
find /data/extractions -name "*.csv" -mtime +30 -delete
find /data/logs -name "*.log" -mtime +30 -delete

# Archive old data
tar -czf /data/archive/nfl_data_$(date +%Y%m).tar.gz /data/extractions/daily/nfl_data_$(date +%Y%m)*.csv
```

### Test Cron Jobs
```bash
# Test the exact command that cron will run
cd /path/to/server && /path/to/server/venv/bin/python -m cli.extract_season_data --year 2024 --dry-run

# Run with same environment as cron
env -i HOME="$HOME" PATH="/usr/local/bin:/usr/bin:/bin" bash -c 'cd /path/to/server && venv/bin/python -m cli.extract_season_data --year 2024 --dry-run'
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x /scripts/nfl_extraction_wrapper.sh
   chown user:user /data/extractions
   ```

2. **Python Path Issues**
   ```bash
   # Use full path to Python in crontab
   /full/path/to/venv/bin/python -m cli.extract_season_data
   ```

3. **Environment Variables**
   ```bash
   # Source the virtual environment in scripts
   source /path/to/venv/bin/activate
   ```

4. **File Permissions**
   ```bash
   # Ensure output directories are writable
   mkdir -p /data/extractions && chmod 755 /data/extractions
   ```

### Debug Mode
Add debug flags to troubleshoot:
```bash
0 2 * * * cd $PROJECT_DIR && $PYTHON_ENV -m cli.extract_season_data --year 2024 --verbose --dry-run --output /tmp/debug_$(date +\%Y\%m\%d).csv 2>&1 | tee /tmp/cron_debug.log
```

## Best Practices

1. **Always use absolute paths** in cron jobs
2. **Test commands manually** before adding to cron
3. **Set up logging** for all automated jobs
4. **Monitor disk space** for output directories
5. **Use meaningful filenames** with timestamps
6. **Set up email notifications** for failures
7. **Regular cleanup** of old files
8. **Backup important data** regularly
9. **Document your cron schedule** for team members
10. **Use wrapper scripts** for complex operations

This setup provides a robust, automated data extraction system using cron that's much simpler and more reliable than a custom scheduler! 