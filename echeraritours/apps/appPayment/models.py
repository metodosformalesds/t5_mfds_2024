from django.db import models
from django.core.validators import MinValueValidator
from apps.appUser.models import Client, Agency
from apps.appTour.models import Reservation

# Create your models here.


class PaymentMethod(models.Model):
    PAYMENT_CHOICES = [
        ('credit_card', 'Tarjeta de Crédito/Débito'),
        ('paypal', 'PayPal'),
    ]

    client = models.ForeignKey(
        Client, null=True, blank=True, on_delete=models.CASCADE, related_name='payment_methods')
    agency = models.ForeignKey(
        Agency, null=True, blank=True, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    stripe_payment_id = models.CharField(
        max_length=255, null=True, blank=True)  # ID de Stripe para la tarjeta
    paypal_email = models.EmailField(null=True, blank=True)  # Correo de PayPal
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Método de pago'
        verbose_name_plural = 'Métodos de pago'
        ordering = ['created_at', 'method_type']

    def save(self, *args, **kwargs):
        if self.client and self.agency:
            raise ValueError(
                "Un método de pago solo puede pertenecer a un cliente o una agencia, no ambos.")
        if not self.client and not self.agency:
            raise ValueError(
                "Debe especificarse un cliente o una agencia para el método de pago.")
        if self.stripe_payment_id and self.paypal_email:
            raise ValueError(
                "Solo se puede ingresar un metodo de pago a la vez")
        if not self.stripe_payment_id and not self.paypal_email:
            raise ValueError("Se debe especificar al menos un metodo de pago")

        super().save(*args, **kwargs)

    def __str__(self):
        owner = self.client.full_name if self.client else self.agency.agency_name
        return f"{self.method_type} - {owner}"


class Payments(models.Model):
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallado', 'Fallado'),
        ('cancelado', 'Cancelado'),
        ('procesando', 'Procesando'),
        ('autorizado', 'Autorizado'),
        ('rechazado', 'Rechazado'),
    ]  # Verificar con las apis

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='payments')
    agency = models.ForeignKey(
        Agency, on_delete=models.CASCADE, related_name='payments')
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.ForeignKey(
        PaymentMethod, max_length=100, on_delete=models.CASCADE)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pendiente')

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['payment_date']

    def save(self, *args, **kwargs):
        if self.amount != self.reservation.tour.price_per_person * self.reservation.number_people:
            raise ValueError(
                "El monto del pago no coincide con el total de la reserva.")

        if self.client != self.payment_method.client:
            raise ValueError("Los clientes no coinciden")

        if self.agency != self.reservation.tour.agency:
            raise ValueError("Las agencias no coinciden")

        if not self.client or not self.agency:
            raise ValueError(
                "El cliente y la agencia deben existir y estar activos.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago de {self.client.full_name} a {self.agency.agency_name} por {self.amount}"
