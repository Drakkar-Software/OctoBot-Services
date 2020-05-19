#  Drakkar-Software OctoBot-Services
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
from octobot_services.interfaces.abstract_interface import AbstractInterface
from octobot_services.interfaces.interface_factory import InterfaceFactory
from octobot_services.managers.interface_manager import start_interfaces as manager_start_interfaces, \
    stop_interfaces as manager_stop_interfaces


def initialize_global_project_data(bot_api: object, project_name: str, project_version: str) -> None:
    AbstractInterface.initialize_global_project_data(bot_api, project_name, project_version)


def create_interface_factory(config: dict) -> InterfaceFactory:
    return InterfaceFactory(config)


def is_enabled(interface_class: AbstractInterface) -> bool:
    return interface_class.enabled


def is_enabled_in_backtesting(interface_class) -> bool:
    return all(service.BACKTESTING_ENABLED for service in interface_class.REQUIRED_SERVICES)


def is_interface_relevant(config, interface_class, backtesting_enabled):
    return is_enabled(interface_class) and \
           all(service.get_is_enabled(config) for service in interface_class.REQUIRED_SERVICES) and \
           (not backtesting_enabled or (backtesting_enabled and is_enabled_in_backtesting(interface_class)))


def disable_interfaces(interface_identifier: str) -> int:
    disabled_interfaces = 0
    normalized_identifier = interface_identifier.lower()
    for interface_class in InterfaceFactory.get_available_interfaces():
        if normalized_identifier in interface_class.__name__.lower():
            interface_class.enabled = False
            disabled_interfaces += 1
    return disabled_interfaces


# Return the list of started interfaces
async def start_interfaces(interfaces: list) -> list:
    return await manager_start_interfaces(interfaces)


async def stop_interfaces(interfaces: list) -> None:
    await manager_stop_interfaces(interfaces)
