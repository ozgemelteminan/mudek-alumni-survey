"""
Message template generation module for MÜDEK Alumni Survey System.
Handles personalized message creation with dynamic variables.
"""

from typing import Dict, Optional
from string import Template
import config
from logger_utils import setup_logger

logger = setup_logger(__name__)


# =============================================================================
# MESSAGE TEMPLATES
# =============================================================================

# Turkish formal template
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


# Turkish semi-formal template
TEMPLATE_TR_SEMIFORMAL = """Merhaba {name},

{graduation_year} yılı mezunu olarak sizinle iletişime geçmek istedik.

Bölümümüzün MÜDEK akreditasyon çalışmaları kapsamında mezun görüşlerini topluyoruz. Kısa anketimize katılarak bize destek olabilir misiniz?

📋 Anket: {survey_url}

{company} şirketindeki {position} pozisyonunuzdaki deneyimlerinizi duymak isteriz.

Teşekkürler!

{department}"""


# English formal template
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


# Template mapping
TEMPLATES = {
    "tr_formal": TEMPLATE_TR_FORMAL,
    "tr_semiformal": TEMPLATE_TR_SEMIFORMAL,
    "en_formal": TEMPLATE_EN_FORMAL
}


class MessageGenerator:
    """
    Generates personalized messages for alumni outreach.
    """
    
    def __init__(self, template_key: str = "tr_formal"):
        """
        Initialize the message generator.
        
        Args:
            template_key: Key for the template to use
        """
        self.template_key = template_key
        self.base_template = TEMPLATES.get(template_key, TEMPLATE_TR_FORMAL)
        
        # Default placeholders from config
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
        Generates a personalized message for an alumni.
        
        Args:
            alumni: Dictionary containing alumni data
            custom_template: Optional custom template string
            
        Returns:
            Personalized message string
        """
        template = custom_template or self.base_template
        
        # Merge defaults with alumni-specific data
        placeholders = {**self.defaults}
        
        # Add alumni-specific data
        placeholders["name"] = alumni.get("name", "Değerli Mezunumuz")
        placeholders["graduation_year"] = alumni.get("graduation_year", "")
        placeholders["company"] = alumni.get("company", "şirketiniz")
        placeholders["position"] = alumni.get("position", "pozisyonunuz")
        
        # Handle empty values gracefully
        if not placeholders["company"]:
            placeholders["company"] = "mevcut şirketiniz"
        if not placeholders["position"]:
            placeholders["position"] = "mevcut pozisyonunuz"
        if not placeholders["graduation_year"]:
            placeholders["graduation_year"] = "geçmiş"
        
        try:
            message = template.format(**placeholders)
            logger.debug(f"Generated message for: {alumni.get('name', 'Unknown')}")
            return message
            
        except KeyError as e:
            logger.error(f"Missing placeholder in template: {e}")
            raise
    
    def preview(self, alumni: Dict) -> str:
        """
        Generates a preview of the message with formatting.
        
        Args:
            alumni: Dictionary containing alumni data
            
        Returns:
            Formatted preview string
        """
        message = self.generate(alumni)
        
        preview = f"""
{'='*60}
📧 MESSAGE PREVIEW
{'='*60}
To: {alumni.get('name', 'Unknown')} ({alumni.get('linkedin_url', 'No URL')})
{'='*60}

{message}

{'='*60}
"""
        return preview
    
    @staticmethod
    def list_templates() -> Dict[str, str]:
        """
        Returns available templates with descriptions.
        
        Returns:
            Dictionary of template keys and descriptions
        """
        return {
            "tr_formal": "Türkçe - Resmi üslup",
            "tr_semiformal": "Türkçe - Yarı resmi üslup",
            "en_formal": "English - Formal style"
        }


def generate_personalized_message(
    alumni: Dict,
    template_key: str = "tr_formal",
    custom_template: Optional[str] = None
) -> str:
    """
    Convenience function to generate a personalized message.
    
    Args:
        alumni: Alumni data dictionary
        template_key: Template to use
        custom_template: Optional custom template string
        
    Returns:
        Personalized message string
    """
    generator = MessageGenerator(template_key)
    
    if custom_template:
        return generator.generate(alumni, custom_template)
    
    return generator.generate(alumni)


# =============================================================================
# STANDALONE TESTING
# =============================================================================

if __name__ == "__main__":
    print("Testing Message Generator...")
    print("-" * 50)
    
    # Sample alumni data
    test_alumni = {
        "name": "Ahmet Yılmaz",
        "linkedin_url": "https://linkedin.com/in/ahmetyilmaz",
        "graduation_year": "2018",
        "company": "Google",
        "position": "Senior Software Engineer"
    }
    
    generator = MessageGenerator("tr_formal")
    
    print("\nAvailable templates:")
    for key, desc in MessageGenerator.list_templates().items():
        print(f"  - {key}: {desc}")
    
    print(generator.preview(test_alumni))
