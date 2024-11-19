# Generated by Django 4.1.7 on 2024-11-18 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appPayment', '0004_payments_card_brand_payments_card_last4_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payments',
            name='card_brand',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='card_last4',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='cardholder_name',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='is_default',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='paypal_email',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='stripe_payment_method_id',
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='card_brand',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='card_last4',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='cardholder_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]