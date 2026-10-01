import logging

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

admin_required = user_passes_test(lambda u: u.is_active and u.is_superuser, login_url='/login/')
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BannerForm, ContactInfoForm, SiteContentForm, VegetableForm
from .models import Banner, ContactInfo, SiteContent, SiteSection, Vegetable

logger = logging.getLogger('catalog')


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

# Hardcoded defaults for each section — used when no DB record exists yet.
_SECTION_DEFAULTS = {
    SiteSection.VISION: {
        'label': "Where We're Headed",
        'title': 'Our Vision',
        'body': (
            'To be the most trusted name in exotic vegetable supply across Kerala — a brand synonymous'
            ' with freshness, reliability, and variety. We envision a future where every kitchen,'
            ' from home cooks to five-star chefs, has easy access to the finest produce harvested at'
            ' peak nutrition and flavour.'
        ),
        'pillars': [
            {'icon': '🌿', 'label': 'Freshness'},
            {'icon': '🤝', 'label': 'Reliability'},
            {'icon': '🥬', 'label': 'Variety'},
        ],
    },
    SiteSection.MISSION: {
        'label': 'What Drives Us',
        'title': 'Our Mission',
        'body': (
            'To deliver fresh, responsibly sourced exotic vegetables with consistency and care.'
            ' We are committed to supporting local farmers, minimising waste through smart supply chains,'
            ' and ensuring every customer — wholesale or retail — receives produce they can trust,'
            ' at the quality their tables deserve.'
        ),
        'pillars': [
            {'icon': '', 'label': 'Supporting local farming communities'},
            {'icon': '', 'label': 'Minimal-waste supply chain'},
            {'icon': '', 'label': 'Quality you can count on, every time'},
        ],
    },
    SiteSection.ABOUT: {
        'label': 'Who We Are',
        'title': 'About Us',
        'body': (
            'LEAFS Exotic Vegetables is a wholesale and retail supplier of premium Chinese and exotic'
            ' produce, based in Kottakkal, Kerala. Founded on a passion for quality greens, we source'
            ' directly from trusted farms to bring the freshest vegetables — from baby bok choy to'
            ' lotus root — to restaurants, hotels, and households across the region.'
        ),
        'pillars': [
            {'icon': '', 'label': 'Wholesale & retail supply'},
            {'icon': '', 'label': 'Sourced from trusted local farms'},
            {'icon': '', 'label': '20+ exotic vegetable varieties'},
        ],
    },
}


def _get_section_content():
    """Return a dict keyed by section value with all display fields, merged from DB + defaults."""
    content = {}
    for key, defaults in _SECTION_DEFAULTS.items():
        try:
            obj = SiteContent.objects.get(section=key)
            content[key.value] = {
                'label':   obj.label   or defaults['label'],
                'title':   obj.title   or defaults['title'],
                'body':    obj.body    or defaults['body'],
                'pillars': obj.pillars_json if obj.pillars_json else defaults['pillars'],
                'image':   obj.image if obj.image else None,
            }
        except SiteContent.DoesNotExist:
            entry = dict(defaults)
            entry['image'] = None
            content[key.value] = entry
    return content


def catalog(request):
    """Main product catalog page."""
    vegetables = Vegetable.objects.filter(is_available=True).order_by('category', 'title')
    banners = Banner.objects.filter(is_active=True)
    # Up to 4 vegetables that have images, for the About Us collage
    about_images = list(
        Vegetable.objects.filter(is_available=True).exclude(image='').order_by('category', 'title')[:4]
    )
    context = {
        'vegetables': vegetables,
        'banners': banners,
        'about_images': about_images,
        'page_title': 'Produce Catalog',
        'site_content': _get_section_content(),
        'contact': ContactInfo.get_solo(),
    }
    return render(request, 'catalog/catalog.html', context)


def vegetable_detail(request, pk):
    """Public detail page for a single vegetable."""
    veg = get_object_or_404(Vegetable, pk=pk)
    # Suggest up to 4 related vegetables from the same category (exclude self)
    related = list(
        Vegetable.objects.filter(is_available=True, category=veg.category)
        .exclude(pk=veg.pk)
        .order_by('title')[:4]
    )
    return render(request, 'catalog/vegetables/detail.html', {
        'veg': veg,
        'related': related,
        'page_title': veg.title,
    })


# ---------------------------------------------------------------------------
# Banner management (admin/superuser only)
# ---------------------------------------------------------------------------

@admin_required
def banner_list(request):
    """Staff page listing all banners with edit/delete/add actions."""
    banners = Banner.objects.all()
    return render(request, 'catalog/banners/list.html', {
        'banners': banners,
        'page_title': 'Manage Banners',
    })


@admin_required
def banner_create(request):
    """Create a new banner."""
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save()
            messages.success(request, f'Banner "{banner.heading}" created successfully.')
            return redirect('catalog:banner_list')
    else:
        form = BannerForm()
    return render(request, 'catalog/banners/form.html', {
        'form': form,
        'page_title': 'Add New Banner',
        'action_label': 'Create Banner',
    })


