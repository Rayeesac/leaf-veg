import logging
from django.db import models
from django.core.validators import MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field

logger = logging.getLogger('catalog')


class VegetableCategory(models.TextChoices):
    LEAFY_GREENS = 'leafy_greens', 'Leafy Greens'
    CABBAGES = 'cabbages', 'Cabbages'
    HERBS = 'herbs', 'Herbs'
    ROOT_VEGETABLES = 'root_vegetables', 'Root Vegetables'
    GOURDS = 'gourds', 'Gourds & Melons'
    SHOOTS = 'shoots', 'Shoots & Stems'
    OTHER = 'other', 'Other'


class Vegetable(models.Model):
    """A wholesale vegetable product in the catalog."""

    title = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, verbose_name='SKU / Product Code')
    image = models.ImageField(upload_to='vegetables/', blank=True, null=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=VegetableCategory.choices,
        default=VegetableCategory.OTHER,
    )
    is_available = models.BooleanField(default=True, verbose_name='In Stock')
    created_at = models.DateTimeField(auto_now_add=True)

    # ---- Detail / informational fields ----
    health_benefits = models.TextField(
        blank=True,
        verbose_name='Health Benefits',
        help_text='Key health benefits of this vegetable (displayed on the detail page).',
    )
    nutrients = models.TextField(
        blank=True,
        verbose_name='Nutrients & Minerals',
        help_text='Notable nutrients, minerals and dietary fibre content.',
    )
    vitamins = models.TextField(
        blank=True,
        verbose_name='Vitamins',
        help_text='Vitamins present in significant amounts.',
    )
    culinary_uses = models.TextField(
        blank=True,
        verbose_name='Culinary Uses',
        help_text='How this vegetable is typically cooked or used.',
    )
    origin = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Origin / Region',
        help_text='Where this vegetable originates from.',
    )
    details_html = CKEditor5Field(
        blank=True,
        verbose_name='Details (rich text)',
        help_text='Full details entered via the rich-text editor on the manage page.',
        config_name='vegetable_details',
    )

    class Meta:
        ordering = ['category', 'title']
        verbose_name = 'Vegetable'
        verbose_name_plural = 'Vegetables'

    def __str__(self):
        return f'{self.title} ({self.code})'


class Banner(models.Model):
    """A promotional hero banner displayed on the catalog home page."""

    heading = models.CharField(max_length=200, help_text='Large hero heading text.')
    subheading = models.CharField(
        max_length=300,
        blank=True,
        help_text='Smaller descriptive text beneath the heading.',
    )
    tag_label = models.CharField(
        max_length=80,
        blank=True,
        default='WHOLESALE PRE-ORDERS',
        help_text='Small uppercase label above the heading (e.g. "WHOLESALE PRE-ORDERS").',
    )
    image = models.ImageField(
        upload_to='banners/',
        blank=True,
        null=True,
        help_text='Background image for the banner. Recommended size: 1600×600 px.',
    )
    # Overlay darkness 0–90 so text stays readable over any photo
    overlay_opacity = models.PositiveSmallIntegerField(
        default=55,
        validators=[MaxValueValidator(90)],
        help_text='Background overlay darkness 0–90 (default 55).',
    )
    is_active = models.BooleanField(default=True, verbose_name='Active')
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Display order — lower numbers appear first.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'

    def __str__(self):
        return self.heading


class SiteSection(models.TextChoices):
    VISION = 'vision', 'Our Vision'
    MISSION = 'mission', 'Our Mission'
    ABOUT = 'about', 'About Us'


class SiteContent(models.Model):
    """Editable CMS content for static homepage sections (Vision, Mission, About)."""

    section = models.CharField(
        max_length=20,
        choices=SiteSection.choices,
        unique=True,
        verbose_name='Section',
    )
    label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Sub-label',
        help_text='Small uppercase label above the title (e.g. "WHERE WE\'RE HEADED").',
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Title',
        help_text='Main section heading (e.g. "Our Vision").',
    )
    body = models.TextField(
        blank=True,
        verbose_name='Body Text',
        help_text='Main paragraph text displayed in this section.',
    )
    image = models.ImageField(
        upload_to='sections/',
        blank=True,
        null=True,
        verbose_name='Section Image',
        help_text='Upload an image for this section. Replaces the default Unsplash photo.',
    )
    pillars_json = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Box / List Items',
        help_text='JSON array of items, each with "icon" and "label" keys.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Content'
        verbose_name_plural = 'Site Contents'

    def __str__(self):
        return self.get_section_display()


class ContactInfo(models.Model):
    """Singleton model for the Contact Us section on the homepage."""

    # Header
    label = models.CharField(
        max_length=100, blank=True, default='Get In Touch',
        verbose_name='Sub-label',
    )
    title = models.CharField(
        max_length=200, blank=True, default='Contact Us',
        verbose_name='Title',
    )
    intro = models.TextField(
        blank=True,
        default=(
            "Whether you're a restaurant, hotel, or home kitchen — we'd love to hear from you. "
            "Visit us at our store or reach out through WhatsApp and we'll get back to you promptly."
        ),
        verbose_name='Intro Text',
    )

    # Location card
    location_text = models.TextField(
        blank=True,
        default='Behind Bustand, Smart Trade City\nKottakkal, Malappuram Dt.\nKerala — 676503',
        verbose_name='Location Text',
        help_text='Each line will be shown on a separate line.',
    )

    # Phone / WhatsApp card
    whatsapp_number = models.CharField(
        max_length=20, blank=True, default='91XXXXXXXXXX',
        verbose_name='WhatsApp Number',
        help_text='Country code + number without + (e.g. 919876543210).',
    )
    phone_display = models.CharField(
        max_length=30, blank=True, default='+91 XXXXX XXXXX',
        verbose_name='Phone Display Text',
    )
    phone_hours = models.CharField(
        max_length=80, blank=True, default='Mon – Sat, 6:00 AM – 8:00 PM',
        verbose_name='Phone Hours',
    )

    # Email card
    email = models.EmailField(
        blank=True, default='info@leafsvegetables.com',
        verbose_name='Email Address',
    )
    email_meta = models.CharField(
        max_length=100, blank=True, default='We reply within 24 hours',
        verbose_name='Email Note',
    )

    # Store hours card
    store_days = models.CharField(
        max_length=100, blank=True, default='All days',
        verbose_name='Store Days',
    )
    store_hours = models.CharField(
        max_length=100, blank=True, default='6:00 AM – 1:00 PM',
        verbose_name='Store Hours',
    )

    # Map embed URL
    map_embed_url = models.URLField(
        max_length=1000,
        blank=True,
        default=(
            'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d979.3!2d76.0032175!3d11.0036981'
            '!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3ba7b5c26d65796f%3A0xacd7161adf7e19a4'
            '!2sLEAFS%20CHINESE%20VEGETABLES!5e0!3m2!1sen!2sin!4v1!5m2!1sen!2sin'
        ),
        verbose_name='Google Maps Embed URL',
        help_text='Paste the src URL from the Google Maps embed iframe.',
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Info'
        verbose_name_plural = 'Contact Info'

    def __str__(self):
        return 'Contact Info'

    @classmethod
    def get_solo(cls):
        """Return the single ContactInfo row, creating it with defaults if absent."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
