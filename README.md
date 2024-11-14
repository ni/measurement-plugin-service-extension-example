# Measurement Plug-In Service Extension Example

- [Measurement Plug-In Service Extension Example](#measurement-plug-in-service-extension-example)
  - [Custom gRPC Service in Measurement Plug-In](#custom-grpc-service-in-measurement-plug-in)
  - [Required Software](#required-software)
  - [User flow](#user-flow)
  - [Steps to create and register a custom gRPC service](#steps-to-create-and-register-a-custom-grpc-service)
    - [Note](#note)
  - [Creating Clients for the custom gRPC Service](#creating-clients-for-the-custom-grpc-service)
    - [Python](#python)
    - [LabVIEW](#labview)

## Custom gRPC Service in Measurement Plug-In

The Measurement Plug-In architecture is built on a microservices model, with each component
functioning as a gRPC service. As a network-based protocol, gRPC enables these components to be
language-agnostic, allowing seamless interoperability across diverse programming environments. This
approach ensures that any feature extensions or customizations can also be implemented as gRPC
services.

A user-defined gRPC service is a custom service in which you specify service methods and message
types in a `.proto` file, generate client and server code, and implement the server logic.
Registering this service with the NI Discovery Service enables various clients to access and
communicate with it over gRPC, simplifying integration across technology stacks.

This repository includes a sample logger service that demonstrates how a typical data
logger can be made into a gRPC service. By registering this gRPC-based logger with the NI Discovery
Service, the provided examples showcase seamless integration, enabling all measurement plug-ins,
regardless of language (e.g., Python, LabVIEW, or C#), to access the logger service and record
measurement during execution.

## Required Software

- [InstrumentStudio 2024
  Q4](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#549673)
  or later
- [TestStand 2021
  SP1](https://www.ni.com/en/support/downloads/software-products/download.teststand.html#445937) or
  later (recommended)
- [LabVIEW 2021
  SP1](https://www.ni.com/en/support/downloads/software-products/download.labview.html#443865) or
  later
- [Python 3.9](https://www.python.org/downloads/release/python-390/) or later

Package dependencies:

- [Measurement Plug-In SDK Service for LabVIEW
  3.1.0.6](https://www.vipm.io/package/ni_measurement_plugin_sdk_service/) or later
- [Measurement Plug-In SDK Service for Python
  2.1.0](https://pypi.org/project/ni_measurement_plugin_sdk_service/) or later

## User flow

![User flow](./docs/images/user_workflow.png)

## Steps to create and register a custom gRPC service

- The flowchart below outlines the steps for creating a custom gRPC service and registering it with
  the NI Discovery service.

  ![Register service](./docs/images/register_service_flowchart.JPG)

1. Define the gRPC Service and implement the Server:
   - Begin by defining a `.proto` file to specify the service structure and data types, following
    the instructions provided
    [here](https://grpc.io/docs/languages/python/basics/#defining-the-service).
   - Generate the client and server code based on the `.proto` file.
   - Implement the gRPC server using the generated code.
   - Refer to the repository for an example of gRPC server initialization
    [here](./src/json_logger/logger_service.py#L53-L71).
2. Register the Service with the NI Discovery Service:
   - Use the discovery client from the Python or LabVIEW service package to register the
    user-defined service with the NI Discovery Service, providing its location details. This
    registration enables the service to be accessed and utilized within measurement plug-ins.
   - See the example implementation of the [logger service](./src/json_logger/logger_service.py)
    for reference.

### Note

- It is recommended to use the NI Discovery Service for dynamic service location resolution instead
  of relying on a static port number. Static port numbers can lead to conflicts and are less
  adaptable to changes in the network environment.
- Dynamically resolving the service's port number allows for services to be relocated or scaled
  across multiple machines without the need to modify client configurations. This approach results
  in more robust and maintainable deployments.

## Creating Clients for the custom gRPC Service

- The flowchart below details the steps necessary to integrate a user-defined service into
  the measurement service.

  ![Resolve logger service](./docs/images/resolve_service_flowchart.JPG)

### Python

- Generate the client stubs for the user-defined service.
- Refer to the instructions provided
  [here](https://grpc.io/docs/languages/python/basics/#creating-a-stub) to create a stub.
- Create a client module to establish a connection with the user-defined service from the python
  measurements.
- Define Service Interface and Service Class Names inside the module.
- Create a class that abstracts the methods from the generated client stubs to interact with the
  service.
- Resolve the service location using the discovery client.
- Establish a gRPC channel to the service and create a stub for making API calls.
- Define methods in the client class to call the service methods, constructing and sending requests
  as needed.
- Example: [logger_service_client.py](./examples/python_measurement/logger_service_client.py).

### LabVIEW

- Install gRPC and LabVIEW gRPC Server and Client tool packages.
  - Refer to this
    [document](https://github.com/ni/grpc-labview/blob/master/docs/QuickStart.md#labview-grpc) for
    installation instructions.

- Generate client interfaces from the `.proto` file to communicate with the service methods using the
  `gRPC Server-Client [2] - Code Generator`.
  
  ![gRPC Server Client Generator](./docs/images/gRPC_Server_Client_Generator.png)

- Establish the connection to communicate with the service methods.
- Create client VIs under a common class to interact with the user-defined service from LabVIEW
  measurements.
- Develop a client VI to initially establish a connection between the service and the measurement.
  - Define Service Interface and Class Names:
    - Provide the gRPC service interface and class names as inputs to the Resolve Service API to
      retrieve the port where the user-defined service is running.
  - Create a Discovery Client:
    - Instantiate a `DiscoveryClient` to resolve the service location.

  - Example:
  
    ![Establish Connection](./docs/images/establish_connection.png)

- In addition to establishing the connection, create a VI to call the service APIs using the gRPC ID
  obtained from the output of the previous VI.
  - Use the client generated during the stub creation process to call the service APIs.
  - The client then calls the Service APIs by obtaining the request models from the measurement
    service.

  - Example:
  
    ![Call Service Methods](./docs/images/call_apis.png)

- Finally, Create a VI to ensure that the client is properly closed without any open connections and
  all associated resources are released for the client.

  - Example:

    ![Call Service Method](./docs/images/destroy_client.png)
