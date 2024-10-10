from typing import Optional
import grpc
from ni_measurement_plugin_sdk_service.discovery._client import DiscoveryClient
from stubs.log_measurement_pb2_grpc import LogMeasurementStub
from stubs.log_measurement_pb2 import LogRequest

# The service interface constant should be updated if the user intends to use a interface other than
# the logger service interface.
GRPC_LOGGER_SERVICE_INTERFACE_NAME = "user.defined.logger.v1.LogService"

# The service class constant should be updated if the user intends to use a service other than the
# JSON logger service.
GRPC_LOGGER_SERVICE_CLASS = "user.defined.jsonlogger.v1.LogService"

class LoggerServiceClient:
    def __init__(
        self,
        *,
        discovery_client: Optional[DiscoveryClient] = None,
        grpc_channel: Optional[grpc.Channel] = None,
    ) -> None:
        self.discovery_client = discovery_client
        self._stub: Optional[LogMeasurementStub] = (
            None
        )

        if grpc_channel is not None:
            self._stub = LogMeasurementStub(
                grpc_channel
            )

    def _get_stub(self) -> LogMeasurementStub:
        """Create a gRPC stub for the Logger service."""       
        if self._stub is None:
            # Resolve the service location using the discovery client
            logger_service_location = self.discovery_client.resolve_service(
                provided_interface=str(GRPC_LOGGER_SERVICE_INTERFACE_NAME),
                service_class=str(GRPC_LOGGER_SERVICE_CLASS),
            )
            
            #  Create a gRPC channel to the resolved service location
            channel = grpc.insecure_channel(logger_service_location.insecure_address)

            # Create a gRPC stub for the Logger service
            self._stub = LogMeasurementStub(channel)
        return self._stub

    def _log_measurement(self, measured_sites, measured_pins, current_measurements, voltage_measurements, in_compliance):
        """Create and send a LogMeasurement request calling the server method."""
        request = LogRequest(
            measured_sites=measured_sites,
            measured_pins=measured_pins,
            current_measurements=current_measurements,
            voltage_measurements=voltage_measurements,
            in_compliance=in_compliance
        )
        self._get_stub().Log(request)
        