from grpc.framework.foundation import logging_pool
from datetime import datetime
import os
import grpc
import csv
import json
from stubs.log_measurement_pb2 import LogMeasurementResponse
from stubs.log_measurement_pb2_grpc import LogMeasurementServicer, add_LogMeasurementServicer_to_server
from bdcdatalogger import Channel, Fields, MeasurementDetails, Series, TestRun, Waveform
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient, ServiceLocation
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo


class MeasurementService(LogMeasurementServicer):
    def LogMeasurement(self, request, context):
        # Implement your logic to handle the measurement request here
        # For example, you can log the measurement data to a file or database
        METADATA = {
            Fields.ProgramName: "DC Power",
        }

        run = TestRun(
            metadata=METADATA, folder_path=os.path.join(os.getcwd(), "test log"), file_name="test_example"
            )
        data = run.Metadata()

        for pin_index,pin in enumerate(request.measured_pins):
            data.add_numeric_parameter("Site", float(request.measured_sites[pin_index]), "S")
            data.add_string_parameter("Pin", pin)
            voltage_measurement = MeasurementDetails(
                            name="Vout",
                            spec_id="VAD",
                            value=request.voltage[pin_index],
                            unit="V",
                        )
            data.add_additional_info("Current", str(request.current[pin_index]) + "A")
            data.add_additional_info("In-Compliance", str(request.in_compliance[pin_index]))
            data.add_additional_info("Logged Time", str(datetime.now().strftime("%Y-%m-%d:%H:%M:%S")))
            run.log_measurement(voltage_measurement)
      
        # Remove metadata and parameters(conditions) added with Metadata() object
        data.remove_all_metadata()
        data.remove_all_parameters()
        data.remove_all_additional_info()

        run.close_datalog()
        print(f"Received measurement: {request}")
        return LogMeasurementResponse()

def serve():
    server = grpc.server(logging_pool.pool(max_workers=10))
    add_LogMeasurementServicer_to_server(MeasurementService(), server)
    host = "[::1]"
    port = str(server.add_insecure_port(f"{host}:0"))
    server.start()
    
    discovery_client = DiscoveryClient()
    service_location = ServiceLocation("localhost", f'{port}', "")
    service_info = ServiceInfo("ni.measurementlink.logger.v1.LogService", "", ["ni.measurementlink.logger.v1.LogService"], display_name="LogService")
    registration_id = discovery_client.register_service(service_info=service_info, service_location=service_location)
    
    _ = input("Press enter to stop the server.")
    discovery_client.unregister_service(registration_id)
    server.stop(grace=5)

if __name__ == '__main__':
    serve()