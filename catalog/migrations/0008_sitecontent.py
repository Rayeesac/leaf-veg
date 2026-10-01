from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_alter_details_html_ckeditor5'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(
                    choices=[
                        ('vision', 'Our Vision'),
                        ('mission', 'Our Mission'),
                        ('about', 'About Us'),
                    ],
                    max_length=20,
                    unique=True,
                    verbose_name='Section',
                )),
                ('body', models.TextField(
                    help_text='Main paragraph text displayed in this section.',
                    verbose_name='Body Text',
                )),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Site Content',
                'verbose_name_plural': 'Site Contents',
            },
        ),
    ]
