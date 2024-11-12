# Measurement Plug-In Service Extension Example

- [Measurement Plug-In Service Extension Example](#measurement-plug-in-service-extension-example)
  - [Custom gRPC Services in Measurement Plug-In framework](#custom-grpc-services-in-measurement-plug-in-framework)
  - [User Workflow](#user-workflow)
  - [Required Software](#required-software)
  - [Steps to create a gRPC service](#steps-to-create-a-grpc-service)
    - [Note](#note)
  - [Creating Python Client Modules](#creating-python-client-modules)
  - [Creating LabVIEW Client Modules](#creating-labview-client-modules)

## Custom gRPC Services in Measurement Plug-In framework

The Measurement Plug-In architecture is based on microservices, with components functioning as gRPC
services. Since gRPC is network-based, it allows these components to be language-agnostic and work
seamlessly across different programming environments. Any feature extensions or customizations,
therefore, should also be implemented as gRPC services.

A user-defined gRPC service is a custom-built service where you define the service methods and
message types in a `.proto` file, generate client and server code, and implement the server logic.
Registering this service with the NI Discovery Service allows various clients to access and
communicate with it over gRPC, making it easy to integrate across technology stacks.

Data loggers are often used to record measurements and debug data during execution. For example, a
logger implemented in Python might only be compatible with Python-based systems. However, if other
measurement plug-ins are written in languages like LabVIEW or C#, direct integration may not be
possible. By converting the logger into a gRPC service and registering it with the NI Discovery
Service, it becomes accessible to all measurement plug-ins, regardless of language.

## User Workflow

![User Workflow](./docs/images/user_workflow.png)

## Required Software

- [InstrumentStudio 2024
  Q3](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#544066)
  or later
- [TestStand 2021
  SP1](https://www.ni.com/en/support/downloads/software-products/download.teststand.html#445937) or
  later (recommended)
- [Python 3.9](https://www.python.org/downloads/release/python-390/) or later
- [LabVIEW 2021
  SP1](https://www.ni.com/en/support/downloads/software-products/download.labview.html#443865) or
  later

Package dependencies,

- [Measurement Plug-In SDK Service for
  LabVIEW](https://www.vipm.io/package/ni_measurement_plugin_sdk_service/)
- [Measurement Plug-In SDK Service for
  Python](https://pypi.org/project/ni_measurement_plugin_sdk_service/)
  
## Steps to create a gRPC service

  1. Define the gRPC Service and Implement the Server:
     - Begin by defining a .proto file to specify the service's structure and data types as
       instructed [here](https://grpc.io/docs/languages/python/basics/#defining-the-service).
     - Generate the client and server code based on the .proto file.
     - Implement the gRPC server following the generated code.
     - Example: See the repository for a gRPC server initialization
       [example](./src/json_logger/logger_service.py#L53-L71).
  2. Register the Service with NI Discovery Service:
     - Use the discovery client from the Python or LabVIEW service package to register the
       user-defined service with the NI Discovery Service, providing its location details. This
       registration enables the service to be accessed and utilized within measurement plug-ins.
     - Example: Implementation of a [Logger service](./src/json_logger/logger_service.py).

### Note

- It is recommended to use the NI Discovery Service for dynamic service location resolution instead
  of relying on a static port number. Static port numbers can lead to conflicts and are less
  adaptable to changes in the network environment.
- Dynamically resolving the service's port number allows for services to be relocated or scaled
  across multiple machines without the need to modify client configurations. This approach results
  in more robust and maintainable deployments.

  The following **flow chart** outlines the steps required to create a user-defined service and
  registering it with the NI Discovery service.
  
  ![Register logger service](./docs/images/register_service_flowchart.JPG)

## Creating Python Client Modules

- Generate the client stubs for the user-defined service.
- Refer to the [instructions](https://grpc.io/docs/languages/python/basics/#creating-a-stub) to
  create a stub.
- Create a client module to establish a connection with the user-defined service from the python
  measurements.
- Define Service Interface and Service Class Names inside the module.
- Create a class that abstracts the methods from the generated client stubs to interact with the
  service.
- Use a discovery client to resolve the service location.
- Establish a gRPC channel to the service and create a stub for making API calls.
- Define methods in the client class to call the service methods, constructing and sending requests
  as needed.
- Example: [Establish connection to custom logger service in
  python](./examples/python_measurement/logger_service_client.py).

## Creating LabVIEW Client Modules

- Install gRPC and LabVIEW gRPC Server and Client tool packages.
  - Refer to this
    [link](https://github.com/ni/grpc-labview/blob/master/docs/QuickStart.md#labview-grpc) for
    installation instructions.

- Generate client interfaces from the .proto file to communicate with the service methods using the
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
    - Instantiate a DiscoveryClient to resolve the service location.

  Example:
  
  ![Establish Connection](./docs/images/establish_connection.png)

- In addition to establishing the connection, create a VI to call the service APIs using the gRPC ID
  obtained from the output of the previous VI.
  - Use the client generated during the stub creation process to call the service APIs.
  - The client then calls the Service APIs by obtaining the request models from the measurement
    service.

  Example:
  
  ![Call Service Methods](./docs/images/call_apis.png)

- Finally, Create a VI to ensure that the client is properly closed without any open connections and
  all associated resources are released for the client.

  Example:
  
  ![Call Service Method](./docs/images/destroy_client.png)

The following **flow chart** details the steps necessary to integrate a user-defined service into
  the measurement service.

![Resolve logger service](./docs/images/resolve_service_flowchart.JPG)
