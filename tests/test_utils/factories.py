import factory
from strategy_field.utils import fqn
from test_utils.interfaces import DummySensorInterface, DummyActuatorInterface, DummyControllerInterface
from django.contrib.auth import get_user_model


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


class StaffUserFactory(UserFactory):
    username = factory.Sequence(lambda n: "StaffUser%d" % n)
    email = factory.Sequence(lambda n: "staffuser-%d@example.com" % n)
    is_superuser = False
    is_staff = True



class SensorFactory(factory.django.DjangoModelFactory):
    slug = factory.Sequence(lambda n: 'sensor-%d' % n)
    name = factory.Sequence(lambda n: 'Sensor %d' % n)
    interface = fqn(DummySensorInterface)


    class Meta:
        model = 'rpi_controller.Sensor'
        django_get_or_create = ('slug',)


class ActuatorFactory(factory.django.DjangoModelFactory):
    slug = factory.Sequence(lambda n: 'Actuator-%d' % n)
    name = factory.Sequence(lambda n: 'Actuator %d' % n)
    interface = fqn(DummyActuatorInterface)


    class Meta:
        model = 'rpi_controller.Actuator'
        django_get_or_create = ('slug',)


class ControllerFactory(factory.django.DjangoModelFactory):
    slug = factory.Sequence(lambda n: 'Controller-%d' % n)
    name = factory.Sequence(lambda n: 'Controller %d' % n)
    interface = fqn(DummyControllerInterface)


    class Meta:
        model = 'rpi_controller.Controller'
        django_get_or_create = ('slug',)


class ControlledSensorDetailsFactory(factory.django.DjangoModelFactory):
    sensor = factory.SubFactory(SensorFactory)
    controller = factory.SubFactory(ControllerFactory)

    class Meta:
        model = 'rpi_controller.ControlledSensorDetails'


class ControlledActuatorDetailsFactory(factory.django.DjangoModelFactory):
    actuator = factory.SubFactory(ActuatorFactory)
    controller = factory.SubFactory(ControllerFactory)

    class Meta:
        model = 'rpi_controller.ControlledActuatorDetails'


class ControllerWithSensorAndActuatorFactory(ControllerFactory):
    sensor = factory.RelatedFactory(
        ControlledSensorDetailsFactory,
        factory_related_name='sensors',
    )
    actuator = factory.RelatedFactory(
        ControlledActuatorDetailsFactory,
        factory_related_name='actuators',
    )
