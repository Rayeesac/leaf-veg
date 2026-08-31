"""
Management command: seed_demo_data
Populates the database with sample Chinese vegetables for development/demo.
Usage: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from catalog.models import Vegetable, VegetableCategory


SAMPLE_VEGETABLES = [
    # Leafy Greens
    {'title': 'Bok Choy (Baby)',       'code': 'LCV-001', 'price_per_kg': 4.50,  'category': VegetableCategory.LEAFY_GREENS,     'description': 'Tender baby bok choy, ideal for stir-fries.'},
    {'title': 'Bok Choy (Large)',       'code': 'LCV-002', 'price_per_kg': 3.80,  'category': VegetableCategory.LEAFY_GREENS,     'description': 'Full-size bok choy with crisp white stems.'},
    {'title': 'Gai Lan (Chinese Broccoli)', 'code': 'LCV-003', 'price_per_kg': 5.20, 'category': VegetableCategory.LEAFY_GREENS,  'description': 'Glossy dark leaves with thick stems.'},
    {'title': 'Water Spinach (Kangkong)',   'code': 'LCV-004', 'price_per_kg': 3.50, 'category': VegetableCategory.LEAFY_GREENS,  'description': 'Popular stir-fry green with hollow stems.'},
    {'title': 'Choy Sum',               'code': 'LCV-005', 'price_per_kg': 4.20,  'category': VegetableCategory.LEAFY_GREENS,     'description': 'Sweet-tasting flowering cabbage vegetable.'},
    {'title': 'Amaranth (Red & Green)', 'code': 'LCV-006', 'price_per_kg': 5.00,  'category': VegetableCategory.LEAFY_GREENS,     'description': 'Nutritious leafy green with vivid colour.'},
    # Cabbages
    {'title': 'Wombok (Napa Cabbage)', 'code': 'LCV-010', 'price_per_kg': 2.90,   'category': VegetableCategory.CABBAGES,         'description': 'Light and crunchy, perfect for dumplings or salads.'},
    {'title': 'Round Green Cabbage',   'code': 'LCV-011', 'price_per_kg': 2.50,   'category': VegetableCategory.CABBAGES,         'description': 'Firm, tightly packed heads.'},
    {'title': 'Purple Cabbage',        'code': 'LCV-012', 'price_per_kg': 3.20,   'category': VegetableCategory.CABBAGES,         'description': 'Vibrant colour, great for slaws.'},
    # Herbs
    {'title': 'Garlic Chives',         'code': 'LCV-020', 'price_per_kg': 8.50,   'category': VegetableCategory.HERBS,            'description': 'Flat-leaf chives with a distinct garlic flavour.'},
    {'title': 'Coriander (Bunched)',   'code': 'LCV-021', 'price_per_kg': 10.00,  'category': VegetableCategory.HERBS,            'description': 'Fresh bunched coriander, roots intact.'},
    {'title': 'Spring Onion',          'code': 'LCV-022', 'price_per_kg': 6.00,   'category': VegetableCategory.HERBS,            'description': 'Mild green onion, used in many Chinese dishes.'},
    {'title': 'Lemongrass',            'code': 'LCV-023', 'price_per_kg': 7.50,   'category': VegetableCategory.HERBS,            'description': 'Aromatic stalks for soups and curries.'},
    # Gourds
    {'title': 'Bitter Melon',          'code': 'LCV-030', 'price_per_kg': 5.80,   'category': VegetableCategory.GOURDS,           'description': 'Distinctively bitter and nutritious.'},
    {'title': 'Fuzzy Melon (Hairy Gourd)', 'code': 'LCV-031', 'price_per_kg': 4.00, 'category': VegetableCategory.GOURDS,        'description': 'Mild-flavoured young gourd.'},
    {'title': 'Winter Melon',          'code': 'LCV-032', 'price_per_kg': 2.80,   'category': VegetableCategory.GOURDS,           'description': 'Large round melon used in soups and braises.'},
    # Shoots & Stems
    {'title': 'Bean Sprouts',          'code': 'LCV-040', 'price_per_kg': 3.00,   'category': VegetableCategory.SHOOTS,           'description': 'Crisp mung bean sprouts.'},
    {'title': 'Bamboo Shoots (Fresh)', 'code': 'LCV-041', 'price_per_kg': 9.50,   'category': VegetableCategory.SHOOTS,           'description': 'Fresh young bamboo shoots.'},
    {'title': 'Lotus Root',            'code': 'LCV-042', 'price_per_kg': 6.50,   'category': VegetableCategory.ROOT_VEGETABLES,  'description': 'Crunchy lotus root with decorative holes.'},
    # Root Vegetables
    {'title': 'Daikon (White Radish)', 'code': 'LCV-050', 'price_per_kg': 2.60,   'category': VegetableCategory.ROOT_VEGETABLES,  'description': 'Large white radish, mild and versatile.'},
    {'title': 'Taro Root',             'code': 'LCV-051', 'price_per_kg': 4.80,   'category': VegetableCategory.ROOT_VEGETABLES,  'description': 'Starchy taro for soups and desserts.'},
]


class Command(BaseCommand):
    help = 'Seed the database with sample Chinese vegetable data for development.'

    def handle(self, *args, **options):
        created_count = 0
        for data in SAMPLE_VEGETABLES:
            _, created = Vegetable.objects.get_or_create(
                code=data['code'],
                defaults=data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. {created_count} new vegetable(s) added. '
                f'{len(SAMPLE_VEGETABLES) - created_count} already existed.'
            )
        )
