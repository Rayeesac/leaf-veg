from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_sitecontent'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitecontent',
            name='label',
            field=models.CharField(
                blank=True,
                max_length=100,
                verbose_name='Sub-label',
                help_text="Small uppercase label above the title (e.g. \"WHERE WE'RE HEADED\").",
            ),
        ),
        migrations.AddField(
            model_name='sitecontent',
            name='title',
            field=models.CharField(blank=True, max_length=200, verbose_name='Title',
                                   help_text='Main section heading (e.g. "Our Vision").'),
        ),
        migrations.AddField(
            model_name='sitecontent',
            name='pillars_json',
            field=models.JSONField(blank=True, default=list, verbose_name='Box / List Items',
                                   help_text='JSON array of items, each with "icon" and "label" keys.'),
        ),
        migrations.AlterField(
            model_name='sitecontent',
            name='body',
            field=models.TextField(blank=True, verbose_name='Body Text',
                                   help_text='Main paragraph text displayed in this section.'),
        ),
    ]
