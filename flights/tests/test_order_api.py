from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from flights.models import Airport, Order, Route, AirplaneType, Airplane, Ticket, Flight
from flights.serializers import OrderListSerializer

ORDER_URL = reverse("airport:order-list")


def detail_url(order_id: int):
    return reverse("airport:order-detail", args=[order_id])


def sample_order1(user, **params):
    Airport1 = Airport.objects.create(
        name="Aberdeen", airport_code="ABZ", closest_big_city="Aberdeen"
    )
    Airport2 = Airport.objects.create(
        name="Valencia", airport_code="VLC", closest_big_city="Valencia"
    )
    route = Route.objects.create(source=Airport1, destination=Airport2, distance=500)
    airplane_type = AirplaneType.objects.create(name="Medium Jets")
    airplane = Airplane.objects.create(
        name="McDonnell Douglas DC-10",
        rows=250,
        seats_in_row=2,
        airplane_type=airplane_type,
    )
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=datetime.strptime("2023-12-15 13:07:09", "%Y-%m-%d %H:%M:%S"),
        arrival_time=datetime.strptime("2023-12-15 16:00:00", "%Y-%m-%d %H:%M:%S"),
    )

    defaults = {"user": user}

    defaults.update(params)
    order = Order.objects.create(**defaults)
    tickets = [
        Ticket.objects.create(order=order, flight=flight, row=4, seat=1),
        Ticket.objects.create(order=order, flight=flight, row=4, seat=2),
    ]

    return order, tickets


def sample_order2(user, **params):
    Airport1 = Airport.objects.create(
        name="Airport1", airport_code="ASS", closest_big_city="Airport1"
    )
    Airport2 = Airport.objects.create(
        name="Airport2", airport_code="VDR", closest_big_city="Airport2"
    )
    route = Route.objects.create(source=Airport1, destination=Airport2, distance=500)
    airplane_type = AirplaneType.objects.create(name="Medium Jets")
    airplane = Airplane.objects.create(
        name="McDonnell Douglas DC-10",
        rows=250,
        seats_in_row=2,
        airplane_type=airplane_type,
    )
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=datetime.strptime("2023-12-15 13:07:09", "%Y-%m-%d %H:%M:%S"),
        arrival_time=datetime.strptime("2023-12-15 16:00:00", "%Y-%m-%d %H:%M:%S"),
    )

    defaults = {"user": user}

    defaults.update(params)
    order = Order.objects.create(**defaults)

    return Ticket.objects.create(order=order, flight=flight, row=5, seat=1)


def sample_order3(user, **params):
    Airport3 = Airport.objects.create(
        name="Airport3", airport_code="AUY", closest_big_city="Airport3"
    )
    Airport4 = Airport.objects.create(
        name="Airport4", airport_code="CCC", closest_big_city="Airport4"
    )
    route = Route.objects.create(source=Airport3, destination=Airport4, distance=500)
    airplane_type = AirplaneType.objects.create(name="Medium Jets")
    airplane = Airplane.objects.create(
        name="McDonnell Douglas DC-10",
        rows=250,
        seats_in_row=2,
        airplane_type=airplane_type,
    )
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=datetime.strptime("2023-12-15 13:07:09", "%Y-%m-%d %H:%M:%S"),
        arrival_time=datetime.strptime("2023-12-15 16:00:00", "%Y-%m-%d %H:%M:%S"),
    )

    defaults = {"user": user}

    defaults.update(params)
    order = Order.objects.create(**defaults)

    return Ticket.objects.create(order=order, flight=flight, row=6, seat=1)


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for retrieving orders"""
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@myproject.com",
            "password",
        )
        self.client.force_authenticate(self.user)

        Airport3 = Airport.objects.create(
            name="Airport3", airport_code="AUY", closest_big_city="Airport3"
        )
        Airport4 = Airport.objects.create(
            name="Airport4", airport_code="CCC", closest_big_city="Airport4"
        )
        self.route = Route.objects.create(
            source=Airport3, destination=Airport4, distance=500
        )
        self.airplane_type = AirplaneType.objects.create(name="Medium Jets")
        self.airplane = Airplane.objects.create(
            name="McDonnell Douglas DC-10",
            rows=250,
            seats_in_row=2,
            airplane_type=self.airplane_type,
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime.strptime(
                "2023-12-15 13:07:09", "%Y-%m-%d %H:%M:%S"
            ),
            arrival_time=datetime.strptime("2023-12-15 16:00:00", "%Y-%m-%d %H:%M:%S"),
        )

    def test_list_order(self):
        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=self.user)

        Ticket.objects.create(order=order1, flight=self.flight, row=3, seat=1)
        Ticket.objects.create(order=order1, flight=self.flight, row=4, seat=2)
        Ticket.objects.create(order=order2, flight=self.flight, row=5, seat=1)
        Ticket.objects.create(order=order2, flight=self.flight, row=6, seat=2)

        res = self.client.get(ORDER_URL)

        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_order(self):
        """Test creating a new order"""

        payload = {
            "tickets": [
                {"flight": self.flight.id, "row": 3, "seat": 1},
                {"flight": self.flight.id, "row": 4, "seat": 2},
            ]
        }

        res = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data["id"])
        self.assertEqual(order.user, self.user)

    def test_retrieve_orders(self):
        """Test retrieving orders"""

        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=self.user)

        Ticket.objects.create(order=order1, flight=self.flight, row=4, seat=1)
        Ticket.objects.create(order=order2, flight=self.flight, row=4, seat=2)

        res = self.client.get(ORDER_URL)

        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_orders_limited_to_user(self):
        """Test that orders returned are for the authenticated user"""

        user2 = get_user_model().objects.create_user(
            "other@myproject.com",
            "testpass",
        )
        Order.objects.create(user=user2)
        order = Order.objects.create(user=self.user)

        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], order.id)

    def test_create_order_with_invalid_tickets(self):
        """Test ticket validation"""

        payload = {
            "tickets": [
                {"flight": self.flight.id, "row": 251, "seat": 1},
                {"flight": self.flight.id, "row": 0, "seat": 2},
                {"flight": self.flight.id, "row": 249, "seat": 3},
                {"flight": self.flight.id, "row": 250, "seat": 0},
            ]
        }

        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_duplicate_tickets(self):
        """Test creating a new order with duplicate tickets"""

        order = Order.objects.create(user=self.user)
        Ticket.objects.create(order=order, flight=self.flight, row=1, seat=1)

        payload = {"tickets": [{"flight": self.flight.id, "row": 1, "seat": 1}]}
        res = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
