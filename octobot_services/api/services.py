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
from octobot_services.managers.service_manager import stop_services as manager_stop_services
from octobot_services.services.service_factory import ServiceFactory
from octobot_services.util.service_util import get_available_services as util_get_available_services


def get_available_services():
    return util_get_available_services()


def create_service_factory(config):
    return ServiceFactory(config)


def stop_services():
    manager_stop_services()
