import datetime
import json
from django import forms
from django.core.exceptions import ValidationError
from .models import Banner, PreOrder, Vegetable, VegetableCategory


class PreOrderForm(forms.ModelForm):
    """Buyer information form for a new wholesale pre-order."""

    class Meta:
        model = PreOrder
        fields = [
            'buyer_name',
            'contact_person',
            'phone_number',
            'email',
            'pickup_date',
            'pickup_time_slot',
            'special_instructions',
        ]
        widgets = {
            'buyer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Green Dragon Imports Pty Ltd',
                'autocomplete': 'organization',
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. John Smith',
                'autocomplete': 'name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 0412 345 678',
                'autocomplete': 'tel',
                'type': 'tel',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@yourbusiness.com (optional)',
                'autocomplete': 'email',
            }),
            'pickup_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': (datetime.date.today() + datetime.timedelta(days=1)).isoformat(),
            }),
            'pickup_time_slot': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 6:00 AM – 9:00 AM',
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Packing preferences, delivery notes, allergies, etc.',
            }),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if not phone:
            raise ValidationError('Phone number is required.')
        # Allow digits, spaces, plus, hyphens, parentheses
        import re
        if not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone):
            raise ValidationError('Enter a valid phone number.')
        return phone

    def clean_pickup_date(self):
        pickup_date = self.cleaned_data.get('pickup_date')
        if pickup_date and pickup_date <= datetime.date.today():
            raise ValidationError('Pickup date must be tomorrow or later — same-day orders are not accepted.')
        return pickup_date


class BannerForm(forms.ModelForm):
    """Form for creating and editing homepage banners."""

    class Meta:
        model = Banner
        fields = ['heading', 'subheading', 'tag_label', 'image', 'overlay_opacity', 'order', 'is_active']
        widgets = {
            'heading': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Fresh Chinese vegetables, pre-ordered by the kilogram',
            }),
            'subheading': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Select your weights, submit a pre-order, and we pack your bulk lot.',
            }),
            'tag_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. WHOLESALE PRE-ORDERS',
            }),
            'overlay_opacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 90,
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VegetableForm(forms.ModelForm):
    """Form for creating and editing vegetable catalog entries."""

    class Meta:
        model = Vegetable
        fields = ['title', 'code', 'category', 'price_per_kg', 'image', 'description', 'is_available']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Bok Choy (Baby)',
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. LCV-001',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'price_per_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0.01',
                'step': '0.01',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of this vegetable (optional).',
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        qs = Vegetable.objects.filter(code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A vegetable with this SKU/code already exists.')
        return code

    def clean_price_per_kg(self):
        price = self.cleaned_data.get('price_per_kg')
        if price is not None and price <= 0:
            raise ValidationError('Price must be greater than zero.')
        return price


class CartItemData(forms.Form):
    """
    Used only for server-side validation of the JSON cart payload
    sent from the catalog page on order submission.
    """
    vegetable_id = forms.IntegerField(min_value=1)
    weight_kg = forms.DecimalField(min_value=0.01, max_digits=8, decimal_places=2)
