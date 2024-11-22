from django.db import models
from apps.appUser.models import Agency, Client
from apps.appTour.models import Tour

# Create your models here.


class Reports(models.Model):
    """
    Authors: Hector Ramos, Leonardo Ortega, Neida Franco
    Represents a report for a specific tour and agency.
    Attributes:
        agency (ForeignKey): The agency associated with the report.
        tour (ForeignKey): The tour associated with the report.
        tour_title (CharField): The title of the tour.
        total_clients (IntegerField): The total number of clients for the tour.
        tour_description (TextField): The description of the tour.
        earnings (DecimalField): The total earnings from the tour.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
        ordering (list): The default ordering for the model.
    Methods:
        save(*args, **kwargs): Custom save method to ensure data consistency.
        __str__(): Returns a string representation of the report.
    """
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE, related_name='reports')
    tour_title = models.CharField(max_length=200, blank=True)
    total_clients = models.IntegerField(default=0)
    tour_description = models.TextField(max_length=500, blank=True)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ["agency"]

    def save(self, *args, **kwargs):
        if self.agency.id != self.tour.agency_id:
            raise ValueError(
                "La agencia no coincide con la agencia del tour seleccionado")

        self.tour_title = self.tour.title if self.tour.title is not None else ''
        self.tour_description = self.tour.description if self.tour.description is not None else ''
        self.total_clients = self.tour.total_bookings if self.tour.total_bookings is not None else 0
        self.earnings = self.total_clients * \
            self.tour.price_per_person if self.tour.price_per_person is not None else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reporte de {self.tour_title} para la agencia {self.agency.agency_name}"


class FavoriteList(models.Model):
    """
    Author: Neida Franco
    Represents a list of favorite tours for a specific agency.
    Attributes:
        client (ForeignKey): The client associated with the favorite list.
        tours (ManyToManyField): The tours associated with the favorite list.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
        ordering (list): The default ordering for the model.
    Methods:
        __str__(): Returns a string representation of the favorite list.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    tours = models.ManyToManyField(Tour)

    class Meta:
        verbose_name = 'Lista de Favoritos'
        verbose_name_plural = 'Listas de Favoritos'
        ordering = ["client"]

    def __str__(self):
        return f"Lista de favoritos del cliente {self.client.user}"
