import factory
from strategy_field.utils import fqn
from test_utils.interfaces import DummySensorInterface
from django.contrib.auth import get_user_model


class SensorFactory(factory.django.DjangoModelFactory):
    slug = factory.Sequence(lambda n: 'sensor-%d' % n)
    name = factory.Sequence(lambda n: 'Sensor %d' % n)
    interface = fqn(DummySensorInterface)


    class Meta:
        model = 'rpi_controller.Sensor'
        django_get_or_create = ('slug',)


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "User%d" % n)
    password = factory.django.Password("password")
    email = factory.Sequence(lambda n: "user-%d@example.com" % n)
    is_active = True

    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)


class SuperUserFactory(UserFactory):
    username = factory.Sequence(lambda n: "SuperUser%d" % n)
    email = factory.Sequence(lambda n: "superuser-%d@example.com" % n)
    is_superuser = True
    is_staff = True
