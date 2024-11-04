from django.db import models
from django.contrib.auth.models import User
import time

#Para la implementación de Stripe
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your models here.


class Client(models.Model):
    """
    Client model represents a client in the Echerari Tours application.
    Attributes:
        user (OneToOneField): A one-to-one relationship with the User model.
        first_name (CharField): The first name of the client (optional).
        maternal_surname (CharField): The maternal surname of the client (optional).
        paternal_surname (CharField): The paternal surname of the client (optional).
        city (CharField): The city where the client resides (optional).
        phone (CharField): The phone number of the client.
        birth_date (DateField): The birth date of the client.
        zip_code (CharField): The zip code of the client's address.
        identification (ImageField): An image of the client's identification document.
        profile_image (ImageField): An image of the client's profile picture.
    Meta:
        verbose_name (str): The singular name for the model in the admin interface.
        verbose_name_plural (str): The plural name for the model in the admin interface.
        ordering (list): The default ordering for the model's QuerySet.
    Methods:
        __str__(): Returns the first name of the client.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    maternal_surname = models.CharField(max_length=30, blank=True, null=True)
    paternal_surname = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15)
    birth_date = models.DateField()
    zip_code = models.CharField(max_length=10)
    identification = models.ImageField(upload_to='static/identifications/')
    profile_image = models.ImageField(
        upload_to='media/profile_images/', blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.stripe_customer_id:
            customer = stripe.Customer.create(
                email=self.user.email,
                name=f"{self.first_name} {self.paternal_surname}",
            )
            self.stripe_customer_id = customer.id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Para eliminar la cuenta de Stripe
        if self.stripe_customer_id:
            try:
                stripe.Customer.delete(self.stripe_customer_id)
                print(f"Cuenta de cliente {self.stripe_customer_id} eliminada de Stripe.")
            except stripe.error.StripeError as e:
                print(f"Error al eliminar la cuenta de Stripe: {e}")
        super().delete(*args, **kwargs)
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-id']

    def __str__(self):
        return self.first_name


class Agency(models.Model):
    """
    Represents an Agency model associated with a user.
    Attributes:
        user (OneToOneField): A one-to-one relationship with the User model. When the user is deleted, the agency is also deleted.
        agency_name (CharField): The name of the agency with a maximum length of 255 characters.
        agency_description (TextField): A brief description of the agency, optional with a maximum length of 255 characters.
        address (CharField): The address of the agency with a maximum length of 255 characters.
        phone (CharField): The phone number of the agency with a maximum length of 15 characters.
        zip_code (CharField): The zip code of the agency with a maximum length of 10 characters.
        certificate (ImageField): An image field to upload the agency's certificate, stored in 'static/certificates/'.
    Meta:
        verbose_name (str): The singular name for the model in the admin interface.
        verbose_name_plural (str): The plural name for the model in the admin interface.
        ordering (list): The default ordering for the model, ordered by descending id.
    Methods:
        __str__(): Returns a string representation of the agency, displaying the agency name.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agency_name = models.CharField(max_length=255)
    agency_description = models.TextField(
        max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    zip_code = models.CharField(max_length=10)
    certificate = models.ImageField(upload_to='static/certificates/')
    profile_image = models.ImageField(
        upload_to='media/agency_profile_images/', blank=True, null=True)
    stripe_agency_id = models.CharField(max_length=255, blank=True, null=True)
    
    def create_stripe_account_for_agency(self):
        try:
            # Crear la cuenta de Stripe para la agencia
            account = stripe.Account.create(
                type="custom",
                country="MX",
                email=self.user.email,
                business_type="individual",
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
                business_profile={
                    "name": self.agency_name,
                    "mcc": "4722",
                    "product_description": self.agency_description or "Servicios de Agencia",
                },
                company={
                    "name": self.agency_name,
                    "address": {
                        "line1": self.address,
                        "postal_code": self.zip_code,  # Código postal de prueba válido
                        "country": "MX",
                    },
                    "phone": self.phone,
                },
                tos_acceptance={
                    "date": int(time.time()),
                    "ip": "127.0.0.1",  # Esto es para el localhost, no se como cambiarlo para cuando ya sea en produccion pipipi
                }
            )

            # Guarda el ID de la cuenta de Stripe
            self.stripe_agency_id = account.id

            # Añadir representante para la agencia con datos de prueba
            stripe.Account.modify(
                self.stripe_agency_id,
                individual={
                    "first_name": "Testing",
                    "last_name": "TestRamirez",
                    "email": "test@outlook.com",
                    # "rfc": "AAA010101AAA",
                    "address": {
                        "line1": "Calle para Testing",
                        "postal_code": self.zip_code,
                        "country": "MX",
                        "city": "Ciudad de prueba",
                        "state": "CDMX",
                    },
                    "dob": {
                        "day": 1,
                        "month": 1,
                        "year": 1990,
                    },
                    "phone": self.phone,
                    "relationship": {
                        "representative": True,
                        "owner": True,
                        "director": True,
                        "executive": True,
                    }
                },
                business_type="individual"
            )

            # Guarda el ID de la cuenta de Stripe
            self.stripe_agency_id = account.id


        except stripe.error.StripeError as e:
            # Manejar errores de Stripe
            print(f"Error al crear la cuenta de Stripe: {e}")
            raise


        stripe.Account.create_external_account(
            self.stripe_agency_id,
            external_account={
                "object": "bank_account",
                "country": "MX",
                "currency": "mxn",
                "account_holder_name": "Testing TestRamirez",
                "account_holder_type": "individual",
                "account_number": "000123456789"  # Número de cuenta para pruebas
            }
        )


    def save(self, *args, **kwargs):
        if not self.stripe_agency_id:
            self.create_stripe_account_for_agency()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Para eliminar la agencia en Stripe
        if self.stripe_agency_id:
            try:
                stripe.Account.delete(self.stripe_agency_id)
                print(f"Cuenta de agencia {self.stripe_agency_id} eliminada de Stripe.")
            except stripe.error.StripeError as e:
                print(f"Error al eliminar la cuenta de Stripe: {e}")
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Agencia'
        verbose_name_plural = 'Agencias'
        ordering = ['-id']

    

    def __str__(self):
        return f"Agencia: {self.agency_name}"

