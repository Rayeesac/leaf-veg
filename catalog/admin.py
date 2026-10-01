from django.contrib import admin, messages
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import ContactInfo, SiteContent, Vegetable


# ---------------------------------------------------------------------------
# Vegetable Admin
# ---------------------------------------------------------------------------

@admin.register(Vegetable)
class VegetableAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'category', 'is_available', 'availability_badge', 'created_at')
    list_filter = ('category', 'is_available')
    search_fields = ('title', 'code', 'description')
    list_editable = ('is_available',)
    ordering = ('category', 'title')
    readonly_fields = ('created_at', 'image_preview')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['details_html'].widget = CKEditor5Widget(
            attrs={'class': 'django_ckeditor_5'},
            config_name='vegetable_details',
        )
        return form

    fieldsets = (
        ('Product Details', {
            'fields': ('title', 'code', 'category', 'description')
        }),
        ('Availability', {
            'fields': ('is_available',)
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Details (shown on the public detail page)', {
            'fields': ('details_html',),
            'description': 'Use the rich-text editor to describe health benefits, nutrients, vitamins, origin, culinary uses, etc.',
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
# ContactInfo Admin
# ---------------------------------------------------------------------------

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Header', {'fields': ('label', 'title', 'intro')}),
        ('Location', {'fields': ('location_text',)}),
        ('Phone / WhatsApp', {'fields': ('whatsapp_number', 'phone_display', 'phone_hours')}),
        ('Email', {'fields': ('email', 'email_meta')}),
        ('Store Hours', {'fields': ('store_days', 'store_hours')}),
        ('Map', {'fields': ('map_embed_url',)}),
    )

    def has_add_permission(self, request):
        # Only one row allowed
        return not ContactInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# SiteContent Admin
# ---------------------------------------------------------------------------

@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('section', 'updated_at')
    fields = ('section', 'body')


# ---------------------------------------------------------------------------
# Admin site customisation
# ---------------------------------------------------------------------------

admin.site.site_header = 'LEAFS Exotic Vegetables — Admin'
admin.site.site_title  = 'LEAFS Admin'
admin.site.index_title = 'Wholesale Management Panel'
