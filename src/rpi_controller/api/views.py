import typing
from rest_framework import viewsets, serializers, decorators
from rest_framework.response import Response

from rpi_controller.models import Sensor


if typing.TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.response import Response


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    interface = serializers.SerializerMethodField()
    last_update_status = serializers.SerializerMethodField()
    last_status_update = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def get_interface(self, obj: Sensor) -> str:
        return obj._meta.get_field("interface").registry.get_name(obj.interface)

    def get_last_update_status(self, obj: Sensor) -> str:
        return obj.get_last_update_status_display()

    class Meta:
        model = Sensor
        fields = ("name", "slug", "visible", "status", "interface",
                  "last_update_status", "last_status_update", "last_status_update_log")
        read_only_fields = ("status", "last_update_status", "last_status_update", "last_status_update_log")


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    http_method_names = ['get', 'post', 'head']
    lookup_field = 'slug'

    @decorators.action(methods=['post'], detail=True)
    def use(self, request: "Request", *args: typing.Any, **kwargs: typing.Any) -> "Response":
        sensor = self.get_object()
        sensor.use()
        serializer = self.get_serializer(sensor)
        return Response(serializer.data)
