# Generated by Django 5.0.3 on 2024-10-20 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appUser', '0002_remove_agency_email_remove_client_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]