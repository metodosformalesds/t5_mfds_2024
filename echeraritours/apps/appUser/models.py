from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    birth_date = models.DateField()
    zip_code = models.CharField(max_length=10)
    identification = models.ImageField(upload_to='static/identifications/')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-id']

    def __str__(self):
        return self.email


class Agency(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agency_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    zip_code = models.CharField(max_length=10)
    certificate = models.ImageField(upload_to='static/certificates/')

    class Meta:
        verbose_name = 'Agencia'
        verbose_name_plural = 'Agencias'
        ordering = ['-id']

    def __str__(self):
        return f"Agencia: {self.agency_name} - {self.email}"
