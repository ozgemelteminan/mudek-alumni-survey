"""
Logging utilities for MÜDEK Alumni Survey System.
Provides both console and file logging with CSV export for campaign tracking.
"""

import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
import config


def setup_logger(name: str = "mudek_survey") -> logging.Logger:
    """
    Sets up and returns a configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Log format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    if config.CONSOLE_OUTPUT:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if config.FILE_LOGGING:
        log_file = config.LOGS_DIR / f"survey_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class CampaignLogger:
    """
    Logs campaign actions to a CSV file for tracking and reporting.
    """
    
    def __init__(self, log_path: Optional[Path] = None):
        """
        Initialize the campaign logger.
        
        Args:
            log_path: Path to the CSV log file
        """
        self.log_path = log_path or config.CAMPAIGN_LOG_PATH
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Creates the CSV file with headers if it doesn't exist."""
        if not self.log_path.exists():
            with open(self.log_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "alumni_name",
                    "linkedin_url",
                    "graduation_year",
                    "company",
                    "position",
                    "action",
                    "status",
                    "notes"
                ])
    
    def log_action(
        self,
        alumni_data: dict,
        action: str,
        status: str,
        notes: str = ""
    ):
        """
        Logs a campaign action to the CSV file.
        
        Args:
            alumni_data: Dictionary containing alumni information
            action: Action performed (e.g., "message_prepared", "skipped")
            status: Result status (e.g., "success", "error")
            notes: Additional notes
        """
        with open(self.log_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                alumni_data.get("name", "Unknown"),
                alumni_data.get("linkedin_url", ""),
                alumni_data.get("graduation_year", ""),
                alumni_data.get("company", ""),
                alumni_data.get("position", ""),
                action,
                status,
                notes
            ])
    
    def get_processed_urls(self) -> set:
        """
        Returns a set of LinkedIn URLs that have already been processed.
        
        Returns:
            Set of processed LinkedIn URLs
        """
        processed = set()
        
        if self.log_path.exists():
            with open(self.log_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("status") == "success":
                        processed.add(row.get("linkedin_url", ""))
        
        return processed


def print_banner():
    """Prints the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     MÜDEK Alumni Survey - Semi-Automated Messaging Tool      ║
    ║                                                              ║
    ║     ⚠️  Human-in-the-loop: Final SEND is always manual       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_summary(processed: int, skipped: int, errors: int, total: int):
    """
    Prints the campaign summary.
    
    Args:
        processed: Number of successfully processed profiles
        skipped: Number of skipped profiles
        errors: Number of errors
        total: Total number of profiles
    """
    summary = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CAMPAIGN SUMMARY                          ║
    ╠══════════════════════════════════════════════════════════════╣
    ║   ✅ Processed:   {processed:>5}                                      ║
    ║   ⏭️  Skipped:     {skipped:>5}                                      ║
    ║   ❌ Errors:      {errors:>5}                                      ║
    ║   📊 Total:       {total:>5}                                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(summary)
