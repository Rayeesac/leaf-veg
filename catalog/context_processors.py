from .models import ContactInfo


def footer_contact(request):
    """Inject the ContactInfo singleton into every template as ``footer_contact``."""
    return {'footer_contact': ContactInfo.get_solo()}
