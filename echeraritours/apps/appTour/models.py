from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.appUser.models import Client, Agency
import random

# Create your models here.


class Tour(models.Model):
    """
    Modelo que representa un tour ofrecido por una agencia.
        Atributos:
            title (CharField): Título del tour.
            agency (ForeignKey): Agencia que ofrece el tour.
            description (TextField): Descripción del tour.
            lodging_place (CharField): Lugar de alojamiento durante el tour.
            price_per_person (DecimalField): Precio por persona para el tour.
            capacity (IntegerField): Capacidad máxima de personas para el tour.
            total_bookings (PositiveIntegerField): Número total de reservas realizadas para el tour.
            start_date (DateTimeField): Fecha y hora de inicio del tour.
            end_date (DateTimeField): Fecha y hora de finalización del tour.
            place_of_origin (CharField): Lugar de origen del tour (opcional).
            destination_place (CharField): Lugar de destino del tour (opcional).
            image (ImageField): Imagen representativa del tour.
        Meta:
            verbose_name (str): Nombre singular del modelo.
            verbose_name_plural (str): Nombre plural del modelo.
            ordering (list): Ordenamiento predeterminado de los tours por fecha de inicio.
        Métodos:
        __str__(): Retorna el título del tour.
    """
    title = models.CharField(max_length=100)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    description = models.TextField(max_length=500)
    lodging_place = models.CharField(max_length=100)  # Lugar de hospedaje
    price_per_person = models.DecimalField(
        validators=[MinValueValidator(0)], max_digits=10, decimal_places=2)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    total_bookings = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    place_of_origin = models.CharField(max_length=100, null=True, blank=True)
    destination_place = models.CharField(
        max_length=100, null=True, blank=True)  # Ciudad o estado
    tour_image = models.ImageField(
        upload_to='media/tours/', null=True, blank=True)

    class Meta:
        verbose_name = 'Tour'
        verbose_name_plural = 'Tours'
        ordering = ['start_date']

    def __str__(self):
        return self.title


class Reservation(models.Model):
    """
    Modelo que representa una reservación para un tour.
        Atributos:
            tour (ForeignKey): Referencia al tour reservado.
            client (ForeignKey): Referencia al cliente que realiza la reservación.
            number_people (PositiveIntegerField): Número de personas en la reservación.
            total_price (DecimalField): Precio total de la reservación, calculado automáticamente.
            reservation_date (DateTimeField): Fecha y hora en que se realizó la reservación.
        Meta:
            verbose_name (str): Nombre singular del modelo en español.
            verbose_name_plural (str): Nombre plural del modelo en español.
            ordering (list): Ordenamiento por fecha de reservación.
        Métodos:
            calculate_total_price(): Calcula el precio total de la reservación.
            save(*args, **kwargs): Guarda la reservación y actualiza el total de reservas del tour.
            delete(*args, **kwargs): Elimina la reservación y actualiza el total de reservas del tour.
            __str__(): Representación en cadena de la reservación.
    """
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE, related_name='reservations')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    number_people = models.PositiveIntegerField(
        validators=[MinValueValidator(1)])
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, blank=True, null=True, default=0)
    reservation_date = models.DateTimeField(auto_now_add=True)
    folio = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'
        ordering = ['reservation_date']

    def calculate_total_price(self):
        return self.tour.price_per_person * self.number_people

    def generate_random_folio(self):
        self.folio = random.randint(100000, 999999)

    def save(self, *args, **kwargs):
        if self.tour.total_bookings + self.number_people > self.tour.capacity:
            raise ValueError(
                "No se puede reservar más personas que la capacidad del tour."
            )
        self.generate_random_folio()
        self.total_price = self.calculate_total_price()
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
    """
    Modelo que representa una reseña de un tour.
        Atributos:
            reservation (ForeignKey): Referencia a la reserva asociada a la reseña.
            rating (PositiveIntegerField): Calificación del tour, debe estar entre 1 y 5.
            review_text (TextField): Texto de la reseña, opcional y con un máximo de 500 caracteres.
            review_date (DateTimeField): Fecha y hora en que se creó la reseña, se establece automáticamente al crearla.
        Meta:
            verbose_name (str): Nombre singular del modelo en español.
            verbose_name_plural (str): Nombre plural del modelo en español.
            ordering (list): Ordenamiento de las reseñas por fecha de creación.
        Métodos:
            __str__: Devuelve una representación en cadena de la reseña, incluyendo el nombre del cliente y el título del tour.
    """
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

    def get_stars(self):
        return [1 if i <= self.rating else 0 for i in range(1, 6)]

    def __str__(self):
        return f"Reseña de {self.reservation.client.first_name} {self.reservation.client.paternal_surname} para {self.reservation.tour.title}"
