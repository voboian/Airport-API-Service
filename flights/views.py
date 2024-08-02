from datetime import datetime

from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination

from .models import Airport, AirplaneType, Airplane, Route, Crew, Flight, Order, Ticket
from .permissions import IsAdminOrIfAuthenticatedReadOnly
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
    FlightDetailSerializer, OrderListSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


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
    ).prefetch_related("crew").annotate(tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )).all()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        departure = self.request.query_params.get("departure")
        arrival = self.request.query_params.get("arrival")
        queryset = self.queryset
        if departure:
            departure = datetime.strptime(departure, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure)

        if arrival:
            arrival = datetime.strptime(arrival, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival)

        if self.action == "list":
            queryset = (
                queryset.select_related("route", "airplane").prefetch_related(
                    "route__source", "route__destination", "crew"
                ).order_by("id"))
        return queryset.distinct()


class OrderPagination(PageNumberPagination):
    page_size = 1
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related(
        "tickets__flight__route__source",
        "tickets__flight__route__destination",
        "tickets__flight__airplane",

    )
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("flight", "order").all()
    serializer_class = TicketSerializer
