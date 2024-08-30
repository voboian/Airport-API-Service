from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from flights.models import AirplaneType
from flights.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("flights:airplanetype-list")


def sample_airplane_type(**params):
    defaults = {
        "name": "Large Jets",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def detail_url(airplane_type_id):
    return reverse("flights:airplanetype-detail", args=[airplane_type_id])


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@myproject.com",
            "password",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_airplane_type(self):
        sample_airplane_type()

        res = self.client.get(AIRPLANE_TYPE_URL)

        airport_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airport_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@admin.com", password="1qazxcde3", is_staff=True
        )
        self.client.force_authenticate(self.admin_user)
        AirplaneType.objects.all().delete()

    def test_airplane_type_list(self):

        res = self.client.get(AIRPLANE_TYPE_URL)

        airplane_type = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_type, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_type(self):

        payload = {"name": "Large Jets"}
        response = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], payload["name"])

    def test_delete_airplane_type_not_allowed(self):
        airplane_type = AirplaneType.objects.create(name="Private Jets")

        url = detail_url(airplane_type.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
