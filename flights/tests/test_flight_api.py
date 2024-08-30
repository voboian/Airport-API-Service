import datetime
from datetime import datetime
import pytz
from django.db.models import F, Count
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from flights.models import Flight, Route, Airplane, AirplaneType, Crew, Airport
from flights.serializers import FlightListSerializer, FlightDetailSerializer

FLIGHT_URL = reverse("flights:flight-list")


def detail_url(flight_id: int):
    return reverse("flights:flight-detail", args=[flight_id])


def create_aware_datetime(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    tz = pytz.timezone("Europe/Kiev")
    return tz.localize(dt)


def sample_flight1(**params):
    Airport1 = Airport.objects.create(
        name="Geneva", iata_code="GTR", closest_big_city="Geneva"
    )
    Airport2 = Airport.objects.create(
        name="Washington", iata_code="RTY", closest_big_city="Washington"
    )
    route = Route.objects.create(source=Airport1, destination=Airport2, distance=1900)
    airplane_type = AirplaneType.objects.create(name="Large Jets")
    airplane = Airplane.objects.create(
        name="Boeing 777X", rows=250, seats_in_row=2, airplane_type=airplane_type
    )
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": create_aware_datetime("2024-08-08 10:09:33"),
        "arrival_time": create_aware_datetime("2024-08-08 13:07:09"),
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


def sample_flight2(**params):
    Airport1 = Airport.objects.create(
        name="Bucharest", iata_code="OTP", closest_big_city="Bucharest"
    )
    Airport2 = Airport.objects.create(
        name="Boryspil", iata_code="KVB", closest_big_city="Boryspil"
    )
    route = Route.objects.create(source=Airport1, destination=Airport2, distance=900)
    airplane_type = AirplaneType.objects.create(name="Planes of local airline(16 C)")
    airplane = Airplane.objects.create(
        name="Airbus A380", rows=150, seats_in_row=2, airplane_type=airplane_type
    )
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": create_aware_datetime("2024-08-09 10:09:33"),
        "arrival_time": create_aware_datetime("2024-08-09 16:09:33"),
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


def sample_flight3(**params):
    Airport1 = Airport.objects.create(
        name="Aberdeen", iata_code="ABZ", closest_big_city="Aberdeen"
    )
    Airport2 = Airport.objects.create(
        name="Valencia", iata_code="VLC", closest_big_city="Valencia"
    )
    route = Route.objects.create(source=Airport1, destination=Airport2, distance=500)
    airplane_type = AirplaneType.objects.create(name="Medium Jets")
    airplane = Airplane.objects.create(
        name="McDonnell Douglas DC-10",
        rows=180,
        seats_in_row=2,
        airplane_type=airplane_type,
    )
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": create_aware_datetime("2024-08-10 10:09:33"),
        "arrival_time": create_aware_datetime("2024-08-10 16:09:33"),
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@myproject.com",
            "password",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_flight(self):
        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.all().annotate(
            tickets_available=(F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")))

        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_departure(self):
        flight1 = sample_flight1()
        flight2 = sample_flight2()
        flight3 = sample_flight3()

        res = self.client.get(FLIGHT_URL, {"departure": "2024-08-10"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)
        serializer3 = FlightListSerializer(flight3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_filter_flight_by_arrival(self):
        flight1 = sample_flight1()
        flight2 = sample_flight2()
        flight3 = sample_flight3()

        res = self.client.get(FLIGHT_URL, {"arrival": "2024-08-10"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)
        serializer3 = FlightListSerializer(flight3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_retrieve_flight_detail(self):
        flight1 = sample_flight1()

        url = detail_url(flight1.id)
        response = self.client.get(url)

        serializer = FlightDetailSerializer(flight1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_flight_forbidden(self):
        Airport1 = Airport.objects.create(
            name="Aberdeen", iata_code="ABZ", closest_big_city="Aberdeen"
        )
        Airport2 = Airport.objects.create(
            name="Valencia", iata_code="VLC", closest_big_city="Valencia"
        )
        route = Route.objects.create(
            source=Airport1, destination=Airport2, distance=500
        )
        airplane_type = AirplaneType.objects.create(name="Medium Jets")
        airplane = Airplane.objects.create(
            name="McDonnell Douglas DC-10",
            rows=180,
            seats_in_row=2,
            airplane_type=airplane_type,
        )
        crew_1 = Crew.objects.create(first_name="Crew1", last_name="Member1")
        crew_2 = Crew.objects.create(first_name="Crew2", last_name="Member2")
        payload = {
            "route": route.pk,
            "airplane": airplane.pk,
            "departure_time": "2024-08-08 16:09:33",
            "arrival_time": "2024-08-09 16:09:33",
            "crew": [crew_1.pk, crew_2.pk],
        }

        response = self.client.post(FLIGHT_URL, payload)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@admin.com", password="1qazxcde3", is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_flight(self):
        Airport1 = Airport.objects.create(
            name="Aberdeen", iata_code="ABZ", closest_big_city="Aberdeen"
        )
        Airport2 = Airport.objects.create(
            name="Valencia", iata_code="VLC", closest_big_city="Valencia"
        )
        route = Route.objects.create(
            source=Airport1, destination=Airport2, distance=500
        )
        airplane_type = AirplaneType.objects.create(name="Medium Jets")
        airplane = Airplane.objects.create(
            name="McDonnell Douglas DC-10",
            rows=180,
            seats_in_row=2,
            airplane_type=airplane_type,
        )
        crew_1 = Crew.objects.create(first_name="Crew1", last_name="Member1")
        crew_2 = Crew.objects.create(first_name="Crew2", last_name="Member2")
        payload = {
            "route": route.pk,
            "airplane": airplane.pk,
            "departure_time": "2024-08-08 16:09:33",
            "arrival_time": "2024-08-08 16:09:33",
            "crew": [crew_1.pk, crew_2.pk],
        }
        response = self.client.post(FLIGHT_URL, payload)
        Flight.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key, value in payload.items():
            if key in ("departure_time", "arrival_time"):
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                tz = pytz.timezone("Europe/Kiev")
                value = tz.localize(value)
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            self.assertEqual(response.data[key], value)

    def test_create_flight_with_two_crew_members(self):
        Airport1 = Airport.objects.create(
            name="Aberdeen", iata_code="ABZ", closest_big_city="Aberdeen"
        )
        Airport2 = Airport.objects.create(
            name="Valencia", iata_code="VLC", closest_big_city="Valencia"
        )
        route = Route.objects.create(
            source=Airport1, destination=Airport2, distance=500
        )
        airplane_type = AirplaneType.objects.create(name="Medium Jets")
        airplane = Airplane.objects.create(
            name="McDonnell Douglas DC-10",
            rows=180,
            seats_in_row=2,
            airplane_type=airplane_type,
        )
        crew_1 = Crew.objects.create(first_name="Crew1", last_name="Member1")
        crew_2 = Crew.objects.create(first_name="Crew2", last_name="Member2")

        payload = {
            "route": route.pk,
            "airplane": airplane.pk,
            "departure_time": "2024-08-08 16:09:33",
            "arrival_time": "2024-08-08 16:09:33",
            "crew": [crew_1.pk, crew_2.pk],
        }

        response = self.client.post(FLIGHT_URL, payload)
        flight1 = Flight.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(flight1.crew.count(), 2)

    def test_delete_flight_not_allowed(self):
        flight1 = sample_flight1()
        url = detail_url(flight1.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
