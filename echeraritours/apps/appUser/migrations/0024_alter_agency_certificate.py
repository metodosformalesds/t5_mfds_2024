# Generated by Django 4.2 on 2024-11-22 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appUser', '0023_merge_20241122_0150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='certificate',
            field=models.ImageField(blank=True, null=True, upload_to='static/certificates/'),
        ),
    ]
