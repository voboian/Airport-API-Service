from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

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
    FlightDetailSerializer,
    OrderListSerializer,
    AirplaneImageSerializer,
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
        if self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneSerializer

    @extend_schema(
        request=AirplaneImageSerializer,
        responses={200: AirplaneImageSerializer},
        description="Upload an image for a specific airplane."
    )
    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination").all()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return RouteListSerializer

        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        source_name = self.request.query_params.get("source")
        destination_name = self.request.query_params.get("destination")

        if source_name:
            queryset = queryset.filter(source__name__icontains=source_name)

        if destination_name:
            queryset = queryset.filter(destination__name__icontains=destination_name)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source",
                type=str,
                description="Filtering by source airport name",
                style="form",
                explode=True,
            ),
            OpenApiParameter(
                name="destination",
                type=str,
                description="Filtering by destination airport name",
                style="form",
                explode=True,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Retrieve a list of routes with optional filtering
        source airport name and destination airport name."""
        return super().list(request, *args, **kwargs)


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
        queryset = self.queryset
        departure = self.request.query_params.get("departure")
        arrival = self.request.query_params.get("arrival")
        source_name = self.request.query_params.get("source")
        destination_name = self.request.query_params.get("destination")

        if departure:
            departure = datetime.strptime(departure, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure)

        if arrival:
            arrival = datetime.strptime(arrival, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival)

        if source_name:
            queryset = queryset.filter(route__source__name__icontains=source_name)

        if destination_name:
            queryset = queryset.filter(route__destination__name__icontains=destination_name)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="departure",
                type=str,
                description="Filtering by departure date (YYYY-MM-DD)",
                style="form",
                explode=True,
            ),
            OpenApiParameter(
                name="arrival",
                type=str,
                description="Filtering by arrival date (YYYY-MM-DD)",
                style="form",
                explode=True,
            ),
            OpenApiParameter(
                name="source",
                type=str,
                description="Filtering by source airport name",
                style="form",
                explode=True,
            ),
            OpenApiParameter(
                name="destination",
                type=str,
                description="Filtering by destination airport name",
                style="form",
                explode=True,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Retrieve a list of flights with optional filtering by departure date,
        arrival date, source airport name, and destination airport name."""
        return super().list(request, *args, **kwargs)


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
