class DeviceException(Exception):
    pass


class SensorException(DeviceException):
    pass


class ActuatorException(DeviceException):
    pass
