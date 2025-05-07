from django.urls import path, include
from rest_framework.routers import SimpleRouter

from rpi_controller.api import views


router = SimpleRouter()
router.register(r'sensor', views.SensorViewSet, basename='api-sensor')
router.register(r'actuator', views.ActuatorViewSet, basename='api-actuator')
router.register(r'controller', views.ControllerViewSet, basename='api-controller')


urlpatterns = [
    path('', include(router.urls)),
]
