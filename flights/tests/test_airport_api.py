from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from flights.models import Airport
from flights.serializers import AirportSerializer

AIRPORT_URL = reverse("fights:airport-list")


def sample_airport(**params):
    defaults = {
        "name": "Geneva",
        "airport_code": "GVA",
        "closest_big_city": "Geneva"
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def detail_url(airport_id):
    return reverse("airport:airport-detail", args=[airport_id])


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@myproject.com",
            "password",
        )
        self.client.force_authenticate(self.user)

    def test_list_airport(self):
        sample_airport()

        res = self.client.get(AIRPORT_URL)

        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@admin.com", password="1qazxcde3", is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

    def test_airport(self):
        sample_airport()

        res = self.client.get(AIRPORT_URL)

        airport = Airport.objects.all()
        serializer = AirportSerializer(airport, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport(self):
        sample_airport()

        payload = {
            "name": "London Heathrow Airport",
            "airport_code": "LHR",
            "closest_big_city": "London",
        }

        response = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], payload["name"])

    def test_delete_airport_not_allowed(self):
        airport = Airport.objects.create(
            name="Kongo", airport_code="KNG", closest_big_city="Kongo"
        )
        url = detail_url(airport.id)
        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
