# Generated by Django 4.2.16 on 2024-11-22 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appUser', '0019_client_identificator'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='cover_photo',
            field=models.ImageField(blank=True, null=True, upload_to='cover_photos/'),
        ),
    ]