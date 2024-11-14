from django.db import models
from django.core.validators import MinValueValidator
from apps.appUser.models import Client, Agency
from apps.appTour.models import Reservation

# Create your models here.


class PaymentMethod(models.Model):
    """
    Modelo que representa un método de pago en el sistema.
    Atributos:
        client (ForeignKey): Referencia al cliente asociado con el método de pago.
        agency (ForeignKey): Referencia a la agencia asociada con el método de pago.
        method_type (CharField): Tipo de método de pago (tarjeta de crédito/débito o PayPal).
        stripe_payment_method_id (CharField): ID de Stripe para la tarjeta de crédito/débito.
        paypal_email (EmailField): Correo electrónico asociado con la cuenta de PayPal.
        is_default (BooleanField): Indica si es el método de pago predeterminado del cliente o agencia.
        created_at (DateTimeField): Fecha y hora en que se creó el método de pago.
    """
    PAYMENT_CHOICES = [
        ('credit_card', 'Tarjeta de Crédito/Débito'),
        ('paypal', 'PayPal'),
    ]

    client = models.ForeignKey(
        Client, null=True, blank=True, on_delete=models.CASCADE, related_name='payment_methods')
    agency = models.ForeignKey(
        Agency, null=True, blank=True, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    stripe_payment_method_id = models.CharField(
        max_length=255, null=True, blank=True)  # Solo para Stripe
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    cardholder_name = models.CharField(max_length=100, blank=True, null=True)
    paypal_email = models.EmailField(null=True, blank=True)  # Solo para PayPal
    is_default = models.BooleanField(default=False)  # Indica si es predeterminado
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Método de pago'
        verbose_name_plural = 'Métodos de pago'
        ordering = ['created_at', 'method_type']

    def save(self, *args, **kwargs):
        # Asegura que solo un método de pago sea el predeterminado
        if self.is_default:
            if self.client:
                PaymentMethod.objects.filter(client=self.client, is_default=True).update(is_default=False)
            elif self.agency:
                PaymentMethod.objects.filter(agency=self.agency, is_default=True).update(is_default=False)

        # Validación para asegurar que solo uno de stripe_payment_method_id o paypal_email esté presente
        if self.method_type == 'credit_card' and not self.stripe_payment_method_id:
            raise ValueError("Se requiere un ID de método de pago de Stripe para la tarjeta de crédito.")
        if self.method_type == 'paypal' and not self.paypal_email:
            raise ValueError("Se requiere un correo electrónico de PayPal para este método de pago.")

        super().save(*args, **kwargs)

    def __str__(self):
        owner = self.client.first_name if self.client else (self.agency.agency_name if self.agency else "Unknown")
        return f"{self.method_type} - {owner} {'(Predeterminado)' if self.is_default else ''}"


class Payments(models.Model):
    """
    Payments model represents a payment transaction in the Echerari Tours system.
    Attributes:
        client (ForeignKey): Referencia al cliente que realiza el pago.
        agency (ForeignKey): Referencia a la agencia que recibe el pago.
        reservation (ForeignKey): Referencia a la reservación asociada con el pago.
        payment_method (ForeignKey): Método de pago utilizado.
        amount (FloatField): Monto pagado.
        status (CharField): Estado del pago.
        payment_intent_id (CharField): ID del intento de pago en Stripe.
    """
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallado', 'Fallado'),
        ('cancelado', 'Cancelado'),
        ('procesando', 'Procesando'),
        ('autorizado', 'Autorizado'),
        ('rechazado', 'Rechazado'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='payments')
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)  # ID para el intento de pago en Stripe

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['payment_date']

    def save(self, *args, **kwargs):
        # Valida que el monto del pago coincida con el total de la reserva
        if self.amount != self.reservation.tour.price_per_person * self.reservation.number_people:
            raise ValueError("El monto del pago no coincide con el total de la reserva.")
        
        # Valida que el cliente y la agencia sean los mismos que en el método de pago
        if self.client != self.payment_method.client:
            raise ValueError("Los clientes no coinciden.")
        if self.agency != self.reservation.tour.agency:
            raise ValueError("Las agencias no coinciden.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago de {self.client.first_name} a {self.agency.agency_name} por {self.amount}"