@admin_required
def banner_edit(request, pk):
    """Edit an existing banner."""
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, f'Banner "{banner.heading}" updated.')
            return redirect('catalog:banner_list')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'catalog/banners/form.html', {
        'form': form,
        'banner': banner,
        'page_title': f'Edit Banner — {banner.heading}',
        'action_label': 'Save Changes',
    })


@admin_required
@require_POST
def banner_delete(request, pk):
    """Delete a banner (POST only)."""
    banner = get_object_or_404(Banner, pk=pk)
    heading = banner.heading
    banner.delete()
    messages.success(request, f'Banner "{heading}" deleted.')
    return redirect('catalog:banner_list')


@admin_required
@require_POST
def banner_toggle(request, pk):
    """Toggle a banner's active state via POST."""
    banner = get_object_or_404(Banner, pk=pk)
    banner.is_active = not banner.is_active
    banner.save(update_fields=['is_active'])
    state = 'activated' if banner.is_active else 'deactivated'
    messages.success(request, f'Banner "{banner.heading}" {state}.')
    return redirect('catalog:banner_list')


# ---------------------------------------------------------------------------
# Vegetable management (admin/superuser only)
# ---------------------------------------------------------------------------

@admin_required
def vegetable_list(request):
    """Staff page listing all vegetables with edit/delete/add actions."""
    vegetables = Vegetable.objects.order_by('category', 'title')
    return render(request, 'catalog/vegetables/list.html', {
        'vegetables': vegetables,
        'page_title': 'Manage Vegetables',
    })


@admin_required
def vegetable_create(request):
    """Create a new vegetable."""
    if request.method == 'POST':
        form = VegetableForm(request.POST, request.FILES)
        if form.is_valid():
            veg = form.save()
            messages.success(request, f'Vegetable "{veg.title}" ({veg.code}) added to catalog.')
            return redirect('catalog:vegetable_list')
    else:
        form = VegetableForm()
    return render(request, 'catalog/vegetables/form.html', {
        'form': form,
        'page_title': 'Add New Vegetable',
        'action_label': 'Add Vegetable',
    })


@admin_required
def vegetable_edit(request, pk):
    """Edit an existing vegetable."""
    veg = get_object_or_404(Vegetable, pk=pk)
    if request.method == 'POST':
        form = VegetableForm(request.POST, request.FILES, instance=veg)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vegetable "{veg.title}" updated.')
            return redirect('catalog:vegetable_list')
    else:
        form = VegetableForm(instance=veg)
    return render(request, 'catalog/vegetables/form.html', {
        'form': form,
        'veg': veg,
        'page_title': f'Edit — {veg.title}',
        'action_label': 'Save Changes',
    })


@admin_required
@require_POST
def vegetable_delete(request, pk):
    """Delete a vegetable (POST only)."""
    veg = get_object_or_404(Vegetable, pk=pk)
    try:
        title = veg.title
        veg.delete()
        messages.success(request, f'"{title}" removed from catalog.')
    except Exception:
        messages.error(request, f'Cannot delete "{veg.title}" — it may be referenced by existing data. Mark it as Out of Stock instead.')
    return redirect('catalog:vegetable_list')


@admin_required
@require_POST
def vegetable_toggle(request, pk):
    """Toggle in-stock / out-of-stock status."""
    veg = get_object_or_404(Vegetable, pk=pk)
    veg.is_available = not veg.is_available
    veg.save(update_fields=['is_available'])
    state = 'marked In Stock' if veg.is_available else 'marked Out of Stock'
    messages.success(request, f'"{veg.title}" {state}.')
    return redirect('catalog:vegetable_list')




# ---------------------------------------------------------------------------
# Site content editing (logged-in users only)
# ---------------------------------------------------------------------------

@admin_required
def section_edit(request, section):
    """Edit a homepage section — label, title, body, pillars."""
    from django.http import Http404
    valid_sections = [s.value for s in SiteSection]
    if section not in valid_sections:
        raise Http404

    # Get or create with defaults pre-populated
    defaults_data = _SECTION_DEFAULTS.get(SiteSection(section), {})
    obj, created = SiteContent.objects.get_or_create(
        section=section,
        defaults={
            'label': defaults_data.get('label', ''),
            'title': defaults_data.get('title', ''),
            'body':  defaults_data.get('body', ''),
            'pillars_json': defaults_data.get('pillars', []),
        },
    )
    section_label = obj.get_section_display()

    if request.method == 'POST':
        form = SiteContentForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{section_label}" updated successfully.')
            return redirect('catalog:catalog')
    else:
        form = SiteContentForm(instance=obj)

    return render(request, 'catalog/section_edit.html', {
        'form': form,
        'section': section,
        'section_label': section_label,
        'page_title': f'Edit — {section_label}',
    })


@admin_required
def contact_edit(request):
    """Edit the Contact Us section."""
    obj = ContactInfo.get_solo()
    if request.method == 'POST':
        form = ContactInfoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact info updated successfully.')
            return redirect('catalog:catalog')
    else:
        form = ContactInfoForm(instance=obj)
    return render(request, 'catalog/contact_edit.html', {
        'form': form,
        'page_title': 'Edit — Contact Us',
    })
