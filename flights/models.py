from django.core.exceptions import ValidationError
from django.db import models

from django.conf import settings


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")

    def __str__(self):
        return self.name

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="routes_from")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="routes_to")
    distance = models.IntegerField()

    class Meta:
        unique_together = ("source", "destination")

    def __str__(self):
        return f"{self.source.name} to {self.destination.name}"

    def clean(self):
        if self.source == self.destination:
            raise ValidationError(
                "The city of departure and arrival cannot be the same"
            )


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        unique_together = ("route", "airplane", "departure_time", "arrival_time")

    def __str__(self):
        return f"Flight {self.route} on {self.departure_time}"

    @property
    def tickets_available(self):
        return self.airplane.rows * self.airplane.seats_in_row - self.tickets.count()


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return f"{self.user}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_seats(row: int, seat: int, error_to_raise, flight: Flight):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(flight.airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {airplane_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self) -> None:
        Ticket.validate_seats(
            self.row,
            self.seat,
            ValidationError,
            self.flight,
        )

    class Meta:
        unique_together = ("flight", "row", "seat")

    def __str__(self):
        return f"Ticket {self.id} for Flight {self.flight}"
