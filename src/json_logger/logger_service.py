"A user-defined service to log the measurement data to a JSON file."

import json

import grpc
from grpc.framework.foundation import logging_pool
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient, ServiceLocation
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo

from json_logger.stubs.log_measurement_pb2 import LogRequest, LogResponse
from json_logger.stubs.log_measurement_pb2_grpc import (
    LogMeasurementServicer,
    add_LogMeasurementServicer_to_server,
)

GRPC_SERVICE_INTERFACE_NAME = "user.defined.logger.v1.LogService"
GRPC_SERVICE_CLASS = "user.defined.jsonlogger.v1.LogService"
DISPLAY_NAME = "JSON Logger Service"


class LoggerService(LogMeasurementServicer):
    """A gRPC service that logs measurement data to a JSON file."""

    def Log(  # noqa: N802 - function name should be lowercase
        self, request: LogRequest, context: grpc.ServicerContext
    ) -> LogResponse:
        """Logs the received measurement data to a JSON file and prints the measurement.

        Args:
            request: The measurement data to be logged.
            context: The context of the request.

        Returns:
            The response after logging the measurement.
        """
        data = {
            "measured_sites": list(request.measured_sites),
            "measured_pins": list(request.measured_pins),
            "current_measurements": list(request.current_measurements),
            "voltage_measurements": list(request.voltage_measurements),
            "in_compliance": list(request.in_compliance),
        }

        # Append new data to the JSON file
        with open("measurements.json", mode="a", newline="") as file:
            json.dump(data, file)
            file.write("\n")

        # Note: The JSON formatting is not strictly followed as this is only a sample example.
        return LogResponse()


def start_server() -> None:
    """Starts the gRPC server and registers the service with the service registry."""
    server = grpc.server(logging_pool.pool(max_workers=10))
    add_LogMeasurementServicer_to_server(LoggerService(), server)
    host = "[::1]"
    port = str(server.add_insecure_port(f"{host}:0"))
    server.start()

    discovery_client = DiscoveryClient()
    service_location = ServiceLocation("localhost", f"{port}", "")
    service_info = ServiceInfo(
        service_class=GRPC_SERVICE_CLASS,
        description_url="",
        provided_interfaces=[GRPC_SERVICE_INTERFACE_NAME],
        display_name=DISPLAY_NAME,
    )
    registration_id = discovery_client.register_service(
        service_info=service_info, service_location=service_location
    )

    _ = input("Press enter to stop the server.")
    discovery_client.unregister_service(registration_id)
    server.stop(grace=5)


if __name__ == "__main__":
    start_server()
