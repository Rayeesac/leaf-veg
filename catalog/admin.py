import logging
from datetime import date

from django.contrib import admin, messages
from django.db.models import Sum
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html

from .models import OrderItem, OrderStatus, PreOrder, Vegetable

logger = logging.getLogger('catalog')


# ---------------------------------------------------------------------------
# Vegetable Admin
# ---------------------------------------------------------------------------

@admin.register(Vegetable)
class VegetableAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'category', 'price_per_kg', 'is_available', 'availability_badge', 'created_at')
    list_filter = ('category', 'is_available')
    search_fields = ('title', 'code', 'description')
    list_editable = ('price_per_kg', 'is_available')
    ordering = ('category', 'title')
    readonly_fields = ('created_at', 'image_preview')

    fieldsets = (
        ('Product Details', {
            'fields': ('title', 'code', 'category', 'description')
        }),
        ('Pricing & Availability', {
            'fields': ('price_per_kg', 'is_available')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Status', boolean=False)
    def availability_badge(self, obj):
        if obj.is_available:
            return format_html('<span style="color:#2E7D32;font-weight:700;">✔ In Stock</span>')
        return format_html('<span style="color:#D32F2F;font-weight:700;">✘ Out of Stock</span>')

    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:6px;" />',
                obj.image.url
            )
        return '—'

    actions = ['mark_in_stock', 'mark_out_of_stock']

    @admin.action(description='Mark selected vegetables as In Stock')
    def mark_in_stock(self, request, queryset):
        count = queryset.update(is_available=True)
        self.message_user(request, f'{count} vegetable(s) marked as In Stock.', messages.SUCCESS)

    @admin.action(description='Mark selected vegetables as Out of Stock')
    def mark_out_of_stock(self, request, queryset):
        count = queryset.update(is_available=False)
        self.message_user(request, f'{count} vegetable(s) marked as Out of Stock.', messages.WARNING)


# ---------------------------------------------------------------------------
# Inline: Order Items in PreOrder
# ---------------------------------------------------------------------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('vegetable', 'weight_kg', 'price_per_kg', 'line_total')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# PreOrder Admin
# ---------------------------------------------------------------------------

@admin.register(PreOrder)
class PreOrderAdmin(admin.ModelAdmin):
    change_list_template = 'admin/catalog/preorder_change_list.html'

    list_display = (
        'order_number', 'buyer_name', 'contact_person', 'phone_number',
        'pickup_date', 'total_weight_kg', 'total_amount', 'status_badge', 'created_at'
    )
    list_filter = ('status', 'pickup_date')
    search_fields = ('order_number', 'buyer_name', 'contact_person', 'phone_number')
    ordering = ('-created_at',)
    date_hierarchy = 'pickup_date'
    readonly_fields = (
        'order_number', 'total_weight_kg', 'total_amount',
        'created_at', 'invoice_link'
    )
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Reference', {
            'fields': ('order_number', 'status', 'invoice_link')
        }),
        ('Buyer Information', {
            'fields': ('buyer_name', 'contact_person', 'phone_number', 'email')
        }),
        ('Pickup Details', {
            'fields': ('pickup_date', 'pickup_time_slot', 'special_instructions')
        }),
        ('Totals', {
            'fields': ('total_weight_kg', 'total_amount'),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        colours = {
            OrderStatus.PENDING:   ('#F57F17', '#FFF9C4'),
            OrderStatus.PACKED:    ('#1565C0', '#E3F2FD'),
            OrderStatus.READY:     ('#6A1B9A', '#F3E5F5'),
            OrderStatus.COMPLETED: ('#2E7D32', '#E8F5E9'),
            OrderStatus.CANCELLED: ('#D32F2F', '#FFEBEE'),
        }
        fg, bg = colours.get(obj.status, ('#333', '#EEE'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:12px;'
            'font-size:12px;font-weight:600;">{}</span>',
            bg, fg, obj.get_status_display()
        )

    @admin.display(description='Invoice')
    def invoice_link(self, obj):
        if obj.pk:
            from django.urls import reverse
            url = reverse('catalog:invoice_print', kwargs={'order_number': obj.order_number})
            return format_html('<a href="{}" target="_blank">🖨 View Invoice</a>', url)
        return '—'

    actions = ['mark_packed', 'mark_ready', 'mark_completed', 'mark_cancelled']

    @admin.action(description='Mark selected orders as Packed')
    def mark_packed(self, request, queryset):
        count = queryset.update(status=OrderStatus.PACKED)
        self.message_user(request, f'{count} order(s) marked as Packed.', messages.SUCCESS)

    @admin.action(description='Mark selected orders as Ready for Pickup')
    def mark_ready(self, request, queryset):
        count = queryset.update(status=OrderStatus.READY)
        self.message_user(request, f'{count} order(s) marked as Ready for Pickup.', messages.SUCCESS)

    @admin.action(description='Mark selected orders as Completed')
    def mark_completed(self, request, queryset):
        count = queryset.update(status=OrderStatus.COMPLETED)
        self.message_user(request, f'{count} order(s) marked as Completed.', messages.SUCCESS)

    @admin.action(description='Mark selected orders as Cancelled')
    def mark_cancelled(self, request, queryset):
        count = queryset.update(status=OrderStatus.CANCELLED)
        self.message_user(request, f'{count} order(s) marked as Cancelled.', messages.WARNING)

    # Custom URL for Pack-Up Batch Report
    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path('packup-report/', self.admin_site.admin_view(self.packup_report_view), name='packup_report'),
        ]
        return extra + urls

    def packup_report_view(self, request):
        """Aggregate pack-up report: total kg needed per vegetable for a given pickup date."""
        selected_date = request.GET.get('date') or date.today().isoformat()
        try:
            report_date = date.fromisoformat(selected_date)
        except ValueError:
            report_date = date.today()

        # All non-cancelled orders for the date
        active_statuses = [OrderStatus.PENDING, OrderStatus.PACKED, OrderStatus.READY]
        orders_on_date = PreOrder.objects.filter(
            pickup_date=report_date,
            status__in=active_statuses,
        )

        # Aggregate kg per vegetable
        line_items = (
            OrderItem.objects
            .filter(order__in=orders_on_date)
            .values('vegetable__title', 'vegetable__code', 'vegetable__category')
            .annotate(total_kg=Sum('weight_kg'))
            .order_by('vegetable__category', 'vegetable__title')
        )

        context = {
            'report_date': report_date,
            'line_items': line_items,
            'orders': orders_on_date,
            'order_count': orders_on_date.count(),
            'grand_total_kg': sum(item['total_kg'] for item in line_items),
            **self.admin_site.each_context(request),
            'title': f'Pack-Up Batch Report — {report_date.strftime("%d %B %Y")}',
            'opts': PreOrder._meta,
        }
        return render(request, 'admin/catalog/packup_report.html', context)


# ---------------------------------------------------------------------------
# Admin site customisation
# ---------------------------------------------------------------------------

admin.site.site_header = 'LEAFS Chinese Vegetables — Admin'
admin.site.site_title  = 'LEAFS Admin'
admin.site.index_title = 'Wholesale Management Panel'
