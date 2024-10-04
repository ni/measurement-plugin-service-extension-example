from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LogMeasurementResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class LogMeasurementRequest(_message.Message):
    __slots__ = ["measured_sites", "measured_pins", "voltage", "current", "in_compliance"]
    MEASURED_SITES_FIELD_NUMBER: _ClassVar[int]
    MEASURED_PINS_FIELD_NUMBER: _ClassVar[int]
    VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    IN_COMPLIANCE_FIELD_NUMBER: _ClassVar[int]
    measured_sites: _containers.RepeatedScalarFieldContainer[int]
    measured_pins: _containers.RepeatedScalarFieldContainer[str]
    voltage: _containers.RepeatedScalarFieldContainer[float]
    current: _containers.RepeatedScalarFieldContainer[float]
    in_compliance: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(self, measured_sites: _Optional[_Iterable[int]] = ..., measured_pins: _Optional[_Iterable[str]] = ..., voltage: _Optional[_Iterable[float]] = ..., current: _Optional[_Iterable[float]] = ..., in_compliance: _Optional[_Iterable[bool]] = ...) -> None: ...
