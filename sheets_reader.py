"""
Google Sheets integration module for MÜDEK Alumni Survey System.
Handles reading alumni data and updating status columns.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Optional
import config
from logger_utils import setup_logger

logger = setup_logger(__name__)


class GoogleSheetsReader:
    """
    Handles all Google Sheets operations for alumni data management.
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize the Google Sheets client."""
        self.credentials_path = credentials_path or config.CREDENTIALS_PATH
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self._connect()
    
    def _connect(self):
        """Establishes connection to Google Sheets API."""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets"
            ]
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                str(self.credentials_path), scope
            )
            
            self.client = gspread.authorize(credentials)
            logger.info("Successfully connected to Google Sheets API")
            
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.credentials_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    
    def open_spreadsheet(
        self, 
        spreadsheet_name: Optional[str] = None,
        worksheet_name: Optional[str] = None
    ):
        """Opens the specified spreadsheet and worksheet."""
        spreadsheet_name = spreadsheet_name or config.SPREADSHEET_NAME
        worksheet_name = worksheet_name or config.WORKSHEET_NAME
        
        try:
            self.spreadsheet = self.client.open(spreadsheet_name)
            self.worksheet = self.spreadsheet.worksheet(worksheet_name)
            logger.info(f"Opened spreadsheet: {spreadsheet_name}/{worksheet_name}")
            
        except gspread.SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found: {spreadsheet_name}")
            logger.info("Make sure to share the spreadsheet with your service account email")
            raise
        except gspread.WorksheetNotFound:
            logger.error(f"Worksheet not found: {worksheet_name}")
            raise
    
    def get_all_alumni(self) -> List[Dict]:
        """
        Retrieves all alumni records from the worksheet.
        """
        if not self.worksheet:
            self.open_spreadsheet()
        
        try:
            # Get all records
            records = self.worksheet.get_all_records()
            
            # Normalize column names using config mapping
            normalized_records = []
            
            # --- DÜZELTME BURADA: enumerate ile sıra numarasını alıyoruz ---
            for i, record in enumerate(records):
                normalized = {}
                for key, sheet_column in config.COLUMN_MAPPING.items():
                    normalized[key] = record.get(sheet_column, "")
                
                # Orijinal veri ve SATIR NUMARASINI kaydet
                normalized["_original"] = record
                normalized["_row_num"] = i  # Kritik ekleme bu!
                
                normalized_records.append(normalized)
            
            logger.info(f"Retrieved {len(normalized_records)} alumni records")
            return normalized_records
            
        except Exception as e:
            logger.error(f"Failed to retrieve alumni data: {e}")
            raise
    
    def get_pending_alumni(self) -> List[Dict]:
        """Retrieves only alumni with pending status."""
        all_alumni = self.get_all_alumni()
        
        pending = [
            alumni for alumni in all_alumni
            if alumni.get("status", "").strip() in ["", config.STATUS_PENDING]
        ]
        
        logger.info(f"Found {len(pending)} pending alumni records")
        return pending
    
    def update_status(self, row_index: int, status: str, notes: str = ""):
        """Updates the status column for a specific alumni."""
        if not self.worksheet:
            self.open_spreadsheet()
        
        try:
            # Find the status column
            headers = self.worksheet.row_values(1)
            status_col_name = config.COLUMN_MAPPING.get("status", "Durum")
            
            if status_col_name in headers:
                status_col = headers.index(status_col_name) + 1
                # Row index + 2 (1 for 0-based to 1-based, 1 for header row)
                actual_row = row_index + 2
                self.worksheet.update_cell(actual_row, status_col, status)
                logger.debug(f"Updated row {actual_row} status to: {status}")
            else:
                logger.warning(f"Status column '{status_col_name}' not found")
                
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    def find_alumni_row(self, linkedin_url: str) -> Optional[int]:
        """Finds the row index of an alumni by their LinkedIn URL."""
        if not self.worksheet:
            self.open_spreadsheet()
        
        try:
            url_column = config.COLUMN_MAPPING.get("linkedin_url", "LinkedIn URL")
            headers = self.worksheet.row_values(1)
            
            if url_column in headers:
                col_index = headers.index(url_column) + 1
                cell = self.worksheet.find(linkedin_url, in_column=col_index)
                if cell:
                    return cell.row - 2  # Convert to 0-based
            return None
            
        except Exception as e:
            logger.error(f"Error finding alumni row: {e}")
            return None

def get_alumni_data(
    spreadsheet_name: Optional[str] = None,
    worksheet_name: Optional[str] = None,
    only_pending: bool = True
) -> List[Dict]:
    """Convenience function to get alumni data."""
    reader = GoogleSheetsReader()
    reader.open_spreadsheet(spreadsheet_name, worksheet_name)
    
    if only_pending:
        return reader.get_pending_alumni()
    else:
        return reader.get_all_alumni()

if __name__ == "__main__":
    print("Testing Google Sheets Connection...")
    print("-" * 50)
    try:
        reader = GoogleSheetsReader()
        reader.open_spreadsheet()
        alumni = reader.get_all_alumni()
        print(f"\n✅ Successfully retrieved {len(alumni)} records")
        if alumni:
            print("\nFirst record sample:")
            print(f"  Row Number: {alumni[0].get('_row_num')}")
            for key, value in alumni[0].items():
                if key not in ["_original", "_row_num"]:
                    print(f"  {key}: {value}")
    except Exception as e:
        print(f"\n❌ Error: {e}")