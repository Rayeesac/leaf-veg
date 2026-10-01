from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_sitecontent_fullfields'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, default='Get In Touch', max_length=100, verbose_name='Sub-label')),
                ('title', models.CharField(blank=True, default='Contact Us', max_length=200, verbose_name='Title')),
                ('intro', models.TextField(
                    blank=True,
                    default=(
                        "Whether you're a restaurant, hotel, or home kitchen — we'd love to hear from you. "
                        "Visit us at our store or reach out through WhatsApp and we'll get back to you promptly."
                    ),
                    verbose_name='Intro Text',
                )),
                ('location_text', models.TextField(
                    blank=True,
                    default='Behind Bustand, Smart Trade City\nKottakkal, Malappuram Dt.\nKerala — 676503',
                    verbose_name='Location Text',
                    help_text='Each line will be shown on a separate line.',
                )),
                ('whatsapp_number', models.CharField(
                    blank=True, default='91XXXXXXXXXX', max_length=20,
                    verbose_name='WhatsApp Number',
                    help_text='Country code + number without + (e.g. 919876543210).',
                )),
                ('phone_display', models.CharField(blank=True, default='+91 XXXXX XXXXX', max_length=30, verbose_name='Phone Display Text')),
                ('phone_hours', models.CharField(blank=True, default='Mon – Sat, 6:00 AM – 8:00 PM', max_length=80, verbose_name='Phone Hours')),
                ('email', models.EmailField(blank=True, default='info@leafsvegetables.com', verbose_name='Email Address')),
                ('email_meta', models.CharField(blank=True, default='We reply within 24 hours', max_length=100, verbose_name='Email Note')),
                ('store_days', models.CharField(blank=True, default='All days', max_length=100, verbose_name='Store Days')),
                ('store_hours', models.CharField(blank=True, default='6:00 AM – 1:00 PM', max_length=100, verbose_name='Store Hours')),
                ('map_embed_url', models.URLField(
                    blank=True,
                    default=(
                        'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d979.3!2d76.0032175!3d11.0036981'
                        '!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3ba7b5c26d65796f%3A0xacd7161adf7e19a4'
                        '!2sLEAFS%20CHINESE%20VEGETABLES!5e0!3m2!1sen!2sin!4v1!5m2!1sen!2sin'
                    ),
                    max_length=1000,
                    verbose_name='Google Maps Embed URL',
                    help_text='Paste the src URL from the Google Maps embed iframe.',
                )),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Contact Info',
                'verbose_name_plural': 'Contact Info',
            },
        ),
    ]
