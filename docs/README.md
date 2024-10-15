# Integrating Python User-defined Services with Measurement Plug-In

This README provides a step-by-step guide for creating a python user-defined gRPC service and integrating
it with measurement services. The process includes defining the service, generating stubs,
registering it with the NI Discovery Service, and using the service in the measurement plug-in.

## Required Software

- [InstrumentStudio 2024 Q3](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#544066)
  or later
- Recommended: [TestStand 2021 SP1](https://www.ni.com/en/support/downloads/software-products/download.teststand.html#445937)
  or later

The software dependencies required for LabVIEW measurements are listed in
[LabVIEW](../measurements/labview_measurement/README.md).

The software dependencies required for Python measurements are listed in
[Python Measurement](../measurements/python_measurement/README.md).

## User Workflow

![User Workflow](user_workflow.png)

## Steps to create a user-defined service

- Follow the steps outlined
  [here](https://grpc.io/docs/languages/python/basics/#defining-the-service) to define a proto
  file, create client and server code, and implement the gRPC server.
  - [Initialization of the gRPC server example - repo](https://github.com/ni/custom-measurement-plugin-services/blob/d9c7657c0f48d6cb733a1fe422e5491815cc51c1/src/json_logger/logger_service.py#L52-L70).
- Using the NI Discovery client, register the service to the NI Discovery service with its location
  information. This enables the user-defined service to be fetched and used in the measurement
  plug-ins.
  - Example:
  [Logger service implementation](../src/json_logger/logger_service.py).

The following **flow chart** outlines the steps required to create a user-defined service and
registering it with the NI Discovery service .

![Register logger service](register_service_flowchart.JPG)

## Steps to interact with the user-defined service by creating a client module in Python measurements

- Generate the client stubs for the user-defined service.
- Refer to the [instructions](https://grpc.io/docs/languages/python/basics/#creating-a-stub) to
  create a stub.
- Create a client module to establish a connection with the user-defined service from the python measurements.
- Define Service Interface and Service Class Names inside the module.
- Create a client class that uses the generated client stubs to interact with the service.
- Use a discovery client to resolve the service location.
- Establish a gRPC channel to the service and create a stub for making API calls.
- Define methods in the client class to call the service methods, constructing and sending requests
  as needed.
- Example:
  [Establish connection to custom logger service in python](../measurements/python_measurement/logger_service_client.py).

## Steps to interact with the user-defined service by creating client modules in LabVIEW measurements

- Install gRPC and LabVIEW gRPC Server and Client tool packages.
  - Refer to this
    [link](https://github.com/ni/grpc-labview/blob/master/docs/QuickStart.md#labview-grpc)
    for installation instructions.

- Generate client interfaces from the the .proto file to communicate with the service methods using
  the `gRPC Server-Client [2] - Code Generator`.

  <div style="text-align: center;">
    <img src="gRPC_Server_Client_Generator.png" alt="gRPC Server Client Generator" width="50%">
  </div>

- Establish the connection to communicate with the service methods.
- Create client VIs under a common class to interact with the user-defined service from LabVIEW
  measurements.
- Develop a client VI to initially establish a connection between the service and the measurement.
  - Define Service Interface and Class Names:
    - Provide the gRPC service interface and class names as inputs to the Resolve Service API to
      retrieve the port where the user-defined service is running.
  - Create a Discovery Client:
    - Instantiate a DiscoveryClient to resolve the service location.

  Example:

  <div style="text-align: center;">
    <img src="establish_connection.png" alt="Establish Connection" width="75%">
  </div>

- In addition to establishing the connection, create a VI to call the service APIs using the gRPC ID
  obtained from the output of the previous VI.
  - Use the client generated during the stub creation process to call the service APIs.
  - The client then calls the Service APIs by obtaining the request models from the measurement
    service.

  Example:
  
  <div style="text-align: center;">
    <img src="call_apis.png" alt="Call Service Methods" width="75%">
  </div>

- Finally, Create a VI to ensure that the client is properly closed without any open connections and
  all associated resources are released for the client.

  Example:

  <div style="text-align: center;">
    <img src="destroy_client.png" alt="Call Service Methods" width="75%">
  </div>

The following **flow chart** details the steps necessary to integrate a user-defined service into the
measurement service.

![Resolve logger service](resolve_service_flowchart.JPG)
