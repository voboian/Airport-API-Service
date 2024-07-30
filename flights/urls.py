from django.urls import include, path
from rest_framework import routers

from flights.views import (
    OrderViewSet,
    CrewViewSet,
    FlightViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    RouteViewSet,
)

router = routers.DefaultRouter()

router.register("orders", OrderViewSet)
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("flights", FlightViewSet)
router.register("crews", CrewViewSet)
router.register("route", RouteViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "flights"
