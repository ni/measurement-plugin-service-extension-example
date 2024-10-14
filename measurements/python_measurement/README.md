# NI-DCPower Source DC Voltage

This is a measurement plug-in example that sources and measures a DC voltage with an NI SMU and
showcases logging measurement data to a custom logging service.

## Features

- Showcases the usage of a user-defined logger service that logs the measurement data.
- Uses the `nidcpower` package to access NI-DCPower from Python
- Demonstrates how to cancel a running measurement by breaking a long wait into
  multiple short waits
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files
- Includes a TestStand sequence showing how to configure the pin map, register
  instrument sessions with the session management service, and run a measurement
  - The TestStand sequence handles pin map and session registration and unregistration in the
    `Setup` and `Cleanup` sections of the main sequence. For **Test UUTs** and batch process model
    use cases, these steps should be moved to the `ProcessSetup` and `ProcessCleanup` callbacks.
- Uses the NI gRPC Device Server to allow sharing instrument sessions with other
  measurement services when running measurements from TestStand.

## Required Software

- InstrumentStudio 2024 Q3 or later
- NI-DCPower
- Recommended: TestStand 2021 SP1 or later
- grpc-stubs==1.53 or later
- grpcio==1.66 or later
- grpcio-tools==1.59 or later
- protobuf==4.25.4 or later

## Required Hardware

This example requires an NI SMU that is supported by NI-DCPower (e.g.
PXIe-4141).

By default, this example uses a physical instrument or a simulated instrument
created in NI MAX. To automatically simulate an instrument without using NI MAX,
follow the steps below:

- Create a `.env` file in the measurement service's directory or one of its
  parent directories (such as the root of your Git repository or
  `C:\ProgramData\National Instruments\Plug-Ins\Measurements` for statically
  registered measurement services).
- Add the following options to the `.env` file to enable simulation via the
  driver's option string:

  ```python
  MEASUREMENT_PLUGIN_NIDCPOWER_SIMULATE=1
  MEASUREMENT_PLUGIN_NIDCPOWER_BOARD_TYPE=PXIe
  MEASUREMENT_PLUGIN_NIDCPOWER_MODEL=4141
  ```
