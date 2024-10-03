"""Source and measure a DC voltage with an NI SMU."""

from __future__ import annotations

import pathlib
import sys
import threading
import time
from contextlib import ExitStack
from typing import TYPE_CHECKING, Iterable, List, NamedTuple, Tuple

import click
import grpc
from ni_measurement_plugin_sdk_service.discovery._client import DiscoveryClient
import hightime
import ni_measurement_plugin_sdk_service as nims
import nidcpower
import nidcpower.session
import stubs.log_measurement_pb2_grpc
from stubs.log_measurement_pb2 import LogRequest,LogResponse
from _helpers import configure_logging, verbosity_option

_NIDCPOWER_WAIT_FOR_EVENT_TIMEOUT_ERROR_CODE = -1074116059
_NIDCPOWER_TIMEOUT_EXCEEDED_ERROR_CODE = -1074097933
_NIDCPOWER_TIMEOUT_ERROR_CODES = [
    _NIDCPOWER_WAIT_FOR_EVENT_TIMEOUT_ERROR_CODE,
    _NIDCPOWER_TIMEOUT_EXCEEDED_ERROR_CODE,
]
GRPC_LOGGER_SERVICE_INTERFACE_NAME = "ni.measurementlink.logger.v1.LogService"
GRPC_LOGGER_SERVICE_CLASS = "ni.measurementlink.logger.v1.LogService"

script_or_exe = sys.executable if getattr(sys, "frozen", False) else __file__
service_directory = pathlib.Path(script_or_exe).resolve().parent
measurement_service = nims.MeasurementService(
    service_config_path=service_directory / "NIDCPowerSourceDCVoltage.serviceconfig",
    version="0.1.0.0",
    ui_file_paths=[
        service_directory / "NIDCPowerSourceDCVoltage.measui",
        service_directory / "NIDCPowerSourceDCVoltageUI.vi",
    ],
)

# Initialize the discovery client
discovery_client = DiscoveryClient()

# Resolve the service location using the discovery client
logger_service_location = discovery_client.resolve_service(
provided_interface=GRPC_LOGGER_SERVICE_INTERFACE_NAME,
logger_service_class=GRPC_LOGGER_SERVICE_CLASS)

# Create a gRPC channel to the resolved service location
logger_service_channel = grpc.insecure_channel(logger_service_location.insecure_address)

# Create a gRPC stub for the Logger service
stub = stubs.log_measurement_pb2_grpc.LogMeasurementStub(channel = logger_service_channel)

if TYPE_CHECKING:
    # The nidcpower Measurement named tuple doesn't support type annotations:
    # https://github.com/ni/nimi-python/issues/1885
    class _Measurement(NamedTuple):
        voltage: float
        current: float
        in_compliance: bool
        channel: str


