import factory
from strategy_field.utils import fqn
from test_utils.interfaces import DummySensorInterface


class SensorFactory(factory.django.DjangoModelFactory):
    slug = "dummy"
    name = "Dummy Sensor"
    interface = fqn(DummySensorInterface)


    class Meta:
        model = 'rpi_controller.Sensor'
        django_get_or_create = ('slug',)
