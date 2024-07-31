from rest_framework import viewsets
from .models import Airport, AirplaneType, Airplane, Route, Crew, Flight, Order, Ticket
from .serializers import (
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    RouteSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
    FlightListSerializer,
    RouteListSerializer,
    AirplaneListSerializer,

)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return AirplaneListSerializer

        return AirplaneSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination").all()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return RouteListSerializer

        return RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route__source",
        "route__destination",
        "airplane"
    ).prefetch_related("crew").all()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return FlightListSerializer

        return FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related(
        "tickets__flight__route",
        "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("flight", "order").all()
    serializer_class = TicketSerializer
