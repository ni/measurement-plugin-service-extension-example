"""Logger Service client stub modules."""

from stubs.log_measurement_pb2 import LogResponse
from stubs.log_measurement_pb2_grpc import (
    LogMeasurementServicer,
    add_LogMeasurementServicer_to_server,
)

__all__ = ["LogResponse", "LogMeasurementServicer", "add_LogMeasurementServicer_to_server"]
