"A user-defined service to log the measurement data in BDC format."

from datetime import datetime
import pathlib

import grpc
from bdcdatalogger import Fields, MeasurementDetails, TestRun
from grpc.framework.foundation import logging_pool
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient, ServiceLocation
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo
from stubs.bdc_logger_pb2 import LogResponse
from stubs.bdc_logger_pb2_grpc import (
    LogMeasurementServicer,
    add_LogMeasurementServicer_to_server,
)

GRPC_SERVICE_INTERFACE_NAME = "user.defined.logger.v1.LogService"
GRPC_SERVICE_CLASS = "user.defined.bdclogger.v1.LogService"
DISPLAY_NAME = "BDC Logger Service"

class MeasurementService(LogMeasurementServicer):
    """A gRPC service that logs measurement data to a CSV file in BDC format."""

    def Log(self, request, context):
        """Logs the measurement data received in the request to a CSV file in BDC format and prints
        the received measurement.

        Args:
            request: The measurement data to be logged.
            context: The context of the request.

        Returns:
            The response after logging the measurement.
        """
        METADATA = {
            Fields.ProgramName: "DC Power",
        }

        run = TestRun(
            metadata=METADATA,
            folder_path= pathlib.Path.cwd() / "test log",
            file_name="test_example",
        )
        data = run.Metadata()

        for pin_index, pin in enumerate(request.measured_pins):
            data.add_numeric_parameter("Site", float(request.measured_sites[pin_index]), "S")
            data.add_string_parameter("Pin", pin)
            voltage_measurement = MeasurementDetails(
                name="Vout",
                spec_id="VAD",
                value=request.voltage_measurements[pin_index],
                unit="V",
            )
            data.add_additional_info("Current", str(request.current_measurements[pin_index]) + "A")
            data.add_additional_info("In-Compliance", str(request.in_compliance[pin_index]))
            data.add_additional_info(
                "Logged Time", str(datetime.now().strftime("%Y-%m-%d:%H:%M:%S"))
            )
            run.log_measurement(voltage_measurement)

        # Remove metadata and parameters(conditions) added with Metadata() object
        data.remove_all_metadata()
        data.remove_all_parameters()
        data.remove_all_additional_info()

        run.close_datalog()
        print(f"Received measurement: {request}")
        return LogResponse()


def serve():
    server = grpc.server(logging_pool.pool(max_workers=10))
    add_LogMeasurementServicer_to_server(MeasurementService(), server)
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
    serve()
