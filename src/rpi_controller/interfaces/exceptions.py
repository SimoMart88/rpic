class InterfaceException(Exception):
    pass


class InterfaceConfigurationException(InterfaceException):
    pass


class InterfaceUserConfigurationException(InterfaceConfigurationException):
    pass


class InterfaceRuntimeException(InterfaceException):
    pass
