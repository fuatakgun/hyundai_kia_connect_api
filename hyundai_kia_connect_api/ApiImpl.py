"""ApiImpl.py"""

# pylint:disable=unnecessary-pass,missing-class-docstring,invalid-name,missing-function-docstring,wildcard-import,unused-wildcard-import,unused-argument,missing-timeout,logging-fstring-interpolation

import datetime as dt
import logging
from dataclasses import dataclass

import requests
from requests.exceptions import JSONDecodeError
from .Token import Token
from .Vehicle import Vehicle
from .const import (
    WINDOW_STATE,
    CHARGE_PORT_ACTION,
    OrderStatus,
    DOMAIN,
    VALET_MODE_ACTION,
    VEHICLE_LOCK_ACTION,
)
from .utils import get_child_value

_LOGGER = logging.getLogger(__name__)


@dataclass
class ClimateRequestOptions:
    set_temp: float = None
    duration: int = None
    defrost: bool = None
    climate: bool = None
    heating: int = None
    front_left_seat: int = None
    front_right_seat: int = None
    rear_left_seat: int = None
    rear_right_seat: int = None


@dataclass
class WindowRequestOptions:
    back_left: WINDOW_STATE = None
    back_right: WINDOW_STATE = None
    front_left: WINDOW_STATE = None
    front_right: WINDOW_STATE = None


@dataclass
class ScheduleChargingClimateRequestOptions:
    @dataclass
    class DepartureOptions:
        enabled: bool = None
        days: list[int] = None  # Sun=0, Mon=1, ..., Sat=6
        time: dt.time = None

    first_departure: DepartureOptions = None
    second_departure: DepartureOptions = None
    charging_enabled: bool = None
    off_peak_start_time: dt.time = None
    off_peak_end_time: dt.time = None
    off_peak_charge_only_enabled: bool = None
    climate_enabled: bool = None
    temperature: float = None
    temperature_unit: int = None
    defrost: bool = None


