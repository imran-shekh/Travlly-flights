from django.db import models


class FlightOffer(models.Model):
    origin = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    departure_date = models.DateField()
    airline = models.CharField(max_length=10)
    flight_number = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5)
    duration = models.CharField(max_length=50, blank=True, null=True)


    def __str__(self):
        return f"{self.airline} {self.flight_number} - {self.origin} to {self.destination}"
