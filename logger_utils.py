import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
import config


def setup_logger(name: str = "mudek_survey") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Mevcut işleyicileri temizle
    logger.handlers.clear()
    
    # Log formatı
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Konsol
    if config.CONSOLE_OUTPUT:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Dosya
    if config.FILE_LOGGING:
        log_file = config.LOGS_DIR / f"survey_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class CampaignLogger:
    """Takip ve raporlama amacıyla kampanya eylemlerini bir CSV dosyasına kaydeder."""
    
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or config.CAMPAIGN_LOG_PATH
        self._initialize_csv()
    
    def _initialize_csv(self):
        if not self.log_path.exists():
            with open(self.log_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "zaman_damgasi",
                    "mezun_adi",
                    "linkedin_url",
                    "mezuniyet_yili",
                    "sirket",
                    "pozisyon",
                    "eylem",
                    "durum",
                    "notlar"
                ])
    
    def log_action(self, alumni_data: dict, action: str, status: str, notes: str = ""):
        with open(self.log_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                alumni_data.get("name", "Bilinmiyor"),
                alumni_data.get("linkedin_url", ""),
                alumni_data.get("graduation_year", ""),
                alumni_data.get("company", ""),
                alumni_data.get("position", ""),
                action,
                status,
                notes
            ])
    
    def get_processed_urls(self) -> set:
        processed = set()
        if self.log_path.exists():
            with open(self.log_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("durum") == "Gönderildi": # Status success/gönderildi uyumu
                        processed.add(row.get("linkedin_url", ""))
        return processed


def print_banner():
    """Uygulama banner'ını (başlık) ekrana basar."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     MÜDEK Mezun Anketi - TAM OTOMATİK Mesajlaşma Aracı       ║
    ║                                                              ║
    ║     🚀 Mod: Otonom Gönderim (Kullanıcı müdahalesi gerekmez)  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_summary(processed: int, skipped: int, errors: int, total: int):
    """Kampanya özetini ekrana basar."""
    summary = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    KAMPANYA SONUCU                           ║
    ╠══════════════════════════════════════════════════════════════╣
    ║   ✅ Gönderilen:  {processed:>5}                             ║        
    ║   ⏭️  Atlanan:     {skipped:>5}                              ║       
    ║   ❌ Hatalar:     {errors:>5}                                ║      
    ║   📊 Toplam:      {total:>5}                                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(summary)