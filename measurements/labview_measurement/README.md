## NI-DCPower Source DC Voltage

This is a measurement plug-in example that sources and measures a DC voltage with an NI SMU and
includes additional functionality to log measurement data using a custom logging service.

### Features

- Includes a custom logging service that logs measurement data centrally. This functionality ensures
  that all measurement data is easily accessible for monitoring and analysis.
- Uses the NI-DCPower LabVIEW API
- Pin-aware, supporting one session and multiple pins
  - Sources the same DC voltage level on all selected pin/site combinations
  - Measures the DC voltage and current for each selected pin/site combination
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files
- Includes a TestStand sequence showing how to configure the pin map, register
  instrument sessions with the session management service, and run a measurement.
  - For the sake of simplicity, the TestStand sequence handles pin map and session registration and unregistration in the `Setup` and `Cleanup` sections of the main sequence. For **Test UUTs** and batch process model use cases, these steps should be moved to the `ProcessSetup` and `ProcessCleanup` callbacks.
- Uses the NI gRPC Device Server to allow sharing instrument sessions with other
  measurement services when running measurements from TestStand

### NOTE

TThe Logger Service is integrated with the Measurement Service. Therefore, starting the Measurement
Service without the Logger Service will result in an error indicating that the Logger Service was
not found. To avoid this, the Logger Service must be started and registered with the discovery
service before it can be called from the Measurement Service.

### Required Driver Software

- NI-DCPower 2023 Q1 or later

### Required Hardware

This example requires an NI SMU that is supported by NI-DCPower (e.g. PXIe-4141).

To simulate an NI SMU in software: open `NI MAX`, right-click `Devices and Interfaces`,
select `Create New...`, and select `Simulated NI-DAQmx Device or Modular Instrument`.
SMUs are in the `Power Supplies` category.
