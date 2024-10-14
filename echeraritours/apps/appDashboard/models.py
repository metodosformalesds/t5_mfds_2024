from django.db import models
from apps.appUser.models import Agency
from apps.appTour.models import Tour

# Create your models here.


class Reports(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE, related_name='reports')
    tour_title = models.CharField(max_length=200, blank=True)
    total_clients = models.IntegerField(default=0)
    tour_description = models.TextField(max_length=500, blank=True)
    earnings = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ["agency"]

    def save(self, *args, **kwargs):
        if self.agency != self.tour.agency:
            raise ValueError(
                "La agencia no coincide con la agencia del tour seleccionado")

        self.tour_title = self.tour.title
        self.tour_description = self.tour.description
        self.total_clients = self.tour.total_bookings
        self.earnings = self.total_clients * self.tour.price_per_person
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reporte de {self.tour_title}"
