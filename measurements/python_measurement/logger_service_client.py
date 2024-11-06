"""gRPC client for interacting with the Logger service."""

from typing import List, Optional

import grpc
from ni_measurement_plugin_sdk_service.discovery._client import DiscoveryClient
from stubs.log_measurement_pb2 import LogRequest
from stubs.log_measurement_pb2_grpc import LogMeasurementStub

GRPC_LOGGER_SERVICE_INTERFACE_NAME = "user.defined.logger.v1.LogService"

GRPC_LOGGER_SERVICE_CLASS = "user.defined.jsonlogger.v1.LogService"


class LoggerServiceClient:
    """Client for the Logger gRPC service."""

    def __init__(
        self,
        *,
        discovery_client: DiscoveryClient = DiscoveryClient(),
    ) -> None:
        """Initialize the LoggerServiceClient with a DiscoveryClient."""
        self._discovery_client = discovery_client
        self._stub: Optional[LogMeasurementStub] = None

    def _get_stub(self) -> LogMeasurementStub:
        """Create a gRPC stub for the Logger service."""
        if self._stub is None:
            # Resolve the service location using the discovery client.
            logger_service_location = self._discovery_client.resolve_service(
                provided_interface=str(GRPC_LOGGER_SERVICE_INTERFACE_NAME),
                service_class=str(GRPC_LOGGER_SERVICE_CLASS),
            )

            #  Create a gRPC channel to the resolved service location.
            channel = grpc.insecure_channel(logger_service_location.insecure_address)

            # Create a gRPC stub for the Logger service.
            self._stub = LogMeasurementStub(channel)
        return self._stub

    def log_measurement(
        self,
        measured_sites: List[int],
        measured_pins: List[str],
        current_measurements: List[float],
        voltage_measurements: List[float],
        in_compliance: List[bool],
    ) -> None:
        """Create and send a LogMeasurement request calling the server method."""
        request = LogRequest(
            measured_sites=measured_sites,
            measured_pins=measured_pins,
            current_measurements=current_measurements,
            voltage_measurements=voltage_measurements,
            in_compliance=in_compliance,
        )
        self._get_stub().Log(request)
