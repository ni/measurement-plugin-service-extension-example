# Custom Measurement Plugin Services

This README provides a step-by-step guide to create a data logging service. The process involves
creating a proto file, generating stubs, establishing a connection and usage of the datalogger
service in different Measurements.

- Protobuf Compiler
- gRPC
- Python (or your preferred language)
- gRPC tools for Python (or your preferred language)

## Step 1: Create a Proto File

Create a `.proto` file that defines the service and messages.

```proto
syntax = "proto3";

package custom_measurement;

service DataLoggingService {
    rpc LogData (LogRequest) returns (LogResponse);
}

message LogRequest {
    string data = 1;
}

message LogResponse {
    bool success = 1;
}
```

## Step 2: Generate Stubs

Use the protobuf compiler to generate the gRPC code from the proto file.

```sh
protoc --python_out=. --grpc_python_out=. <proto_file>
```

## Step 3: Implement the Logger Service

Create a server implementation for the service.

- Initialize a gRPC server.
- Register the DataLoggingService implementation with the gRPC server. This allows the server to
  handle incoming requests.
- Configure and start a gRPC server to listen for incoming connections on a port, and then keep the
  server running indefinitely to handle incoming requests.

```python
import grpc
from concurrent import futures
import custom_measurement_pb2
import custom_measurement_pb2_grpc

class DataLoggingService(custom_measurement_pb2_grpc.DataLoggingServiceServicer):
        def LogData(self, request, context):
                print(f"Received data: {request.data}")
                return custom_measurement_pb2.LogResponse(success=True)

def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        custom_measurement_pb2_grpc.add_DataLoggingServiceServicer_to_server(DataLoggingService(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()

if __name__ == '__main__':
        serve()
```

## Step 4: Establish Connection

Create a client to connect to the server and log data.

- Create a gRPC client that connects to a server running on a localhost.
- This creates a stub for the custom service.

```python
import grpc
import custom_measurement_pb2
import custom_measurement_pb2_grpc

def run():
        with grpc.insecure_channel('localhost:50051') as channel:
                stub = custom_measurement_pb2_grpc.DataLoggingServiceStub(channel)
                response = stub.LogData(custom_measurement_pb2.LogRequest(data='Sample data'))
                print(f"Log success: {response.success}")

if __name__ == '__main__':
        run()
```

## Using the Logging Service in Python

- Define Service Interface and Class Names:
  - Set the gRPC service interface and class names.

```python
GRPC_SERVICE_INTERFACE_NAME = "ni.measurementlink.logger.v1.LogService"
GRPC_SERVICE_CLASS = "ni.measurementlink.logger.v1.LogService"
```

- Create a Discovery Client:
  - Instantiate a DiscoveryClient to resolve the service location.

```python
discovery_client = DiscoveryClient()
```

- Resolve the Service Location:
  - Use the discovery client to resolve the service location based on the provided interface and
    service class.

```python
service_location = discovery_client.resolve_service(
    provided_interface=GRPC_SERVICE_INTERFACE_NAME,
    service_class=GRPC_SERVICE_CLASS
)
```

- Create a gRPC Channel:
  - Create an insecure gRPC channel to the resolved service location.

```python
channel = grpc.insecure_channel(service_location.insecure_address)
```

- Create a Stub for the Logging Service:
  - Create a stub for the LogMeasurement service using the gRPC channel.

```python
stub = stubs.log_measurement_pb2_grpc.LogMeasurementStub(channel=channel)
```

- Prepare the Data for Logging:

```python
voltage = [measurement.voltage for measurement in measurements]
current = [measurement.current for measurement in measurements]
in_compliance = [measurement.in_compliance for measurement in measurements]
```

- Call the LogMeasurement API:

```python
stub.LogMeasurement(LogMeasurementRequest(
    measured_sites=measured_sites,
    measured_pins=measured_pins,
    voltage=voltage,
    current=current,
    in_compliance=in_compliance,
))
```

## Using the Logging Service in LabVIEW

## Conclusion

This guide covered creating a proto file, generating stubs, implementing the service, establishing a
connection and usage of the datalogger service in different Measurements.
