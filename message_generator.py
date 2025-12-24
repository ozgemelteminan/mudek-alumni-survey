from typing import Dict, Optional
from string import Template
import config
from logger_utils import setup_logger

logger = setup_logger(__name__)


# ---------- MESAJ ŞABLONLARI ------------

# Türkçe resmi şablon
TEMPLATE_TR_FORMAL = """Sayın {name},

{university} {faculty} {department} olarak, {graduation_year} yılı mezunlarımızla iletişime geçmekten büyük mutluluk duyuyoruz.

Bölümümüz şu anda MÜDEK (Mühendislik Eğitim Programları Değerlendirme ve Akreditasyon Derneği) akreditasyon sürecinde olup, mezunlarımızın değerli görüşleri bu süreçte kritik önem taşımaktadır.

Sizden ricamız, aşağıdaki kısa anketi (yaklaşık 5-10 dakika) doldurarak eğitim programımızın geliştirilmesine katkıda bulunmanızdır:

🔗 {survey_url}

Şu anki profesyonel konumunuz ({position} - {company}) göz önüne alındığında, sektör deneyimleriniz ve eğitim sürecinize dair geri bildirimleriniz bizim için son derece değerlidir.

Katılımınız için şimdiden teşekkür ederiz.

Saygılarımızla,
{department}
{contact_email}"""


# Türkçe yarı resmi şablon (Daha samimi)
TEMPLATE_TR_SEMIFORMAL = """Merhaba {name},

{graduation_year} yılı mezunu olarak sizinle iletişime geçmek istedik.

Bölümümüzün MÜDEK akreditasyon çalışmaları kapsamında mezun görüşlerini topluyoruz. Kısa anketimize katılarak bize destek olabilir misiniz?

📋 Anket: {survey_url}

{company} şirketindeki {position} pozisyonunuzdaki deneyimlerinizi duymak isteriz.

Teşekkürler!

{department}"""


# İngilizce resmi şablon 
TEMPLATE_EN_FORMAL = """Dear {name},

We are reaching out to you as a {graduation_year} graduate of {department}, {university}.

Our department is currently undergoing MÜDEK accreditation, and alumni feedback is an essential component of this quality assurance process.

We would greatly appreciate if you could take a few minutes to complete our alumni survey:

🔗 {survey_url}

Given your current role as {position} at {company}, your insights on how our program prepared you for your career would be invaluable.

Thank you for your time and continued connection with our department.

Best regards,
{department}
{contact_email}"""


# Şablon eşleşmeleri
TEMPLATES = {
    "tr_formal": TEMPLATE_TR_FORMAL,
    "tr_semiformal": TEMPLATE_TR_SEMIFORMAL,
    "en_formal": TEMPLATE_EN_FORMAL
}


class MessageGenerator:
    """
    Mezun iletişimi için kişiselleştirilmiş mesajlar oluşturur.
    """
    
    def __init__(self, template_key: str = "tr_formal"):
        """
        Mesaj oluşturucuyu başlatır.
        
        Args:
            template_key: Kullanılacak şablon anahtarı (örn: 'tr_formal')
        """
        self.template_key = template_key
        self.base_template = TEMPLATES.get(template_key, TEMPLATE_TR_FORMAL)
        
        # Config dosyasından gelen varsayılan yer tutucular
        self.defaults = {
            "university": config.UNIVERSITY_NAME,
            "faculty": config.FACULTY_NAME,
            "department": config.DEPARTMENT_NAME,
            "survey_url": config.SURVEY_URL,
            "contact_email": config.CONTACT_EMAIL,
            "contact_phone": config.CONTACT_PHONE
        }
    
    def generate(self, alumni: Dict, custom_template: Optional[str] = None) -> str:
        """
        Bir mezun için kişiselleştirilmiş mesaj metni üretir.
        
        Args:
            alumni: Mezun verilerini içeren sözlük
            custom_template: (İsteğe bağlı) Özel şablon metni
            
        Returns:
            Kişiselleştirilmiş mesaj metni (str)
        """
        template = custom_template or self.base_template
        
        # Varsayılanları kopyala
        placeholders = {**self.defaults}
        
        # Mezuna özel verileri ekle
        placeholders["name"] = alumni.get("name", "Değerli Mezunumuz")
        placeholders["graduation_year"] = alumni.get("graduation_year", "")
        placeholders["company"] = alumni.get("company", "şirketiniz")
        placeholders["position"] = alumni.get("position", "pozisyonunuz")
        
        # Boş veriler için mantıklı varsayılanlar ata (Cümle akışını bozmamak için)
        if not placeholders["company"]:
            placeholders["company"] = "mevcut şirketiniz"
        if not placeholders["position"]:
            placeholders["position"] = "mevcut pozisyonunuz"
        if not placeholders["graduation_year"]:
            placeholders["graduation_year"] = "geçmiş"
        
        try:
            message = template.format(**placeholders)
            logger.debug(f"Mesaj oluşturuldu: {alumni.get('name', 'Bilinmiyor')}")
            return message
            
        except KeyError as e:
            logger.error(f"Şablonda eksik yer tutucu (placeholder): {e}")
            raise
    
    def preview(self, alumni: Dict) -> str:
        """
        Mesajın önizlemesini formatlı bir şekilde oluşturur.
        
        Args:
            alumni: Mezun verilerini içeren sözlük
            
        Returns:
            Formatlanmış önizleme metni
        """
        message = self.generate(alumni)
        
        preview = f"""
{'='*60}
📧 MESAJ ÖNİZLEME
{'='*60}
Kime: {alumni.get('name', 'Bilinmiyor')} ({alumni.get('linkedin_url', 'URL Yok')})
{'='*60}

{message}

{'='*60}
"""
        return preview
    
    @staticmethod
    def list_templates() -> Dict[str, str]:
        """
        Mevcut şablonları açıklamalarıyla birlikte döndürür.
        
        Returns:
            Şablon anahtarları ve açıklamaları sözlüğü
        """
        return {
            "tr_formal": "Türkçe - Resmi üslup (Varsayılan)",
            "tr_semiformal": "Türkçe - Yarı resmi / Samimi",
            "en_formal": "İngilizce - Resmi üslup"
        }


def generate_personalized_message(
    alumni: Dict,
    template_key: str = "tr_formal",
    custom_template: Optional[str] = None
) -> str:
    """
    Kişiselleştirilmiş mesaj oluşturmak için yardımcı (wrapper) fonksiyon.
    
    Args:
        alumni: Mezun verisi
        template_key: Kullanılacak şablon
        custom_template: Özel şablon
        
    Returns:
        Hazır mesaj metni
    """
    generator = MessageGenerator(template_key)
    
    if custom_template:
        return generator.generate(alumni, custom_template)
    
    return generator.generate(alumni)



# ---------- BAĞIMSIZ TEST  ----------

if __name__ == "__main__":
    print("Mesaj Oluşturucu Test Ediliyor...")
    print("-" * 50)
    
    # Örnek mezun verisi
    test_alumni = {
        "name": "Ahmet Yılmaz",
        "linkedin_url": "https://linkedin.com/in/ahmetyilmaz",
        "graduation_year": "2018",
        "company": "Google",
        "position": "Senior Software Engineer"
    }
    
    generator = MessageGenerator("tr_formal")
    
    print("\nMevcut Şablonlar:")
    for key, desc in MessageGenerator.list_templates().items():
        print(f"  - {key}: {desc}")
    
    print(generator.preview(test_alumni))