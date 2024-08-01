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
        fields = ("id", "name", "closest_big_city", )


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


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField(many=False)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


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


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew", "tickets_available")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False)
    airplane = serializers.StringRelatedField(many=False)
    crew = serializers.StringRelatedField(many=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

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
