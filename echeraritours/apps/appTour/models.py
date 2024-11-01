from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.appUser.models import Client, Agency

# Create your models here.


class Tour(models.Model):
    title = models.CharField(max_length=100)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    description = models.TextField(max_length=500)
    lodging_place = models.CharField(max_length=30)
    price_per_person = models.DecimalField(
        validators=[MinValueValidator(0)], max_digits=10, decimal_places=2)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    total_bookings = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    place_of_origin = models.CharField(max_length=100, null=True, blank=True)
    destination_place = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = 'Tour'
        verbose_name_plural = 'Tours'
        ordering = ['start_date']

    def __str__(self):
        return self.title


class Reservation(models.Model):
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE, related_name='reservations')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    number_people = models.PositiveIntegerField(
        validators=[MinValueValidator(1)])
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, blank=True, null=True)
    reservation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'
        ordering = ['reservation_date']

    def calculate_total_price(self):
        return self.tour.price_per_person * self.number_people

    def save(self, *args, **kwargs):
        if self.tour.total_bookings + self.number_people > self.tour.capacity:
            raise ValueError(
                "No se puede reservar más personas que la capacidad del tour.")
        self.total_price = self.calculate_total_price
        self.tour.total_bookings += self.number_people
        self.tour.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.tour.total_bookings -= self.number_people
        self.tour.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Reservación de {self.client.first_name} {self.client.paternal_surname} en {self.tour.title}"


class Reviews(models.Model):
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(max_length=500, blank=True)
    review_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['review_date']

    def __str__(self):
        return f"Reseña de {self.reservation.client.first_name} {self.reservation.client.paternal_surname} para {self.reservation.tour.title}"
