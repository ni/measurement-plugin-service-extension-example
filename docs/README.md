# Custom Measurement Plugin Services

This README provides a step-by-step guide to create a custom service. The process involves creating
a proto file, generating stubs, establishing a connection, and using the custom service in
different measurements.

## Steps

- Define the service.
  - Example:
  [Logger service proto](../src/csv_logger/log_measurement.proto).
- Generate server interfaces from the service definition. Implement the servicer interface generated
  from the service definition, ensuring that the method implementation is complete.
- Set up a gRPC server to handle client requests and execute the service's tasks.
  - Example:
  [Logger service implementation](../src/csv_logger/logger_service.py).
- Establish the connection to communicate with the service methods.
  - Create stubs to call the service methods.
  - Instantiate a discovery client to resolve the service location.
  - Create an insecure gRPC channel to the resolved service location.
  - Create a stub for the CustomService using the gRPC channel.
  - Call the service methods through the stubs.
  - Example:
  [Establish connection to custom logger service in python](../measurements/python_measurement/measurement.py).

## Integrating the the Custom Service in LabVIEW measurements

- Generate client interfaces from the the .proto file to communicate with the service methods using
  the `gRPC Server-Client [2] - Code Generator`.

!["gRPC Server-Client [2] - Code Generator](gRPC_server_client_generator.JPG)

- Define Service Interface and Class Names:
  - Provide the gRPC service interface and class names as inputs to the Resolve Service API to
    retrieve the port where the custom service is running.

!["Get_Port"](define_service.png)

- Create a Discovery Client:
  - Instantiate a DiscoveryClient to resolve the service location.

!["Create_Client"](create_client.png)

- The client calls the Service APIs by obtaining the request models from the measurement service.

## Conclusion

This guide covered creating a proto file, generating stubs, implementing the service, establishing a
connection, and using the custom service in different measurements.