@measurement_service.register_measurement
@measurement_service.configuration(
    "pin_names",
    nims.DataType.IOResourceArray1D,
    ["Pin1"],
    instrument_type=nims.session_management.INSTRUMENT_TYPE_NI_DCPOWER,
)
@measurement_service.configuration("voltage_level", nims.DataType.Double, 6.0)
@measurement_service.configuration("voltage_level_range", nims.DataType.Double, 6.0)
@measurement_service.configuration("current_limit", nims.DataType.Double, 0.01)
@measurement_service.configuration("current_limit_range", nims.DataType.Double, 0.01)
@measurement_service.configuration("source_delay", nims.DataType.Double, 0.0)
@measurement_service.output("measurement_sites", nims.DataType.Int32Array1D)
@measurement_service.output("measurement_pin_names", nims.DataType.StringArray1D)
@measurement_service.output("voltage_measurements", nims.DataType.DoubleArray1D)
@measurement_service.output("current_measurements", nims.DataType.DoubleArray1D)
@measurement_service.output("in_compliance", nims.DataType.BooleanArray1D)
def measure(
    pin_names: Iterable[str],
    voltage_level: float,
    voltage_level_range: float,
    current_limit: float,
    current_limit_range: float,
    source_delay: float,
) -> Tuple[List[int], List[str], List[float], List[float], List[bool]]:
    """Source and measure a DC voltage with an NI SMU."""

    cancellation_event = threading.Event()
    measurement_service.context.add_cancel_callback(cancellation_event.set)

    with measurement_service.context.reserve_sessions(pin_names) as reservation:
        with reservation.initialize_nidcpower_sessions() as session_infos:
            # Configure the same channel settings for all of the sessions corresponding
            # to the selected pins and sites.
            for session_info in session_infos:
                channels = session_info.session.channels[session_info.channel_list]
                channels.source_mode = nidcpower.SourceMode.SINGLE_POINT
                channels.output_function = nidcpower.OutputFunction.DC_VOLTAGE
                channels.current_limit = current_limit
                channels.voltage_level_range = voltage_level_range
                channels.current_limit_range = current_limit_range
                channels.source_delay = hightime.timedelta(seconds=source_delay)
                channels.voltage_level = voltage_level

            with ExitStack() as stack:
                # Initiate the channels to start sourcing the outputs. initiate()
                # returns a context manager that aborts the measurement when the
                # function returns or raises an exception.
                for session_info in session_infos:
                    channels = session_info.session.channels[session_info.channel_list]
                    stack.enter_context(channels.initiate())

                # Wait for the outputs to settle.
                for session_info in session_infos:
                    channels = session_info.session.channels[session_info.channel_list]
                    timeout = source_delay + 10.0
                    _wait_for_event(
                        channels, cancellation_event, nidcpower.enums.Event.SOURCE_COMPLETE, timeout
                    )

                measurements: List[_Measurement] = []
                measured_sites, measured_pins = [], []
                for session_info in session_infos:
                    channels = session_info.session.channels[session_info.channel_list]
                    # Measure the voltage and current for each output of the session.
                    session_measurements: List[_Measurement] = channels.measure_multiple()

                    for measurement, channel_mapping in zip(
                        session_measurements, session_info.channel_mappings
                    ):
                        measured_sites.append(channel_mapping.site)
                        measured_pins.append(channel_mapping.pin_or_relay_name)
                        # Determine whether the outputs are in compliance.
                        in_compliance = session_info.session.channels[
                            channel_mapping.channel
                        ].query_in_compliance()
                        measurements.append(measurement._replace(in_compliance=in_compliance))

                # Reset the channels to a known state
                for session_info in session_infos:
                    session_info.session.channels[session_info.channel_list].reset()

    # Extract measurement data
    voltage=[measurement.voltage for measurement in measurements]
    current=[measurement.current for measurement in measurements]
    in_compliance=[measurement.in_compliance for measurement in measurements]

    # Create and send a LogMeasurement request
    stub.Log(LogRequest(
        measured_sites=measured_sites,
        measured_pins=measured_pins,
        voltage=voltage,
        current=current,
        in_compliance=in_compliance,))

    return (
        measured_sites,
        measured_pins,
        [measurement.voltage for measurement in measurements],
        [measurement.current for measurement in measurements],
        [measurement.in_compliance for measurement in measurements],
    )


def _wait_for_event(
    channels: nidcpower.session._SessionBase,
    cancellation_event: threading.Event,
    event_id: nidcpower.enums.Event,
    timeout: float,
) -> None:
    """Wait for a NI-DCPower event or until error/cancellation occurs."""
    grpc_deadline = time.time() + measurement_service.context.time_remaining
    user_deadline = time.time() + timeout

    while True:
        if time.time() > user_deadline:
            raise TimeoutError("User timeout expired.")
        if time.time() > grpc_deadline:
            measurement_service.context.abort(
                grpc.StatusCode.DEADLINE_EXCEEDED, "Deadline exceeded."
            )
        if cancellation_event.is_set():
            measurement_service.context.abort(
                grpc.StatusCode.CANCELLED, "Client requested cancellation."
            )

        # Wait for the NI-DCPower event. If this takes more than 100 ms, check
        # whether the measurement was canceled and try again. NI-DCPower does
        # not support canceling a call to wait_for_event().
        try:
            channels.wait_for_event(event_id, timeout=100e-3)
            break
        except nidcpower.errors.DriverError as e:
            if e.code in _NIDCPOWER_TIMEOUT_ERROR_CODES:
                pass
            raise


@click.command
@verbosity_option
def main(verbosity: int) -> None:
    """Source and measure a DC voltage with an NI SMU."""
    configure_logging(verbosity)

    with measurement_service.host_service():
        input("Press enter to close the measurement service.\n")


if __name__ == "__main__":
    main()
