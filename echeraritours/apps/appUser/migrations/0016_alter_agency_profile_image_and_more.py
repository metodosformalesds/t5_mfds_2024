# Generated by Django 4.2 on 2024-11-13 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appUser', '0015_alter_agency_profile_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='profile_image',
            field=models.ImageField(blank=True, default='img/default_profile.jpg', null=True, upload_to='static/img/'),
        ),
        migrations.AlterField(
            model_name='client',
            name='profile_image',
            field=models.ImageField(blank=True, default='img/default_profile.jpg', null=True, upload_to='static/img/'),
        ),
    ]
