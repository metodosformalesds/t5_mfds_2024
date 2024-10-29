# Generated by Django 5.0.3 on 2024-10-27 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appUser', '0003_client_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='certificate_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='agency',
            name='certificate_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='client',
            name='biometric_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='identification_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='agency',
            name='certificate',
            field=models.ImageField(upload_to='media/certificates/'),
        ),
        migrations.AlterField(
            model_name='client',
            name='identification',
            field=models.ImageField(upload_to='media/identifications/'),
        ),
    ]
