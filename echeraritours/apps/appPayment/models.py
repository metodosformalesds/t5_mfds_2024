from django.db import models
from django.core.validators import MinValueValidator
from apps.appUser.models import Client, Agency
from apps.appTour.models import Reservation

# Create your models here.


class PaymentMethod(models.Model):
    """
    Modelo que representa un método de pago en el sistema.
    Atributos:
        PAYMENT_CHOICES (list): Opciones de tipos de métodos de pago disponibles.
        client (ForeignKey): Referencia al cliente asociado con el método de pago.
        agency (ForeignKey): Referencia a la agencia asociada con el método de pago.
        method_type (CharField): Tipo de método de pago (tarjeta de crédito/débito o PayPal).
        stripe_payment_id (CharField): ID de Stripe para la tarjeta de crédito/débito.
        paypal_email (EmailField): Correo electrónico asociado con la cuenta de PayPal.
        created_at (DateTimeField): Fecha y hora en que se creó el método de pago.
    Meta:
        verbose_name (str): Nombre singular del modelo en la interfaz de administración.
        verbose_name_plural (str): Nombre plural del modelo en la interfaz de administración.
        ordering (list): Orden predeterminado de los métodos de pago.
    Métodos:
        save(*args, **kwargs): Guarda el método de pago después de validar los datos.
        validate_client_and_agency(): Valida que el método de pago pertenezca a un cliente o una agencia, pero no a ambos.
        validate_payment_methods(): Valida que solo se ingrese un método de pago (Stripe o PayPal).
        __str__(): Devuelve una representación en cadena del método de pago, incluyendo el tipo y el propietario.
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
        max_length=255, null=True, blank=True)  # ID de Stripe
    paypal_email = models.EmailField(null=True, blank=True)  # Correo de PayPal
    stripe_payment_method_id = models.CharField(max_length=255, blank=True, null=True)
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
        self.validate_client_and_agency()
        self.validate_payment_methods()
        
        # Para tener default un metodo de pago
        if self.is_default:
            if self.client:
                PaymentMethod.objects.filter(client=self.client, is_default=True).update(is_default=False)
            elif self.agency:
                PaymentMethod.objects.filter(agency=self.agency, is_default=True).update(is_default=False)

        # Valida para asegurar que solo uno de stripe_payment_method_id o paypal_email
        if self.method_type == 'credit_card' and not self.stripe_payment_method_id:
            raise ValueError("Se requiere un ID de método de pago de Stripe para la tarjeta de crédito.")
        if self.method_type == 'paypal' and not self.paypal_email:
            raise ValueError("Se requiere un correo electrónico de PayPal para este método de pago.")
        
        super().save(*args, **kwargs)

    def validate_client_and_agency(self):
        if self.client and self.agency:
            raise ValueError(
                "Un método de pago solo puede pertenecer a un cliente o una agencia, no ambos.")
        if not self.client and not self.agency:
            raise ValueError(
                "Debe especificarse un cliente o una agencia para el método de pago.")

    def validate_payment_methods(self):
        if self.stripe_payment_id and self.paypal_email:
            raise ValueError(
                "Solo se puede ingresar un metodo de pago a la vez")
        if not self.stripe_payment_id and not self.paypal_email:
            raise ValueError("Se debe especificar al menos un metodo de pago")
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        owner = self.client.first_name if self.client else (
            self.agency.agency_name if self.agency else "Unknown")
        return f"{self.method_type} - {owner}"


class Payments(models.Model):
    """
    Payments model represents a payment transaction in the Echerari Tours system.
    Attributes:
        STATUS_CHOICES (list): A list of tuples representing the possible statuses of a payment.
        client (ForeignKey): A foreign key to the Client model, representing the client making the payment.
        agency (ForeignKey): A foreign key to the Agency model, representing the agency receiving the payment.
        reservation (ForeignKey): A foreign key to the Reservation model, representing the reservation associated with the payment.
        payment_date (DateTimeField): The date and time when the payment was made, automatically set to the current date and time.
        payment_method (ForeignKey): A foreign key to the PaymentMethod model, representing the method used for the payment.
        amount (FloatField): The amount of money paid, validated to be a non-negative value.
        status (CharField): The status of the payment, with choices defined in STATUS_CHOICES and a default value of 'pendiente'.
    Meta:
        verbose_name (str): The singular name for the model in the admin interface.
        verbose_name_plural (str): The plural name for the model in the admin interface.
        ordering (list): The default ordering for the model, set to order by payment_date.
    Methods:
        save(self, *args, **kwargs): Custom save method to validate the payment details before saving.
        __str__(self): Returns a string representation of the payment, including the client's full name, agency's name, and the amount paid.
    """
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
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True) # Hola soy nuevo

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
        return f"Pago de {self.client.first_name} a {self.agency.agency_name} por {self.amount}"
