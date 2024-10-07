"""A custom service for logging measurement data to a CSV file."""

import csv

import grpc
from grpc.framework.foundation import logging_pool
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient, ServiceLocation
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo
from stubs.log_measurement_pb2 import LogResponse
from stubs.log_measurement_pb2_grpc import (
    LogMeasurementServicer,
    add_LogMeasurementServicer_to_server,
)

GRPC_SERVICE_INTERFACE_NAME = "user.defined.csvlogger.v1.LogService"
GRPC_SERVICE_CLASS = "user.defined.csvlogger.v1.LogService"

class MeasurementService(LogMeasurementServicer):
    """A gRPC service that logs measurement data to a CSV file."""
    
    def Log(self, request, context):
        """Logs the measurement data received in the request to a CSV file and prints the received
        measurement.

        Args:
            request: The measurement data to be logged.
            context: The context of the request.

        Returns:
            The response after logging the measurement.
        """
        with open("measurements.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([request])

        print(f"Received measurement: {request}")
        return LogResponse()


def serve():
    """Starts the gRPC server and registers the service with the service registry."""
    server = grpc.server(logging_pool.pool(max_workers=10))
    add_LogMeasurementServicer_to_server(MeasurementService(), server)
    host = "[::1]"
    port = str(server.add_insecure_port(f"{host}:0"))
    server.start()

    discovery_client = DiscoveryClient()
    service_location = ServiceLocation("localhost", f"{port}", "")
    service_info = ServiceInfo(
        GRPC_SERVICE_CLASS,
        "",
        [GRPC_SERVICE_INTERFACE_NAME],
        display_name="CSV Logger Service",
    )
    registration_id = discovery_client.register_service(
        service_info=service_info, service_location=service_location
    )

    _ = input("Press enter to stop the server.")
    discovery_client.unregister_service(registration_id)
    server.stop(grace=5)


if __name__ == "__main__":
    serve()
