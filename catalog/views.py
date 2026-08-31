import json
import logging
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

admin_required = user_passes_test(lambda u: u.is_active and u.is_superuser, login_url='/admin/login/')
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods

from .forms import BannerForm, CartItemData, PreOrderForm, VegetableForm
from .models import Banner, OrderItem, OrderStatus, PreOrder, Vegetable

logger = logging.getLogger('catalog')


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def catalog(request):
    """Main product catalog page with floating order drawer."""
    vegetables = Vegetable.objects.filter(is_available=True).order_by('category', 'title')
    banners = Banner.objects.filter(is_active=True)
    form = PreOrderForm()
    context = {
        'vegetables': vegetables,
        'banners': banners,
        'form': form,
        'page_title': 'Order Wholesale Produce',
    }
    return render(request, 'catalog/catalog.html', context)


# ---------------------------------------------------------------------------
# Pre-order submission
# ---------------------------------------------------------------------------

@require_POST
@transaction.atomic
def submit_order(request):
    """
    Processes the combined buyer-info form + JSON cart payload.
    Creates PreOrder and OrderItem records, then redirects to confirmation.
    """
    form = PreOrderForm(request.POST)

    # --- Parse and validate cart JSON ---
    cart_json = request.POST.get('cart_data', '').strip()
    cart_error = None
    cart_items = []

    try:
        raw_items = json.loads(cart_json) if cart_json else []
        if not isinstance(raw_items, list) or len(raw_items) == 0:
            cart_error = 'Your order is empty. Please select at least one vegetable.'
        else:
            for raw in raw_items:
                item_form = CartItemData(data={
                    'vegetable_id': raw.get('id'),
                    'weight_kg': raw.get('weight_kg'),
                })
                if not item_form.is_valid():
                    cart_error = 'One or more cart items are invalid. Please refresh and try again.'
                    break
                cart_items.append(item_form.cleaned_data)
    except (json.JSONDecodeError, TypeError):
        cart_error = 'Invalid cart data. Please refresh and try again.'

    if cart_error:
        messages.error(request, cart_error)
        vegetables = Vegetable.objects.filter(is_available=True)
        return render(request, 'catalog/catalog.html', {
            'vegetables': vegetables,
            'form': form,
            'cart_error': cart_error,
            'page_title': 'Order Wholesale Produce',
        })

    if not form.is_valid():
        messages.error(request, 'Please correct the errors below before submitting.')
        vegetables = Vegetable.objects.filter(is_available=True)
        return render(request, 'catalog/catalog.html', {
            'vegetables': vegetables,
            'form': form,
            'page_title': 'Order Wholesale Produce',
        })

    # --- Build order ---
    pre_order = form.save()

    vegetable_ids = [item['vegetable_id'] for item in cart_items]
    vegetable_map = {
        v.pk: v for v in Vegetable.objects.filter(pk__in=vegetable_ids, is_available=True)
    }

    for item in cart_items:
        veg = vegetable_map.get(item['vegetable_id'])
        if not veg:
            # Vegetable became unavailable between page load and submission
            continue
        OrderItem.objects.create(
            order=pre_order,
            vegetable=veg,
            weight_kg=item['weight_kg'],
            price_per_kg=veg.price_per_kg,
        )

    pre_order.recalculate_totals()

    if pre_order.items.count() == 0:
        pre_order.delete()
        messages.error(request, 'None of the selected vegetables are currently available.')
        return redirect('catalog:catalog')

    logger.info('New pre-order created: %s for %s', pre_order.order_number, pre_order.buyer_name)
    return redirect('catalog:order_confirmation', order_number=pre_order.order_number)


# ---------------------------------------------------------------------------
# Order confirmation
# ---------------------------------------------------------------------------

def order_confirmation(request, order_number):
    """Order confirmation page shown after successful submission."""
    order = get_object_or_404(PreOrder, order_number=order_number)
    context = {
        'order': order,
        'items': order.items.select_related('vegetable').all(),
        'page_title': f'Order Confirmed — {order.order_number}',
    }
    return render(request, 'catalog/confirmation.html', context)


# ---------------------------------------------------------------------------
# Invoice / print view
# ---------------------------------------------------------------------------

def invoice_print(request, order_number):
    """Printable invoice page (also used for PDF generation via WeasyPrint)."""
    order = get_object_or_404(PreOrder, order_number=order_number)
    context = {
        'order': order,
        'items': order.items.select_related('vegetable').all(),
    }
    return render(request, 'catalog/invoice.html', context)


def invoice_pdf(request, order_number):
    """Generate and stream a PDF invoice using WeasyPrint."""
    from weasyprint import HTML, CSS
    from django.template.loader import render_to_string

    order = get_object_or_404(PreOrder, order_number=order_number)
    context = {
        'order': order,
        'items': order.items.select_related('vegetable').all(),
        'pdf_mode': True,
    }
    html_string = render_to_string('catalog/invoice.html', context, request=request)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="LCV-Invoice-{order.order_number}.pdf"'
    )
    return response


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
    """Delete a vegetable (POST only). Blocked if orders reference it."""
    veg = get_object_or_404(Vegetable, pk=pk)
    try:
        title = veg.title
        veg.delete()
        messages.success(request, f'"{title}" removed from catalog.')
    except Exception:
        messages.error(request, f'Cannot delete "{veg.title}" — it is referenced by existing orders. Mark it as Out of Stock instead.')
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
# Order management (admin/superuser only)
# ---------------------------------------------------------------------------

@admin_required
def order_list(request):
    """Admin page: all orders with summary stats and status filter."""
    from django.db.models import Count, Sum

    status_filter = request.GET.get('status', '')
    orders = PreOrder.objects.order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Summary stats (always across all orders, not filtered)
    stats = PreOrder.objects.aggregate(
        total_orders=Count('pk'),
        total_amount=Sum('total_amount'),
        total_weight=Sum('total_weight_kg'),
    )
    status_counts = {
        s.value: PreOrder.objects.filter(status=s).count()
        for s in OrderStatus
    }

    return render(request, 'catalog/orders/list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'order_statuses': OrderStatus.choices,
        'stats': stats,
        'status_counts': status_counts,
        'page_title': 'Manage Orders',
    })


@admin_required
def order_detail(request, order_number):
    """Admin page: full detail view of a single order with status update."""
    order = get_object_or_404(PreOrder, order_number=order_number)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [s.value for s in OrderStatus]
        if new_status in valid_statuses:
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(request, f'Order {order.order_number} status updated to "{order.get_status_display()}".')
            return redirect('catalog:order_detail', order_number=order.order_number)
        else:
            messages.error(request, 'Invalid status value.')

    items = order.items.select_related('vegetable').all()
    return render(request, 'catalog/orders/detail.html', {
        'order': order,
        'items': items,
        'order_statuses': OrderStatus.choices,
        'page_title': f'Order — {order.order_number}',
    })
