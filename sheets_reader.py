import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Optional
import config
from logger_utils import setup_logger

logger = setup_logger(__name__)


class GoogleSheetsReader:
    """
    Mezun veri yönetimi için tüm Google E-Tablolar işlemlerini yürütür.
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        # Google E-Tablolar istemcisini başlatır.
        self.credentials_path = credentials_path or config.CREDENTIALS_PATH
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self._connect()
    
    def _connect(self):
        # Google Sheets API ile bağlantı kurar.
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
            logger.info("Google Sheets API'ye başarıyla bağlanıldı")
            
        except FileNotFoundError:
            logger.error(f"Kimlik doğrulama dosyası bulunamadı: {self.credentials_path}")
            raise
        except Exception as e:
            logger.error(f"Google Sheets'e bağlanılamadı: {e}")
            raise
    
    def open_spreadsheet(
        self, 
        spreadsheet_name: Optional[str] = None,
        worksheet_name: Optional[str] = None
    ):
        # Belirtilen e-tabloyu ve çalışma sayfasını açar.
        spreadsheet_name = spreadsheet_name or config.SPREADSHEET_NAME
        worksheet_name = worksheet_name or config.WORKSHEET_NAME
        
        try:
            self.spreadsheet = self.client.open(spreadsheet_name)
            self.worksheet = self.spreadsheet.worksheet(worksheet_name)
            logger.info(f"E-Tablo açıldı: {spreadsheet_name}/{worksheet_name}")
            
        except gspread.SpreadsheetNotFound:
            logger.error(f"E-Tablo bulunamadı: {spreadsheet_name}")
            logger.info("E-tabloyu servis hesabı e-postasıyla paylaştığınızdan emin olun")
            raise
        except gspread.WorksheetNotFound:
            logger.error(f"Çalışma sayfası bulunamadı: {worksheet_name}")
            raise
    
    def get_all_alumni(self) -> List[Dict]:
        """
        Çalışma sayfasındaki tüm mezun kayıtlarını çeker.
        """
        if not self.worksheet:
            self.open_spreadsheet()
        
        try:
            # Tüm kayıtları al
            records = self.worksheet.get_all_records()
            
            # Config eşleşmelerini kullanarak sütun isimlerini standartlaştır
            normalized_records = []
            
            # --- enumerate ile sıra numarasını alıyoruz ---
            for i, record in enumerate(records):
                normalized = {}
                for key, sheet_column in config.COLUMN_MAPPING.items():
                    normalized[key] = record.get(sheet_column, "")
                
                # Orijinal veri ve SATIR NUMARASINI kaydet
                normalized["_original"] = record
                normalized["_row_num"] = i  
                
                normalized_records.append(normalized)
            
            logger.info(f"{len(normalized_records)} adet mezun kaydı çekildi")
            return normalized_records
            
        except Exception as e:
            logger.error(f"Mezun verileri alınırken hata oluştu: {e}")
            raise
    
    def get_pending_alumni(self) -> List[Dict]:
        # Sadece 'beklemede' (işlem yapılmamış) durumundaki mezunları getirir.
        all_alumni = self.get_all_alumni()
        
        pending = [
            alumni for alumni in all_alumni
            if alumni.get("status", "").strip() in ["", config.STATUS_PENDING]
        ]
        
        logger.info(f"{len(pending)} adet beklemede olan mezun kaydı bulundu")
        return pending
    
    def update_status(self, row_index: int, status: str, notes: str = ""):
        # Belirli bir mezun için durum sütununu günceller.
        if not self.worksheet:
            self.open_spreadsheet()
        
        try:
            # Durum sütununu bul
            headers = self.worksheet.row_values(1)
            status_col_name = config.COLUMN_MAPPING.get("status", "Durum")
            
            if status_col_name in headers:
                status_col = headers.index(status_col_name) + 1
                # Satır indeksi + 2 (0-tabanlıdan 1-tabanlıya geçiş + başlık satırı)
                actual_row = row_index + 2
                self.worksheet.update_cell(actual_row, status_col, status)
                logger.debug(f"{actual_row}. satır durumu güncellendi: {status}")
            else:
                logger.warning(f"Durum sütunu '{status_col_name}' bulunamadı")
                
        except Exception as e:
            logger.error(f"Durum güncelleme hatası: {e}")
    
    def find_alumni_row(self, linkedin_url: str) -> Optional[int]:
        # LinkedIn URL'sine göre bir mezunun satır numarasını bulur.
        if not self.worksheet:
            self.open_spreadsheet()
        
        try:
            url_column = config.COLUMN_MAPPING.get("linkedin_url", "LinkedIn URL")
            headers = self.worksheet.row_values(1)
            
            if url_column in headers:
                col_index = headers.index(url_column) + 1
                cell = self.worksheet.find(linkedin_url, in_column=col_index)
                if cell:
                    return cell.row - 2  # 0-tabanlı indekse çevir
            return None
            
        except Exception as e:
            logger.error(f"Mezun satırı bulma hatası: {e}")
            return None

def get_alumni_data(
    spreadsheet_name: Optional[str] = None,
    worksheet_name: Optional[str] = None,
    only_pending: bool = True
) -> List[Dict]:
    # Mezun verilerini almak için yardımcı fonksiyon.
    reader = GoogleSheetsReader()
    reader.open_spreadsheet(spreadsheet_name, worksheet_name)
    
    if only_pending:
        return reader.get_pending_alumni()
    else:
        return reader.get_all_alumni()

if __name__ == "__main__":
    print("Google E-Tablolar Bağlantısı Test Ediliyor...")
    print("-" * 50)
    try:
        reader = GoogleSheetsReader()
        reader.open_spreadsheet()
        alumni = reader.get_all_alumni()
        print(f"\n✅ {len(alumni)} adet kayıt başarıyla çekildi")
        if alumni:
            print("\nİlk kayıt örneği:")
            print(f"  Satır Numarası: {alumni[0].get('_row_num')}")
            for key, value in alumni[0].items():
                if key not in ["_original", "_row_num"]:
                    print(f"  {key}: {value}")
    except Exception as e:
        print(f"\n❌ Hata: {e}")