from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_contactinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitecontent',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='sections/',
                verbose_name='Section Image',
                help_text='Upload an image for this section. Replaces the default Unsplash photo.',
            ),
        ),
    ]
