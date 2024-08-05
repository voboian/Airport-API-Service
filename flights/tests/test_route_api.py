from django.contrib.auth import get_user_model
from ..models import Airport, Route
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..serializers import RouteListSerializer

ROUTE_URL = reverse("flights:route-list")


def detail_url(route_id: int):
    return reverse("flights:route-detail", args=[route_id])


def sample_route(source, destination, **params):
    defaults = {"source": source, "destination": destination, "distance": 1900}
    defaults.update(params)
    return Route.objects.create(**defaults)


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@myproject.com",
            "password",
        )

        self.airport1 = Airport.objects.create(
            name="Aberdeen", iata_code="ABZ", closest_big_city="Aberdeen"
        )
        self.airport2 = Airport.objects.create(
            name="Valencia", iata_code="VLC", closest_big_city="Valencia"
        )

        self.route1 = Route.objects.create(source=self.airport1, destination=self.airport2, distance=1900)
        self.route2 = Route.objects.create(source=self.airport2, destination=self.airport1, distance=1900)

        self.client.force_authenticate(self.user)

    def test_filter_route_by_source(self):
        """Test filtering routes by source"""

        res = self.client.get(ROUTE_URL, {"source": self.airport1.name})

        serializer1 = RouteListSerializer(self.route1)
        serializer2 = RouteListSerializer(self.route2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_route_by_destination(self):
        """Test filtering routes by destination"""

        res = self.client.get(ROUTE_URL, {"destination": self.airport2.name})

        serializer1 = RouteListSerializer(self.route1)
        serializer2 = RouteListSerializer(self.route2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_create_route_forbidden(self):
        """Test that creating a route is forbidden"""
        res = self.client.post(ROUTE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@admin.com", password="1qazxcde3", is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

        self.airport1 = Airport.objects.create(
            name="Aberdeen", iata_code="ABZ", closest_big_city="Aberdeen"
        )
        self.airport2 = Airport.objects.create(
            name="Valencia", iata_code="VLC", closest_big_city="Valencia"
        )

    def test_create_route(self):
        """Test creating a route"""
        payload = {
            "source": self.airport2.id,
            "destination": self.airport1.id,
            "distance": 1900,
        }

        response = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(route.source, self.airport2)
        self.assertEqual(route.destination, self.airport1)
        self.assertEqual(route.distance, 1900)

    def test_create_route_with_same_source_and_destination(self):
        """Test creating a route with the same source and destination
        raises a ValidationError"""

        payload = {
            "source": self.airport1.id,
            "destination": self.airport1.id,
            "distance": 1900,
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res.data["non_field_errors"][0],
            "The city of departure and arrival cannot be the same",
        )