class ApiImpl:
    data_timezone = dt.timezone.utc
    temperature_range = None

    def __init__(self) -> None:
        """Initialize."""

    def login(self, username: str, password: str) -> Token:
        """Login into cloud endpoints and return Token"""
        raise NotImplementedError("required")

    def get_vehicles(self, token: Token) -> list[Vehicle]:
        """Return all Vehicle instances for a given Token"""
        raise NotImplementedError("required")

    def refresh_vehicles(self, token: Token, vehicles: list[Vehicle]) -> None:
        """Refresh the vehicle data provided in get_vehicles.
        Required for Kia USA as key is session specific"""
        return vehicles

    def update_vehicle_with_cached_state(self, token: Token, vehicle: Vehicle) -> None:
        """Get cached vehicle data and update Vehicle instance with it"""
        raise NotImplementedError("required")

    def check_action_status(
        self,
        token: Token,
        vehicle: Vehicle,
        action_id: str,
        synchronous: bool = False,
        timeout: int = 0,
    ) -> OrderStatus | None:
        """
        feature only available for some regions.
        """
        return None

    def force_refresh_vehicle_state(self, token: Token, vehicle: Vehicle) -> None:
        """Triggers the system to contact the car and get fresh data"""
        raise NotImplementedError("required")

    @staticmethod
    def update_geocoded_location(
        token: Token, vehicle: Vehicle, use_email: bool
    ) -> None:
        """Uses OpenStreetMap to initialize vehicle.geocode."""
        if vehicle.location_latitude and vehicle.location_longitude:
            email_parameter = ""
            if use_email is True:
                email_parameter = "&email=" + token.username

            url = (
                "https://nominatim.openstreetmap.org/reverse?lat="
                + str(vehicle.location_latitude)
                + "&lon="
                + str(vehicle.location_longitude)
                + "&format=json&addressdetails=1&zoom=18"
                + email_parameter
            )
            _LOGGER.debug(
                f"{DOMAIN} - Running update geocode location with value: {url}"
            )
            response = requests.get(url)
            _LOGGER.debug(f"{DOMAIN} - geocode location raw response: {response}")
            try:
                response = response.json()
            except JSONDecodeError:
                _LOGGER.debug(f"{DOMAIN} - failed to decode json for geocode location")
                vehicle.geocode = None
            else:
                _LOGGER.debug(f"{DOMAIN} - geocode location json response: {response}")
                vehicle.geocode = (
                    get_child_value(response, "display_name"),
                    get_child_value(response, "address"),
                )

    def lock_action(
        self, token: Token, vehicle: Vehicle, action: VEHICLE_LOCK_ACTION
    ) -> str:
        """Lock or unlocks a vehicle.  Returns the tracking ID"""
        raise NotImplementedError("required")

    def start_climate(
        self, token: Token, vehicle: Vehicle, options: ClimateRequestOptions
    ) -> str:
        """Starts climate or remote start.  Returns the tracking ID"""
        raise NotImplementedError("required")

    def stop_climate(self, token: Token, vehicle: Vehicle) -> str:
        """Stops climate or remote start.  Returns the tracking ID"""
        raise NotImplementedError("required")

    def start_charge(self, token: Token, vehicle: Vehicle) -> str:
        """Starts charge. Returns the tracking ID"""
        raise NotImplementedError("required")

    def stop_charge(self, token: Token, vehicle: Vehicle) -> str:
        """Stops charge. Returns the tracking ID"""
        raise NotImplementedError("required")

    def set_charge_limits(
        self, token: Token, vehicle: Vehicle, ac: int, dc: int
    ) -> str:
        """Sets charge limits. Returns the tracking ID"""
        raise NotImplementedError("required")

    def set_charging_current(
        self, token: Token, vehicle: Vehicle, level: int
    ) -> str | None:
        """
        feature only available for some regions.
        Sets charge current level (1=100%, 2=90%, 3=60%). Returns the tracking
        ID
        """
        return None

    def set_windows_state(
        self, token: Token, vehicle: Vehicle, options: WindowRequestOptions
    ) -> str | None:
        """
        feature only available for some regions.
        Opens or closes a particular window. Returns the tracking ID.
        """
        return None

    def charge_port_action(
        self, token: Token, vehicle: Vehicle, action: CHARGE_PORT_ACTION
    ) -> str | None:
        """
        feature only available for some regions.
        Opens or closes the charging port of the car. Returns the tracking ID
        """
        return None

    def update_month_trip_info(
        self, token: Token, vehicle: Vehicle, yyyymm_string: str
    ) -> None:
        """
        feature only available for some regions.
        Updates the vehicle.month_trip_info for the specified month.

        Default this information is None:

        month_trip_info: MonthTripInfo = None
        """
        return None

    def update_day_trip_info(
        self, token: Token, vehicle: Vehicle, yyyymmdd_string: str
    ) -> None:
        """
        feature only available for some regions.
        Updates the vehicle.day_trip_info information for the specified day.

        Default this information is None:

        day_trip_info: DayTripInfo = None
        """
        return None

    def schedule_charging_and_climate(
        self,
        token: Token,
        vehicle: Vehicle,
        options: ScheduleChargingClimateRequestOptions,
    ) -> str | None:
        """
        feature only available for some regions.
        Schedule charging and climate control. Returns the tracking ID
        """
        return None

    def start_hazard_lights(self, token: Token, vehicle: Vehicle) -> str | None:
        """
        feature only available for some regions.
        Turns on the hazard lights for 30 seconds
        """
        return None

    def start_hazard_lights_and_horn(
        self, token: Token, vehicle: Vehicle
    ) -> str | None:
        """
        feature only available for some regions.
        Turns on the hazard lights and horn for 30 seconds
        """
        return None

    def valet_mode_action(
        self, token: Token, vehicle: Vehicle, action: VALET_MODE_ACTION
    ) -> str:
        """
        feature only available for some regions.
        Activate or Deactivate valet mode. Returns the tracking ID
        """
        return None
