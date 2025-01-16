from django.urls import path, include
from rest_framework.routers import SimpleRouter

from rpi_controller.api import views


router = SimpleRouter()
router.register(r'sensor', views.SensorViewSet, basename='api-sensor')


urlpatterns = [
    path('', include(router.urls)),
]
