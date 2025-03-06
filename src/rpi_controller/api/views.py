import typing
from rest_framework import viewsets, serializers, decorators, status
from rest_framework.response import Response

from rpi_controller.models import Sensor, Actuator


if typing.TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.response import Response


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    interface = serializers.SerializerMethodField()
    last_update_status = serializers.SerializerMethodField()
    last_status_update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def get_interface(self, obj: Sensor) -> str:
        return obj._meta.get_field("interface").registry.get_name(obj.interface)

    def get_last_update_status(self, obj: Sensor) -> str:
        return obj.get_last_update_status_display()

    class Meta:
        fields = ("name", "slug", "visible", "status", "interface",
                  "last_update_status", "last_status_update_time", "last_status_update_log")
        read_only_fields = ("status", "last_update_status", "last_status_update_time", "last_status_update_log")


class SensorSerializer(DeviceSerializer):

    class Meta(DeviceSerializer.Meta):
        model = Sensor


class ActuatorSerializer(DeviceSerializer):

    class Meta(DeviceSerializer.Meta):
        model = Actuator


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    http_method_names = ['get', 'post', 'head']
    lookup_field = 'slug'

    @decorators.action(methods=['post'], detail=True, url_path='read-status')
    def read_status(self, request: "Request", *args: typing.Any, **kwargs: typing.Any) -> "Response":
        sensor = self.get_object()
        response_status = status.HTTP_200_OK

        try:
            sensor.read_status()
        except Exception:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        serializer = self.get_serializer(sensor)
        return Response(serializer.data, status=response_status)



class ActuatorViewSet(viewsets.ModelViewSet):
    queryset = Actuator.objects.all()
    serializer_class = ActuatorSerializer
    http_method_names = ['get', 'post', 'head']
    lookup_field = 'slug'

    @decorators.action(methods=['post'], detail=True, url_path='update-status')
    def update_status(self, request: "Request", *args: typing.Any, **kwargs: typing.Any) -> "Response":
        actuator = self.get_object()
        response_status = status.HTTP_200_OK

        try:
            actuator.update_status(**request.data)
        except Exception:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        serializer = self.get_serializer(actuator)
        return Response(serializer.data, status=response_status)
