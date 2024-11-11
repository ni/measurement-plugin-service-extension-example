# NI-DCPower Source DC Voltage

This is a measurement plug-in example that sources and measures a DC voltage with an NI SMU and
includes additional functionality to log measurement data using a custom logging service.

## Features

- Showcases the usage of a user-defined logger service that logs the measurement data.
- Uses the NI-DCPower LabVIEW API
- Pin-aware, supporting one session and multiple pins
  - Sources the same DC voltage level on all selected pin/site combinations
  - Measures the DC voltage and current for each selected pin/site combination
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files
- Includes a TestStand sequence showing how to configure the pin map, register
  instrument sessions with the session management service, and run a measurement.
  - For the sake of simplicity, the TestStand sequence handles pin map and session registration and
    unregistration in the `Setup` and `Cleanup` sections of the main sequence. For **Test UUTs** and
    batch process model use cases, these steps should be moved to the `ProcessSetup` and
    `ProcessCleanup` callbacks.
- Uses the NI gRPC Device Server to allow sharing instrument sessions with other
  measurement services when running measurements from TestStand

## Software Requirements

### Core Requirements

- [LabVIEW 2021 SP1](https://www.ni.com/en/support/downloads/software-products/download.labview.html#443865) or later
- [InstrumentStudio 2024 Q3](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#544066) or later
- [TestStand 2021 SP1](https://www.ni.com/en/support/downloads/software-products/download.teststand.html#445937) or later (recommended)
- [NI-DCPower 2023 Q1](https://www.ni.com/en/support/downloads/drivers/download.ni-dcpower.html#477835) or later

### Additional Tools

- [gRPC Server-Client [2] - Code Generator](https://github.com/ni/grpc-labview/releases/download/v1.2.6.1/grpc-labview.zip)
- [Measurement Plug-In SDK](https://github.com/ni/measurement-plugin-labview/releases/tag/v3.1.0.5)

## Hardware Requirements

- This example requires an NI SMU that is supported by NI-DCPower (e.g. PXIe-4141).
- [Simulation Setup Instructions](#simulation-setup)

## Simulation Setup

To simulate an NI SMU:

1. Open NI MAX
2. Right-click "Devices and Interfaces"
3. Select "Create New..."
4. Choose "Simulated NI-DAQmx Device or Modular Instrument"
5. Select from "Power Supplies" category
