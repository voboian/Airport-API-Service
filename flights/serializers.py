from django.db import transaction
from rest_framework import serializers

from flights.models import (
    Airport,
    AirplaneType,
    Crew,
    Airplane,
    Route,
    Ticket,
    Flight,
    Order,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city", "iata_code")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity")


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField(many=False)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, data):
        if data["source"] == data["destination"]:
            raise serializers.ValidationError(
                "The city of departure and arrival cannot be the same"
            )
        if data["distance"] < 0:
            raise serializers.ValidationError(
                "The distance cannot be negative"
            )
        return data


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField(many=False)
    destination = serializers.StringRelatedField(many=False)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs) -> dict:
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seats(
            attrs["row"],
            attrs["seat"],
            serializers.ValidationError,
            attrs["flight"],
        )
        return data

    class Meta:
        model = Ticket
        fields = ("flight", "row", "seat",)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightSerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew", "tickets_available")

    def validate(self, data):
        if data["departure_time"] > data["arrival_time"]:
            raise serializers.ValidationError("Departure time must be before arrival time.")
        return data


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False)
    airplane = serializers.StringRelatedField(many=False)
    airplane_num_seats = serializers.IntegerField(
        source="airplane.capacity", read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "tickets_available",
            "airplane_num_seats",
        )


class FlightDetailSerializer(FlightListSerializer):
    crew = serializers.StringRelatedField(many=True)
    taken_places = TicketSeatsSerializer(many=True, read_only=True, source="tickets")

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "taken_places",
            "tickets_available",
            "crew",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets",)

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
