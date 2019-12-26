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
from octobot_services.managers.dispatcher_manager import DispatcherManager
from octobot_services.dispatchers.dispatcher_factory import DispatcherFactory


def create_dispatcher_factory(config, main_async_loop) -> DispatcherFactory:
    return DispatcherFactory(config, main_async_loop)


def start_dispatchers(dispatchers) -> None:
    DispatcherManager.start_dispatchers(dispatchers)


def stop_dispatchers(dispatchers) -> None:
    DispatcherManager.stop_dispatchers(dispatchers)
