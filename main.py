#!/usr/bin/env python3
"""
MÜDEK Alumni Survey - Semi-Automated LinkedIn Messaging System

This is the main orchestrator script that coordinates:
- Reading alumni data from Google Sheets
- Generating personalized messages
- Semi-automated LinkedIn messaging with human-in-the-loop

IMPORTANT: The final SEND action is always performed manually by the user.

Usage:
    python main.py [--template TEMPLATE] [--max MAX_PROFILES] [--delay SECONDS]

Author: MÜDEK Accreditation Team
"""

import argparse
import sys
import time
from typing import Optional

import config
from logger_utils import (
    setup_logger,
    CampaignLogger,
    print_banner,
    print_summary
)
from sheets_reader import GoogleSheetsReader, get_alumni_data
from message_generator import MessageGenerator, generate_personalized_message
from linkedin_automation import LinkedInAutomation


logger = setup_logger("main")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MÜDEK Alumni Survey - Semi-Automated LinkedIn Messaging"
    )
