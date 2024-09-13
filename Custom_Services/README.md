# Custom Measurement Plugin Services

This README provides a step-by-step guide to create a data logging service. The process involves
creating a proto file, generating stubs, and establishing a connection.

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
protoc --python_out=. --grpc_python_out=. custom_measurement.proto
```

## Step 3: Implement the Service

Create a server implementation for the service.

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

## Conclusion

This guide covered creating a proto file, generating stubs, implementing the service, and
establishing a connection.
