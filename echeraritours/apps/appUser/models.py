from django.db import models
from django.contrib.auth.models import User
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

    class Meta:
        verbose_name = 'Agencia'
        verbose_name_plural = 'Agencias'
        ordering = ['-id']

    def __str__(self):
        return f"Agencia: {self.agency_name}"
