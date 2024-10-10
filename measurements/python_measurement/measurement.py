"""Source and measure a DC voltage with an NI SMU."""

from __future__ import annotations

import pathlib
import sys
import threading
import time
from typing import TYPE_CHECKING, NamedTuple, Tuple

import click
import grpc
import hightime
import ni_measurement_plugin_sdk_service as nims
import nidcpower
import nidcpower.session as session
from measurements.python_measurement.logger_service_client import LoggerServiceClient
from _helpers import configure_logging, verbosity_option

_NIDCPOWER_WAIT_FOR_EVENT_TIMEOUT_ERROR_CODE = -1074116059
_NIDCPOWER_TIMEOUT_EXCEEDED_ERROR_CODE = -1074097933
_NIDCPOWER_TIMEOUT_ERROR_CODES = [
    _NIDCPOWER_WAIT_FOR_EVENT_TIMEOUT_ERROR_CODE,
    _NIDCPOWER_TIMEOUT_EXCEEDED_ERROR_CODE,
]

script_or_exe = sys.executable if getattr(sys, "frozen", False) else __file__
service_directory = pathlib.Path(script_or_exe).resolve().parent
measurement_service = nims.MeasurementService(
    service_config_path=service_directory / "NIDCPowerSourceDCVoltage.serviceconfig",
    version="0.1.0.0",
    ui_file_paths=[service_directory / "NIDCPowerSourceDCVoltage.measui",],
)

logger_service_client = LoggerServiceClient()

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
    "pin_name",
    nims.DataType.IOResource,
    "Pin1",
    instrument_type=nims.session_management.INSTRUMENT_TYPE_NI_DCPOWER,
)
@measurement_service.configuration("voltage_level", nims.DataType.Double, 6.0)
@measurement_service.configuration("voltage_level_range", nims.DataType.Double, 6.0)
@measurement_service.configuration("current_limit", nims.DataType.Double, 0.01)
@measurement_service.configuration("current_limit_range", nims.DataType.Double, 0.01)
@measurement_service.configuration("source_delay", nims.DataType.Double, 0.0)
@measurement_service.output("voltage_measurement", nims.DataType.Double)
@measurement_service.output("current_measurement", nims.DataType.Double)
def measure(
    pin_name: str,
    voltage_level: float,
    voltage_level_range: float,
    current_limit: float,
    current_limit_range: float,
    source_delay: float,
) -> Tuple[float, float]:
    """Source and measure a DC voltage with an NI SMU."""
    cancellation_event = threading.Event()
    measurement_service.context.add_cancel_callback(cancellation_event.set)

    with measurement_service.context.reserve_session(pin_name) as reservation:
        with reservation.initialize_nidcpower_session() as session_info:
            channels = session_info.session.channels[session_info.channel_list]
            channels.source_mode = nidcpower.SourceMode.SINGLE_POINT
            channels.output_function = nidcpower.OutputFunction.DC_VOLTAGE
            channels.current_limit = current_limit
            channels.voltage_level_range = voltage_level_range
            channels.current_limit_range = current_limit_range
            channels.source_delay = hightime.timedelta(seconds=source_delay)
            channels.voltage_level = voltage_level

            with channels.initiate():
                # Wait for the outputs to settle.
                timeout = source_delay + 10.0
                _wait_for_event(
                    channels,
                    cancellation_event,
                    nidcpower.Event.SOURCE_COMPLETE,
                    timeout,
                )

                channel_mappings = list(session_info.channel_mappings)
                measured_site = channel_mappings[0].site
                measured_pin = channel_mappings[0].pin_or_relay_name
                in_compliance = session_info.session.channels[
                    channel_mappings[0].channel
                ].query_in_compliance()
                measurement: _Measurement = channels.measure_multiple()[0]
            channels.reset()

    logger_service_client._log_measurement(
        measured_sites=[measured_site],
        measured_pins=[measured_pin],
        voltage_measurements=[measurement.voltage],
        current_measurements=[measurement.current],
        in_compliance=[in_compliance]
    )

    return (
        measurement.voltage,
        measurement.current,
    )


def _wait_for_event(
    channels: session._SessionBase,
    cancellation_event: threading.Event,
    event_id: nidcpower.Event,
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
