# Generated by Django 4.1.7 on 2024-11-22 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appPayment', '0006_paymentmethod_transfer_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='transfer_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]