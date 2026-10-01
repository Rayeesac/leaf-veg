import json
from django import forms
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Banner, ContactInfo, SiteContent, Vegetable


class BannerForm(forms.ModelForm):
    """Form for creating and editing homepage banners."""

    class Meta:
        model = Banner
        fields = ['heading', 'subheading', 'tag_label', 'image', 'is_active']
        widgets = {
            'heading': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Fresh Exotic vegetables, pre-ordered by the kilogram',
            }),
            'subheading': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Select your weights, submit a pre-order, and we pack your bulk lot.',
            }),
            'tag_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. WHOLESALE PRE-ORDERS',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VegetableForm(forms.ModelForm):
    """Form for creating and editing vegetable catalog entries."""

    class Meta:
        model = Vegetable
        fields = [
            'title', 'code', 'category', 'image', 'description',
            'is_available', 'details_html',
        ]
        labels = {
            'is_available': 'Show as In Stock on the catalog',
            'description': 'Description',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Bok Choy (Baby)',
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control sku-readonly',
                'readonly': True,
                'placeholder': 'Auto-generated from title',
                'tabindex': '-1',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of this vegetable (optional).',
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'details_html': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5'},
                config_name='vegetable_details',
            ),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        qs = Vegetable.objects.filter(code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A vegetable with this SKU/code already exists.')
        return code


class SiteContentForm(forms.ModelForm):
    """Form for editing a homepage section — label, title, body, and up to 3 pillar/list items."""

    # Pillar rows — icon + label for each of the 3 boxes/bullets
    pillar_0_icon  = forms.CharField(required=False, label='Item 1 — Icon / Emoji',
                                     widget=forms.TextInput(attrs={'class': 'form-control pillar-icon-field', 'maxlength': '10'}))
    pillar_0_label = forms.CharField(required=False, label='Item 1 — Label',
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    pillar_1_icon  = forms.CharField(required=False, label='Item 2 — Icon / Emoji',
                                     widget=forms.TextInput(attrs={'class': 'form-control pillar-icon-field', 'maxlength': '10'}))
    pillar_1_label = forms.CharField(required=False, label='Item 2 — Label',
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    pillar_2_icon  = forms.CharField(required=False, label='Item 3 — Icon / Emoji',
                                     widget=forms.TextInput(attrs={'class': 'form-control pillar-icon-field', 'maxlength': '10'}))
    pillar_2_label = forms.CharField(required=False, label='Item 3 — Label',
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))

    clear_image = forms.BooleanField(
        required=False,
        label='Remove current image (revert to default)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = SiteContent
        fields = ['label', 'title', 'body', 'image']
        widgets = {
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. WHERE WE\'RE HEADED',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Our Vision',
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Main paragraph text for this section.',
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'label': 'Sub-label (small uppercase text above title)',
            'title': 'Section Title',
            'body': 'Body Text',
            'image': 'Section Image',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill pillar fields from existing pillars_json on the instance
        if self.instance and self.instance.pk:
            pillars = self.instance.pillars_json or []
            for i in range(3):
                if i < len(pillars):
                    self.fields[f'pillar_{i}_icon'].initial = pillars[i].get('icon', '')
                    self.fields[f'pillar_{i}_label'].initial = pillars[i].get('label', '')

    def save(self, commit=True):
        obj = super().save(commit=False)
        # Clear image if requested
        if self.cleaned_data.get('clear_image'):
            obj.image = None
        # Pack pillar fields back into pillars_json
        pillars = []
        for i in range(3):
            icon = self.cleaned_data.get(f'pillar_{i}_icon', '').strip()
            label = self.cleaned_data.get(f'pillar_{i}_label', '').strip()
            if icon or label:
                pillars.append({'icon': icon, 'label': label})
        obj.pillars_json = pillars
        if commit:
            obj.save()
        return obj


class ContactInfoForm(forms.ModelForm):
    """Form for editing the Contact Us section."""

    class Meta:
        model = ContactInfo
        fields = [
            'label', 'title', 'intro',
            'location_text',
            'whatsapp_number', 'phone_display', 'phone_hours',
            'email', 'email_meta',
            'store_days', 'store_hours',
            'map_embed_url',
        ]
        widgets = {
            'label':           forms.TextInput(attrs={'class': 'form-control'}),
            'title':           forms.TextInput(attrs={'class': 'form-control'}),
            'intro':           forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location_text':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                     'placeholder': 'One line per address line'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control',
                                                      'placeholder': 'e.g. 919876543210'}),
            'phone_display':   forms.TextInput(attrs={'class': 'form-control',
                                                      'placeholder': 'e.g. +91 98765 43210'}),
            'phone_hours':     forms.TextInput(attrs={'class': 'form-control'}),
            'email':           forms.EmailInput(attrs={'class': 'form-control'}),
            'email_meta':      forms.TextInput(attrs={'class': 'form-control'}),
            'store_days':      forms.TextInput(attrs={'class': 'form-control'}),
            'store_hours':     forms.TextInput(attrs={'class': 'form-control'}),
            'map_embed_url':   forms.URLInput(attrs={'class': 'form-control',
                                                     'placeholder': 'https://www.google.com/maps/embed?...'}),
        }
        labels = {
            'label':           'Sub-label (small uppercase text above title)',
            'title':           'Section Title',
            'intro':           'Intro Paragraph',
            'location_text':   'Location (one address line per line)',
            'whatsapp_number': 'WhatsApp Number (digits only, with country code)',
            'phone_display':   'Phone Display Text',
            'phone_hours':     'Phone / WhatsApp Hours',
            'email':           'Email Address',
            'email_meta':      'Email Note (e.g. "We reply within 24 hours")',
            'store_days':      'Store — Days Open',
            'store_hours':     'Store — Hours',
            'map_embed_url':   'Google Maps Embed URL',
        }
