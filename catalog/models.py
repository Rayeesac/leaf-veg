import datetime
import logging
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    price_per_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Price per kg ($)',
    )
    image = models.ImageField(upload_to='vegetables/', blank=True, null=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=VegetableCategory.choices,
        default=VegetableCategory.OTHER,
    )
    is_available = models.BooleanField(default=True, verbose_name='In Stock')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'title']
        verbose_name = 'Vegetable'
        verbose_name_plural = 'Vegetables'

    def __str__(self):
        return f'{self.title} ({self.code})'


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PACKED = 'packed', 'Packed'
    READY = 'ready', 'Ready for Pickup'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class PreOrder(models.Model):
    """A wholesale pre-order placed by a buyer."""

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    buyer_name = models.CharField(max_length=200, verbose_name='Business / Client Name')
    contact_person = models.CharField(max_length=200, verbose_name='Contact Person')
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    pickup_date = models.DateField(verbose_name='Preferred Pickup / Delivery Date')
    pickup_time_slot = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Preferred Time Slot',
        help_text='e.g. 6:00 AM – 9:00 AM',
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    total_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Total Weight (kg)',
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Total Amount ($)',
    )
    special_instructions = models.TextField(blank=True, verbose_name='Packing / Delivery Notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pre-Order'
        verbose_name_plural = 'Pre-Orders'

    def __str__(self):
        return f'{self.order_number} — {self.buyer_name}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        year = datetime.date.today().year
        # Use a sequential suffix based on today's count + existing total
        count = PreOrder.objects.count() + 1
        return f'LCV-{year}-{count:05d}'

    def recalculate_totals(self):
        """Recompute weight and amount from related items. Call after saving items."""
        from django.db.models import Sum
        agg = self.items.aggregate(
            total_weight=Sum('weight_kg'),
            total_amount=Sum('line_total'),
        )
        self.total_weight_kg = agg['total_weight'] or 0
        self.total_amount = agg['total_amount'] or 0
        self.save(update_fields=['total_weight_kg', 'total_amount'])
        logger.info('Recalculated totals for order %s', self.order_number)


class OrderItem(models.Model):
    """A single vegetable line item within a pre-order."""

    order = models.ForeignKey(PreOrder, on_delete=models.CASCADE, related_name='items')
    vegetable = models.ForeignKey(Vegetable, on_delete=models.PROTECT)
    weight_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Weight (kg)',
    )
    price_per_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Price per kg ($)',
    )
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Line Total ($)',
    )

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.vegetable.title} × {self.weight_kg} kg'

    def save(self, *args, **kwargs):
        self.line_total = self.weight_kg * self.price_per_kg
        super().save(*args, **kwargs)


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
