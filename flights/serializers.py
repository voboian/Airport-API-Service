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
    class Meta:
        model = Ticket
        fields = ("flight", "row", "seat", "order")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew", "tickets_available")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False)
    airplane = serializers.StringRelatedField(many=False)
    crew = serializers.StringRelatedField(many=True)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "user", "created_at")
