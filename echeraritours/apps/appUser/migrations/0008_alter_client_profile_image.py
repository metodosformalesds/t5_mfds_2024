# Generated by Django 4.2.16 on 2024-11-06 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appUser', '0007_alter_agency_profile_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images'),
        ),
    ]